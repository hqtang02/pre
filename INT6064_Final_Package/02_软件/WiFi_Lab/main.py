"""Cross-platform launcher. Run python main.py or choose a stage by flag."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def launch(stage):
    path = ROOT / ('student_version/gui.py' if stage == 'basic' else 'stage3/stage3_gui.py')
    return subprocess.Popen([sys.executable, str(path)], cwd=path.parent)


def main():
    parser=argparse.ArgumentParser(description='Campus Wi-Fi Coding Lab')
    parser.add_argument('--basic',action='store_true')
    parser.add_argument('--advanced',action='store_true')
    args=parser.parse_args()
    if args.basic or args.advanced:
        return launch('basic' if args.basic else 'advanced').wait()
    import tkinter as tk
    from tkinter import ttk
    root=tk.Tk();root.title('Campus Wi-Fi Lab');root.geometry('500x240')
    box=ttk.Frame(root,padding=24);box.pack(fill='both',expand=True)
    ttk.Label(box,text='Campus Wi-Fi Coding Lab',font=('Arial',17,'bold')).pack(pady=8)
    ttk.Button(box,text='Basic lab · TODO 1–2',command=lambda:launch('basic')).pack(fill='x',pady=8)
    ttk.Button(box,text='Optimization lab · TODO 3–6',command=lambda:launch('advanced')).pack(fill='x',pady=8)
    ttk.Label(box,text='Teacher references are stored separately in teacher/.').pack(pady=8)
    root.mainloop()
    return 0


if __name__=='__main__':raise SystemExit(main())
