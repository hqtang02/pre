import importlib.util
import math
import multiprocessing as mp
from pathlib import Path
import queue
import unittest
from unittest.mock import patch
from itertools import combinations
from data import CLASSROOMS, ROUTERS, ROUTER_COVERAGE, INSTALLATION_COSTS
from stage3_core import evaluate_plan, find_best_plan, verify_optimal, valid_plan
from coding_engine import (assemble_algorithm, check_expressions, run_code,
                           exercise_worker, DEBUG_STARTERS, validate_student_algorithm)

ref_path=Path(__file__).resolve().parents[1]/'teacher'/'reference_answers.py'
spec=importlib.util.spec_from_file_location('reference_answers',ref_path)
ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)


class RevisionTests(unittest.TestCase):
    def test_all_49_expressions(self):
        self.assertEqual(check_expressions(ref.EXPRESSIONS),(49,49,[]))

    def test_cost_expression_cannot_be_constant(self):
        expressions=dict(ref.EXPRESSIONS);expressions[3]='750'
        self.assertLess(check_expressions(expressions)[0],49)

    def test_score_expression_tested_on_multiple_weights(self):
        expressions=dict(ref.EXPRESSIONS);expressions[4]='0.7*coverage_rate + 0.3*cost_score'
        self.assertLess(check_expressions(expressions)[0],49)

    def test_strict_comparison_rejects_equal(self):
        expressions=dict(ref.EXPRESSIONS);expressions[5]='score >= best_score'
        self.assertLess(check_expressions(expressions)[0],49)

    def test_same_data_object_for_costs(self):
        import stage3_core
        self.assertIs(stage3_core.INSTALLATION_COSTS,INSTALLATION_COSTS)

    def test_bad_weights(self):
        for w in [-.1,1.1,float('nan'),float('inf'),True,'0.7']:
            with self.subTest(weight=w),self.assertRaises(ValueError):
                evaluate_plan(('B','D','G'),w)

    def test_invalid_return_values(self):
        for p in [None,('A','B'),('A','A','B'),('A','B','Z'),[['A'],'B','C'],{'A','B','C'},'ABC']:
            with self.subTest(plan=p):self.assertFalse(valid_plan(p))

    def test_overlap_deduplicated(self):
        plan=('A','E','G')
        total=sum(len(ROUTER_COVERAGE[r]) for r in plan)
        actual=evaluate_plan(plan)['covered_count']
        self.assertGreater(total,actual)
        self.assertLessEqual(actual,len(CLASSROOMS))

    def test_reference_geometry_independent_of_precomputed_map(self):
        for plan in combinations(ROUTERS,3):
            covered={c for c,(x,y) in CLASSROOMS.items() if any(
                (x-ROUTERS[r][0])**2+(y-ROUTERS[r][1])**2<=9 for r in plan)}
            self.assertEqual(set(evaluate_plan(plan)['covered']),covered)

    def test_guided_and_free_algorithms_all_weights(self):
        for w in [1,.7,.3]:
            for source in [assemble_algorithm(ref.BLOCKS),ref.FREE_ALGORITHM]:
                with self.subTest(weight=w):
                    plan=run_code(source,w,ref.EXPRESSIONS)
                    self.assertTrue(verify_optimal(plan,w))

    def test_weight_changes_selected_plan(self):
        plans=[find_best_plan(w)[0]['routers'] for w in [1,.7,.3]]
        self.assertEqual(plans[0],('B','D','E'))
        self.assertEqual(plans[1],('B','D','G'))
        self.assertNotEqual(plans[1],plans[2])

    def test_tied_top_scores_accepted(self):
        # At cost-only weighting, make every installation cost equal.
        with patch.dict(INSTALLATION_COSTS,{r:100 for r in ROUTERS}):
            self.assertTrue(verify_optimal(('A','B','C'),0))
            self.assertTrue(verify_optimal(('E','F','G'),0))

    def test_all_nonoptimal_plans_rejected(self):
        for w in [1,.7,.3]:
            best,plans=find_best_plan(w)
            for p in plans:
                self.assertEqual(verify_optimal(p['routers'],w),
                    math.isclose(best['score'],p['score'],abs_tol=1e-9))

    def test_student_helpers_reuse_expressions(self):
        expressions=dict(ref.EXPRESSIONS);expressions[3]='0'
        result=run_code('return student_cost(("A","B","C"))',.7,expressions)
        self.assertEqual(result,0)

    def test_each_guided_block_independent(self):
        for key in 'ABC':
            q=queue.Queue();exercise_worker(key,ref.BLOCKS[key],.7,ref.EXPRESSIONS,q)
            status,r=q.get();self.assertEqual(status,'tests');self.assertEqual(r['passed'],r['total'])

    def test_incomplete_block_reports_failure(self):
        q=queue.Queue();exercise_worker('B','pass',.7,ref.EXPRESSIONS,q)
        status,r=q.get();self.assertEqual(status,'tests');self.assertEqual(r['passed'],0)
        self.assertIn('NameError',r['errors'][0])

    def test_debug_originals_fail_repairs_pass(self):
        for key in DEBUG_STARTERS:
            for source,should_pass in [(DEBUG_STARTERS[key],False),(ref.DEBUG_REPAIRS[key],True)]:
                q=queue.Queue();exercise_worker(key,source,.7,ref.EXPRESSIONS,q)
                status,r=q.get();self.assertEqual(status,'tests')
                self.assertEqual(r['passed']==r['total'],should_pass)

    def test_import_and_file_access_rejected(self):
        for source in ['import os\nreturn None','return open("data.py")','return ROUTERS.__class__']:
            with self.assertRaises(ValueError):validate_student_algorithm(source)

    def test_invalid_or_missing_algorithm_return(self):
        for source in ['pass','return ("A", "A", "B")','return ("A","B","Z")']:
            q=queue.Queue();exercise_worker('Algorithm',source,.7,ref.EXPRESSIONS,q)
            self.assertEqual(q.get()[0],'error')

    def test_worker_uses_passed_weight_under_spawn(self):
        ctx=mp.get_context('spawn');q=ctx.Queue()
        p=ctx.Process(target=exercise_worker,args=('Algorithm',ref.FREE_ALGORITHM,1,ref.EXPRESSIONS,q))
        p.start()
        try:
            status,result=q.get(timeout=3);self.assertEqual(status,'plan');self.assertEqual(result,('B','D','E'))
        finally:
            p.join(timeout=.5)
            if p.is_alive():p.terminate();p.join()
            q.close()

    def test_runaway_process_can_be_terminated(self):
        ctx=mp.get_context('spawn');q=ctx.Queue()
        source='for x in range(1000000000000):\n    pass\nreturn ("A","B","C")'
        p=ctx.Process(target=exercise_worker,args=('Algorithm',source,.7,ref.EXPRESSIONS,q))
        p.start();p.join(timeout=.2)
        self.assertTrue(p.is_alive());p.terminate();p.join(timeout=1)
        self.assertFalse(p.is_alive());q.close()


if __name__=='__main__':unittest.main()
