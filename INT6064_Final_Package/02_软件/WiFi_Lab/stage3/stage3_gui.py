"""Revised teaching interface; original Tkinter map and evaluator retained."""
import csv
import io
import multiprocessing as mp
import queue
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from data import CLASSROOMS, ROUTERS, ROUTER_LIMIT, INSTALLATION_COSTS, ROUTER_COVERAGE
from stage3_core import WEIGHT_PRESETS, evaluate_plan, verify_optimal, valid_plan
from coding_engine import (BLOCK_HINTS, DEBUG_STARTERS, assemble_algorithm,
                           check_expressions, exercise_worker, validate_student_algorithm)
from map_view import MapView


class Stage3App(MapView):
    def __init__(self, root):
        self.root=root
        root.title('Campus Wi-Fi Lab | Evaluate, Code and Explain')
        root.geometry('1320x900');root.minsize(1100,780)
        self.selected=[];self.tests_passed=False;self.block_passed={k:False for k in 'ABC'}
        self.process=None;self.result_queue=None;self.job=None;self.history=[];self.evidence=[]
        self.revision=0;self.poll_token=0
        self.weight_name=tk.StringVar(value='Balanced 70/30')
        self.mode=tk.StringVar(value='Guided blocks')
        self.debug_kind=tk.StringVar(value='Overlap')
        self.build_gui();self.refresh_map()
        root.protocol('WM_DELETE_WINDOW',self.close)

    @property
    def weight(self):
        return WEIGHT_PRESETS[self.weight_name.get()]

    def build_gui(self):
        style=ttk.Style()
        if 'clam' in style.theme_names():style.theme_use('clam')
        style.configure('Title.TLabel',font=('Arial',18,'bold'))
        style.configure('Heading.TLabel',font=('Arial',11,'bold'))
        style.configure('TNotebook.Tab',padding=(12,7))
        outer=ttk.Frame(self.root,padding=12);outer.pack(fill='both',expand=True)
        ttk.Label(outer,text='Campus Wi-Fi Lab',style='Title.TLabel').pack(anchor='w')
        ttk.Label(outer,text='Choose exactly 3 installation points. Predict → test → compare → explain.').pack(anchor='w',pady=(3,8))
        bar=ttk.Frame(outer);bar.pack(fill='x',pady=(0,8))
        ttk.Label(bar,text='Scoring scenario:').pack(side='left')
        self.weights=ttk.Combobox(bar,textvariable=self.weight_name,values=list(WEIGHT_PRESETS),state='readonly',width=26)
        self.weights.pack(side='left',padx=8);self.weights.bind('<<ComboboxSelected>>',self.change_weight)
        ttk.Label(bar,text='Weights change the objective, not the map or costs.').pack(side='left')
        panes=ttk.PanedWindow(outer,orient='horizontal');panes.pack(fill='both',expand=True)
        left=ttk.Frame(panes);right=ttk.Frame(panes);panes.add(left,weight=0);panes.add(right,weight=1)
        self.canvas=tk.Canvas(left,width=460,height=460,bg='white',highlightthickness=0)
        self.canvas.pack()
        self.plan_label=ttk.Label(left,justify='left',wraplength=500,font=('Arial',10))
        self.plan_label.pack(anchor='w',pady=6)
        self.manual_feedback=ttk.Label(left,text='Manual plan: Not checked',style='Heading.TLabel')
        self.manual_feedback.pack(anchor='w',pady=4)
        controls=ttk.Frame(left);controls.pack(fill='x')
        self.manual_button=ttk.Button(controls,text='Check & record manual plan',command=self.check_manual_plan,state='disabled')
        self.manual_button.pack(side='left',padx=(0,5))
        ttk.Button(controls,text='Clear selection',command=self.clear_selection).pack(side='left')
        ttk.Label(left,text='Circles = classroom detection points; squares = installation points.\nCoverage uses distance only. Cost is installation cost, not router capacity.',wraplength=495).pack(anchor='w',pady=10)
        self.tabs=ttk.Notebook(right);self.tabs.pack(fill='both',expand=True)
        self.basic_tab=ttk.Frame(self.tabs,padding=10);self.algorithm_tab=ttk.Frame(self.tabs,padding=10)
        self.debug_tab=ttk.Frame(self.tabs,padding=10);self.history_tab=ttk.Frame(self.tabs,padding=10)
        for frame,title in [(self.basic_tab,'1  Expressions'),(self.algorithm_tab,'2  Algorithm'),
                            (self.debug_tab,'3  Debug'),(self.history_tab,'4  Evidence')]:
            self.tabs.add(frame,text=title)
        self.build_basic();self.build_algorithm();self.build_debug();self.build_history()
        self.status=tk.StringVar(value='Start with TODO 3–5. Reference optimal plans remain hidden.')
        ttk.Label(outer,textvariable=self.status,wraplength=1200).pack(anchor='w',pady=(8,0))

    def text_editor(self,parent,height,text='',callback=None):
        box=ttk.Frame(parent);box.pack(fill='both',expand=True,pady=4)
        widget=tk.Text(box,height=height,font=('Courier',10),wrap='none',undo=True)
        vs=ttk.Scrollbar(box,orient='vertical',command=widget.yview)
        hs=ttk.Scrollbar(box,orient='horizontal',command=widget.xview)
        widget.configure(yscrollcommand=vs.set,xscrollcommand=hs.set)
        widget.grid(row=0,column=0,sticky='nsew');vs.grid(row=0,column=1,sticky='ns');hs.grid(row=1,column=0,sticky='ew')
        box.rowconfigure(0,weight=1);box.columnconfigure(0,weight=1)
        widget.insert('1.0',text);widget.edit_modified(False)
        if callback:
            def changed(event):
                if widget.edit_modified():
                    widget.edit_modified(False);callback()
            widget.bind('<<Modified>>',changed)
        return widget

    @staticmethod
    def source(editor):return editor.get('1.0','end-1c')

    def expressions(self):return {k:self.source(e).strip() for k,e in self.editors.items()}

    def build_basic(self):
        p=self.basic_tab
        ttk.Label(p,text='TODO 3–5 | Write and test one expression at a time',style='Heading.TLabel').pack(anchor='w')
        self.editors={}
        specs=[(3,'Installation cost','costs, selected  |  selected contains exactly 3 IDs'),
               (4,'Weighted score','coverage_rate, cost_score, coverage_weight, cost_weight'),
               (5,'Best-plan comparison','score, best_score  |  return True only when strictly better')]
        for number,label,hint in specs:
            f=ttk.LabelFrame(p,text=f'TODO {number}  {label}',padding=6);f.pack(fill='x',pady=5)
            ttk.Label(f,text=hint,wraplength=620).pack(anchor='w')
            self.editors[number]=self.text_editor(f,2,callback=lambda:self.code_changed('basic'))
        ttk.Button(p,text='Run 49 expression tests',command=self.run_student_tests).pack(anchor='w',pady=5)
        self.test_label=ttk.Label(p,text='Tests: Not completed');self.test_label.pack(anchor='w')
        ttk.Label(p,text='Inputs use fractions from 0 to 1. Cost score = 1 − total cost / MAX_COST.\nMAX_COST is a normalization reference (1100), not a spending limit.',wraplength=620).pack(anchor='w',pady=8)
        self.basic_log=tk.Text(p,height=8,wrap='word',font=('Courier',10));self.basic_log.pack(fill='both',expand=True)
        ttk.Label(p,text='Your expressions become student_cost, student_score and student_better in TODO 6.',wraplength=620).pack(anchor='w',pady=5)

    def build_algorithm(self):
        p=self.algorithm_tab
        ttk.Label(p,text='TODO 6 | Build a search over all 35 combinations',style='Heading.TLabel').pack(anchor='w')
        row=ttk.Frame(p);row.pack(fill='x',pady=5)
        for value in ['Guided blocks','Free coding']:
            ttk.Radiobutton(row,text=value,value=value,variable=self.mode,command=self.switch_mode).pack(side='left',padx=4)
        self.guided=ttk.Frame(p);self.free=ttk.Frame(p)
        self.guided.pack(fill='both',expand=True)
        ttk.Label(self.guided,text='Provided: best_plan=None, best_score=-1 and the combination loop.\nComplete A → B → C; each block is tested independently.',wraplength=620).pack(anchor='w')
        blocks=ttk.Notebook(self.guided);blocks.pack(fill='both',expand=True,pady=6)
        self.blocks={};self.block_labels={}
        for key,title in [('A','A  Merge coverage'),('B','B  Evaluate a plan'),('C','C  Update the best')]:
            page=ttk.Frame(blocks,padding=6);blocks.add(page,text=title)
            self.blocks[key]=self.text_editor(page,14,BLOCK_HINTS[key],lambda k=key:self.code_changed(k))
            ttk.Button(page,text=f'Test block {key}',command=lambda k=key:self.run_block(k)).pack(anchor='w',pady=5)
            self.block_labels[key]=ttk.Label(page,text=f'Block {key}: Not tested',wraplength=600)
            self.block_labels[key].pack(anchor='w')
        ttk.Button(self.guided,text='Preview assembled algorithm',command=self.preview).pack(anchor='w',pady=4)
        ttk.Label(self.free,text='Function body only; no def or import. Use the same variables and helpers.\nFree coding keeps its own draft and does not require guided-block tests.',wraplength=620).pack(anchor='w')
        self.algorithm_editor=self.text_editor(self.free,20,callback=lambda:self.code_changed('free'))
        ttk.Label(p,text='Available: ROUTERS, ROUTER_COVERAGE, INSTALLATION_COSTS, CLASSROOMS,\nROUTER_LIMIT, MAX_COST, coverage_weight, cost_weight, combinations, set, len,\nsum, sorted, student_cost, student_score, student_better.',wraplength=640).pack(anchor='w',pady=4)
        self.algorithm_button=ttk.Button(p,text='Run & record my algorithm',command=self.run_student_algorithm,state='disabled')
        self.algorithm_button.pack(anchor='w',pady=5)
        self.algorithm_feedback=ttk.Label(p,text='Student algorithm: Not checked',wraplength=630)
        self.algorithm_feedback.pack(anchor='w')

    def build_debug(self):
        p=self.debug_tab
        ttk.Label(p,text='Debug a supplied mistake, then explain the repair',style='Heading.TLabel').pack(anchor='w')
        choice=ttk.Combobox(p,textvariable=self.debug_kind,values=list(DEBUG_STARTERS),state='readonly')
        choice.pack(anchor='w',pady=5);choice.bind('<<ComboboxSelected>>',self.load_debug)
        ttk.Label(p,text='Overlap: compute covered_count without double counting.\nComparison: update best_score and best_plan only when better.',wraplength=620).pack(anchor='w')
        ttk.Label(p,text='Prediction / 运行前预测').pack(anchor='w',pady=(8,0))
        self.prediction=self.text_editor(p,2)
        self.debug_editor=self.text_editor(p,9,DEBUG_STARTERS['Overlap'],lambda:self.code_changed('debug'))
        ttk.Button(p,text='Test this repair',command=self.run_debug).pack(anchor='w',pady=5)
        self.debug_feedback=ttk.Label(p,text='Run the original code first to capture a failure.',wraplength=620)
        self.debug_feedback.pack(anchor='w')
        ttk.Label(p,text='Reason for the repair / 修改原因').pack(anchor='w',pady=(8,0))
        self.reason=self.text_editor(p,3)
        ttk.Button(p,text='Save explanation to evidence',command=self.save_explanation).pack(anchor='w',pady=5)

    def build_history(self):
        p=self.history_tab
        ttk.Label(p,text='Compare outcomes under different objectives',style='Heading.TLabel').pack(anchor='w')
        ttk.Label(p,text='Do not rank different scenarios by their composite scores.\nCompare coverage, cost and which classrooms are left out.',wraplength=620).pack(anchor='w',pady=5)
        columns=('weight','method','plan','coverage','cost','score','uncovered','optimal')
        box=ttk.Frame(p);box.pack(fill='both',expand=True)
        self.records=ttk.Treeview(box,columns=columns,show='headings',height=8)
        for col,width in zip(columns,(85,85,85,90,70,80,150,70)):
            self.records.heading(col,text=col.title());self.records.column(col,width=width,minwidth=60,stretch=False)
        scroll=ttk.Scrollbar(box,orient='horizontal',command=self.records.xview)
        vertical=ttk.Scrollbar(box,orient='vertical',command=self.records.yview)
        self.records.configure(xscrollcommand=scroll.set,yscrollcommand=vertical.set)
        self.records.grid(row=0,column=0,sticky='nsew');scroll.grid(row=1,column=0,sticky='ew');vertical.grid(row=0,column=1,sticky='ns')
        box.rowconfigure(0,weight=1);box.columnconfigure(0,weight=1)
        row=ttk.Frame(p);row.pack(fill='x',pady=7)
        ttk.Button(row,text='Copy comparison table',command=self.copy_history).pack(side='left')
        ttk.Button(row,text='Export evidence TXT',command=self.export_evidence).pack(side='left',padx=6)
        ttk.Label(p,text='Recommendation / 推荐哪个方案及原因').pack(anchor='w')
        self.recommendation=self.text_editor(p,4)
        self.evidence_log=tk.Text(p,height=7,wrap='word',state='disabled',font=('Courier',9))
        self.evidence_log.pack(fill='both',expand=True,pady=6)

    def code_changed(self,kind):
        self.cancel_job();self.revision+=1
        if kind=='basic':
            self.tests_passed=False
            self.test_label.config(text='Tests: Expressions changed; test again.')
            for k in 'ABC':
                self.block_passed[k]=False;self.block_labels[k].config(text=f'Block {k}: Test again')
            self.manual_feedback.config(text='Manual plan: Not checked')
        elif kind in 'ABC':
            self.block_passed[kind]=False;self.block_labels[kind].config(text=f'Block {kind}: Code changed; test again')
        if kind=='debug':self.debug_feedback.config(text='Code changed; test the repair again.')
        self.algorithm_feedback.config(text='Student algorithm: Not checked')
        self.sync_buttons()

    def sync_buttons(self):
        state='normal' if self.tests_passed and self.process is None else 'disabled'
        self.manual_button.config(state=state);self.algorithm_button.config(state=state)

    def change_weight(self,event=None):
        self.cancel_job();self.revision+=1
        for k in 'ABC':
            self.block_passed[k]=False;self.block_labels[k].config(text=f'Block {k}: New scenario; test again')
        self.manual_feedback.config(text='Manual plan: New scenario; not checked')
        self.algorithm_feedback.config(text='Student algorithm: New scenario; rerun')
        self.refresh_map();self.sync_buttons()
        self.status.set('Scenario changed. Code retained; history retains its original weights. Rerun to verify.')

    def switch_mode(self):
        self.cancel_job();self.revision+=1
        self.guided.pack_forget();self.free.pack_forget()
        (self.guided if self.mode.get()=='Guided blocks' else self.free).pack(fill='both',expand=True,before=self.algorithm_button)
        self.algorithm_feedback.config(text='Student algorithm: Mode changed; rerun');self.sync_buttons()

    def refresh_map(self):
        self.draw_map()
        if not valid_plan(self.selected):
            self.plan_label.config(text=f"Selected: {', '.join(sorted(self.selected)) or 'None'} ({len(self.selected)}/3)\nSelect exactly 3 installation points.")
            return
        r=evaluate_plan(self.selected,self.weight)
        self.plan_label.config(text=(f"Plan: {' + '.join(r['routers'])}  |  Weights {self.weight:.0%}/{1-self.weight:.0%}\n"
            f"Coverage: {r['covered_count']}/{len(CLASSROOMS)} = {r['coverage_rate']:.2%}\n"
            f"Uncovered: {', '.join(r['uncovered']) or 'None'}\n"
            f"Cost: ${r['cost']}  |  Cost score: {r['cost_score']:.4f}\n"
            f"Score = {self.weight:.2f} × {r['coverage_rate']:.4f} + {1-self.weight:.2f} × {r['cost_score']:.4f}\n"
            f"Composite score: {r['score']:.4f}"))

    def on_router_click(self,event):
        for item in reversed(self.canvas.find_overlapping(event.x,event.y,event.x,event.y)):
            for tag in self.canvas.gettags(item):
                if tag.startswith('router_'):
                    rid=tag.split('_',1)[1]
                    if rid in self.selected:self.selected.remove(rid)
                    elif len(self.selected)<ROUTER_LIMIT:self.selected.append(rid)
                    else:self.status.set('Selection limit: remove one point before adding another.');return
                    self.cancel_job();self.manual_feedback.config(text='Manual plan: Not checked')
                    self.algorithm_feedback.config(text='Map selection changed; algorithm not checked for this plan')
                    self.refresh_map();self.sync_buttons();return

    def clear_selection(self):
        self.cancel_job();self.selected=[];self.refresh_map();self.sync_buttons()
        self.manual_feedback.config(text='Manual plan: Not checked')
        self.algorithm_feedback.config(text='Student algorithm: Not checked')

    def run_student_tests(self):
        self.cancel_job()
        passed,total,errors=check_expressions(self.expressions())
        self.tests_passed=passed==total
        self.test_label.config(text=f'Tests: {passed}/{total} PASS')
        self.basic_log.delete('1.0','end');self.basic_log.insert('end','\n'.join(errors[:6]) if errors else 'All passed. Continue to guided blocks A, B and C.')
        self.sync_buttons()

    def preview(self):
        win=tk.Toplevel(self.root);win.title('Assembled algorithm | your current blocks');win.geometry('760x620')
        editor=self.text_editor(win,28,assemble_algorithm({k:self.source(e) for k,e in self.blocks.items()}));editor.config(state='disabled')

    def start_job(self,kind,source):
        if not self.tests_passed:
            self.status.set('Complete TODO 3–5 tests first.');return
        self.cancel_job()
        try:validate_student_algorithm(source)
        except Exception as error:
            self.status.set(f'{kind}: {error}');return
        self.result_queue=mp.get_context('spawn').Queue()
        self.process=mp.get_context('spawn').Process(target=exercise_worker,
            args=(kind,source,self.weight,self.expressions(),self.result_queue),daemon=True)
        self.job=dict(kind=kind,source=source,weight=self.weight,revision=self.revision,
                      expressions=self.expressions(),started=time.monotonic(),prediction=self.source(self.prediction),reason=self.source(self.reason))
        self.process.start();self.sync_buttons();self.status.set(f'Running {kind}… (3 second limit)')
        token=self.poll_token
        self.root.after(60,lambda:self.poll_job(token))

    def run_block(self,key):self.start_job(key,self.source(self.blocks[key]))

    def run_student_algorithm(self):
        if self.mode.get()=='Guided blocks':
            if not all(self.block_passed.values()):
                self.status.set('Pass each block A, B and C before running the guided algorithm.');return
            source=assemble_algorithm({k:self.source(e) for k,e in self.blocks.items()})
        else:source=self.source(self.algorithm_editor)
        self.start_job('Algorithm',source)

    def run_debug(self):
        if not self.source(self.prediction).strip():
            self.status.set('Write a prediction before testing the debugging exercise.');return
        self.start_job(self.debug_kind.get(),self.source(self.debug_editor))

    def load_debug(self,event=None):
        self.cancel_job()
        self.debug_editor.delete('1.0','end');self.debug_editor.insert('1.0',DEBUG_STARTERS[self.debug_kind.get()])
        self.prediction.delete('1.0','end');self.reason.delete('1.0','end')
        self.debug_feedback.config(text='Original mistake loaded. Predict, run, repair, explain.')

    def poll_job(self,token):
        if token != self.poll_token or self.process is None:return
        try:status,result=self.result_queue.get_nowait()
        except queue.Empty:
            if time.monotonic()-self.job['started']>=3:
                kind=self.job['kind'];self.add_evidence(f'{kind}: TIMEOUT',self.job)
                self.cancel_job();self.status.set(f'{kind}: TIMEOUT after 3 seconds. Check loops.');self.sync_buttons();return
            if not self.process.is_alive() and time.monotonic()-self.job['started']>.8:
                self.add_evidence('Worker exited without a result',self.job)
                self.cancel_job();self.status.set('Worker exited without a result.');self.sync_buttons();return
            self.root.after(60,lambda:self.poll_job(token));return
        job=self.job
        self.cancel_job();self.sync_buttons()
        if job['revision']!=self.revision or job['weight']!=self.weight:return
        kind=job['kind']
        if status=='plan':
            self.selected=list(result);self.refresh_map();optimal=verify_optimal(result,self.weight)
            self.algorithm_feedback.config(text=f"Student algorithm: {'Optimal' if optimal else 'Not optimal'} (reference hidden)")
            self.manual_feedback.config(text='Manual plan: Not checked')
            self.record_plan('Algorithm');self.add_evidence('Algorithm returned '+str(result),job)
            self.status.set('Algorithm result is on the map and in Evidence. Explain its trade-offs.')
        elif status=='tests':
            passed=result['passed']==result['total'];summary=f"{kind}: {result['passed']}/{result['total']} PASS"
            if kind in 'ABC':
                self.block_passed[kind]=passed;self.block_labels[kind].config(text=summary)
            else:self.debug_feedback.config(text=summary)
            self.add_evidence(summary+'\n'+'\n'.join(result['errors']),job)
            self.status.set(summary+(' | '+result['errors'][0] if result['errors'] else ''))
        else:
            self.status.set(f'{kind}: {result}');self.add_evidence(f'{kind}: {result}',job)
            if kind=='Algorithm':self.algorithm_feedback.config(text=f'Code error: {result}')

    def cancel_job(self):
        self.poll_token+=1
        if self.process is not None:
            if self.process.is_alive():self.process.terminate()
            self.process.join(timeout=.3)
            self.process=None
        if self.result_queue is not None:
            self.result_queue.close();self.result_queue=None
        self.job=None

    def check_manual_plan(self):
        if not self.tests_passed:return
        if not valid_plan(self.selected):self.status.set('Select exactly 3 different installation points.');return
        optimal=verify_optimal(self.selected,self.weight)
        self.manual_feedback.config(text=f"Manual plan: {'Optimal' if optimal else 'Not optimal'} (reference hidden)")
        self.record_plan('Manual')

    def record_plan(self,method):
        result=evaluate_plan(self.selected,self.weight)
        row=(f'{self.weight:.0%}/{1-self.weight:.0%}',method,'+'.join(result['routers']),
             f"{result['covered_count']}/12 ({result['coverage_rate']:.1%})",result['cost'],
             f"{result['score']:.4f}",','.join(result['uncovered']) or 'None',
             'YES' if verify_optimal(self.selected,self.weight) else 'NO')
        if row in self.history:
            self.status.set('This outcome is already recorded for the current scenario.')
            return
        self.history.append(row);self.records.insert('','end',values=row)
        self.status.set('Outcome recorded in Evidence.')

    def add_evidence(self,summary,job=None):
        entry=f"[{datetime.now().strftime('%H:%M:%S')}] {summary}"
        if job:
            entry+=f"\nWeights: {job['weight']:.0%}/{1-job['weight']:.0%}\nCode:\n{job['source']}"
            entry+=f"\nTODO 3–5: {job['expressions']}"
            if job['kind'] in DEBUG_STARTERS:
                entry+=f"\nPrediction: {job['prediction']}\nReason: {job['reason']}"
        self.evidence.append(entry)
        self.evidence_log.config(state='normal');self.evidence_log.insert('end',entry+'\n\n');self.evidence_log.see('end');self.evidence_log.config(state='disabled')

    def save_explanation(self):
        if not self.source(self.reason).strip():self.status.set('Write the reason for your repair first.');return
        self.add_evidence(f"{self.debug_kind.get()} explanation: {self.source(self.reason)}")
        self.status.set('Explanation saved in Evidence; export it before closing the app.')

    def history_tsv(self):
        stream=io.StringIO();writer=csv.writer(stream,delimiter='\t')
        writer.writerow(['Weights','Method','Plan','Coverage','Cost','Score','Uncovered','Optimal'])
        writer.writerows(self.history);return stream.getvalue()

    def copy_history(self):
        self.root.clipboard_clear();self.root.clipboard_append(self.history_tsv())
        self.status.set('Comparison table copied. Scores from different weights are not directly comparable.')

    def export_evidence(self):
        path=filedialog.asksaveasfilename(defaultextension='.txt',initialfile='wifi_learning_evidence.txt',filetypes=[('Text','*.txt')])
        if not path:return
        try:
            with open(path,'w',encoding='utf-8') as f:
                f.write('Wi-Fi Lab learning evidence\n\n'+self.history_tsv()+'\nRecommendation:\n'+self.source(self.recommendation)+'\n\n'+'\n\n'.join(self.evidence))
        except OSError as error:messagebox.showerror('Export failed',str(error));return
        self.status.set('Evidence exported successfully.')

    def close(self):
        if self.history or self.evidence:
            if not messagebox.askyesno('Close lab','Session records are kept in memory. Export evidence before closing. Close now?'):return
        self.cancel_job();self.root.destroy()


def main():
    mp.freeze_support()
    root=tk.Tk();Stage3App(root);root.mainloop()


if __name__=='__main__':main()
