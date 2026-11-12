"""Headless controller tests. These do not replace desktop layout inspection."""
import ast
import math
import operator
from pathlib import Path
import unittest
from unittest.mock import MagicMock
from stage3_gui import Stage3App
from data import CLASSROOMS, ROUTERS


class Value:
    def __init__(self,value):self.value=value
    def get(self):return self.value
    def set(self,value):self.value=value


class ControllerTests(unittest.TestCase):
    def app(self):
        a=Stage3App.__new__(Stage3App)
        a.weight_name=Value('Balanced 70/30');a.mode=Value('Guided blocks')
        a.process=None;a.result_queue=None;a.job=None;a.poll_token=0;a.revision=0
        a.tests_passed=True;a.block_passed={k:True for k in 'ABC'}
        a.block_labels={k:MagicMock() for k in 'ABC'}
        a.history=[('70/30','old result')];a.selected=['B','D','G']
        for name in ['test_label','manual_feedback','algorithm_feedback','manual_button',
                     'algorithm_button','status','debug_feedback','plan_label','records','draw_map']:
            setattr(a,name,MagicMock())
        return a

    def test_weight_change_invalidates_certification_not_history(self):
        a=self.app();a.weight_name.set('Coverage priority 100/0');a.change_weight()
        self.assertEqual(a.history,[('70/30','old result')])
        self.assertEqual(a.weight,1);self.assertFalse(any(a.block_passed.values()))
        a.manual_feedback.config.assert_called_with(text='Manual plan: New scenario; not checked')
        self.assertIn('100%/0%',a.plan_label.config.call_args.kwargs['text'])

    def test_expression_edit_invalidates_all_blocks(self):
        a=self.app();a.code_changed('basic')
        self.assertFalse(a.tests_passed);self.assertFalse(any(a.block_passed.values()))
        a.algorithm_button.config.assert_called_with(state='disabled')

    def test_one_block_edit_does_not_erase_other_blocks(self):
        a=self.app();a.code_changed('A')
        self.assertEqual(a.block_passed,dict(A=False,B=True,C=True))
        self.assertTrue(a.tests_passed)

    def test_unfinished_guided_algorithm_cannot_run(self):
        a=self.app();a.block_passed['B']=False;a.start_job=MagicMock()
        a.run_student_algorithm();a.start_job.assert_not_called()

    def test_manual_check_uses_active_weight(self):
        a=self.app();a.check_manual_plan()
        self.assertEqual(a.history[-1][-1],'YES')
        a.weight_name.set('Coverage priority 100/0');a.check_manual_plan()
        self.assertEqual(a.history[-1][-1],'NO')
        self.assertEqual(a.history[-1][0],'100%/0%')

    def test_cancel_job_stops_worker(self):
        a=self.app();p=MagicMock();p.is_alive.return_value=True;q=MagicMock()
        a.process=p;a.result_queue=q;a.cancel_job()
        p.terminate.assert_called_once();q.close.assert_called_once()
        self.assertIsNone(a.process);self.assertEqual(a.poll_token,1)

    def test_old_poll_cannot_consume_new_job(self):
        a=self.app();a.poll_token=3;a.process=MagicMock();a.result_queue=MagicMock()
        a.poll_job(2);a.result_queue.get_nowait.assert_not_called()


class BasicExpressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Extract only pure evaluator functions; basic GUI launches Tk at import.
        source=(Path(__file__).resolve().parents[1]/'student_version'/'gui.py').read_text()
        tree=ast.parse(source)
        names={'safe_evaluate','calculate_student_distance','calculate_student_condition',
               'verify_student_pair','expected_distance','student_calculate'}
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names
               or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in
                   {'BINARY_OPS','COMPARE_OPS','ALLOWED_NAMES'} for t in n.targets)]
        cls.env=dict(ast=ast,math=math,operator=operator,CLASSROOMS=CLASSROOMS,ROUTERS=ROUTERS,COVERAGE_RADIUS=3)
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<basic-functions>','exec'),cls.env)

    def setUp(self):
        self.env['get_expressions']=lambda:('(cx-rx)**2 + (cy-ry)**2','distance_squared <= COVERAGE_RADIUS**2')

    def test_all_84_pairs_and_full_coverage(self):
        for c in CLASSROOMS.values():
            for r in ROUTERS.values():self.env['verify_student_pair'](c,r)
        self.assertEqual(self.env['student_calculate'](['B','D','E'])['count'],12)

    def test_boundary_covered(self):
        self.assertTrue(self.env['verify_student_pair']((3,8),(6,8)))

    def test_distance_task_cannot_be_bypassed(self):
        self.env['get_expressions']=lambda:('0','distance_squared <= COVERAGE_RADIUS**2')
        with self.assertRaises(ValueError):self.env['verify_student_pair']((3,8),(6,8))


if __name__=='__main__':unittest.main()
