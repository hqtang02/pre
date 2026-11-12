"""Student code execution, adapted from the original restricted evaluator.
This is a local teaching guard, not a security sandbox for hostile code.
"""
import ast
import math
import operator
from itertools import combinations
from data import CLASSROOMS, ROUTERS, ROUTER_LIMIT, ROUTER_COVERAGE, INSTALLATION_COSTS
from stage3_core import valid_plan, get_max_cost
MAX_COST = get_max_cost()

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

COMPARISON_OPERATORS = {
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
}

def evaluate_expression(source, variables):

    if not source.strip():
        raise ValueError("Expression is empty.")

    if len(source) > 300:
        raise ValueError("Expression is too long.")

    tree = ast.parse(source, mode="eval")

    if len(list(ast.walk(tree))) > 80:
        raise ValueError("Expression is too complex.")

    def walk(node, depth=0):

        if depth > 20:
            raise ValueError("Expression is too deep.")

        if isinstance(node, ast.Expression):
            return walk(node.body, depth + 1)

        if isinstance(node, ast.Constant):
            if type(node.value) in (
                int, float, bool, str
            ):
                return node.value

        if isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]

            raise ValueError(
                f"Unknown variable: {node.id}"
            )

        if isinstance(node, ast.Subscript):

            container = walk(
                node.value, depth + 1
            )

            index = walk(
                node.slice, depth + 1
            )

            if isinstance(container, (list, tuple)):
                if type(index) is not int:
                    raise ValueError(
                        "List index must be an integer."
                    )

                return container[index]

            if isinstance(container, dict):
                return container[index]

            raise ValueError(
                "Unsupported indexing operation."
            )

        if isinstance(node, ast.BinOp):

            operation = BINARY_OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    "Unsupported arithmetic operator."
                )

            left = walk(node.left, depth + 1)
            right = walk(node.right, depth + 1)

            if (
                type(left) not in (int, float)
                or type(right) not in (int, float)
            ):
                raise ValueError(
                    "Arithmetic requires numbers."
                )

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):

            value = walk(
                node.operand, depth + 1
            )

            if type(value) not in (int, float):
                raise ValueError(
                    "Unary operation requires a number."
                )

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

        if isinstance(node, ast.Compare):

            left = walk(
                node.left, depth + 1
            )

            for op, comparator in zip(
                node.ops,
                node.comparators
            ):

                comparison = COMPARISON_OPERATORS.get(
                    type(op)
                )

                if comparison is None:
                    raise ValueError(
                        "Unsupported comparison."
                    )

                right = walk(
                    comparator, depth + 1
                )

                if not comparison(left, right):
                    return False

                left = right

            return True

        raise ValueError(
            "Unsupported expression syntax."
        )

    return walk(tree)

ALLOWED_FUNCTIONS = {
    "combinations",
    "set",
    "len",
    "sum",
    "sorted",
    "range",
    "tuple",
    "list",
    "min",
    "max",
    "enumerate", "student_cost", "student_score", "student_better",
}

ALLOWED_METHODS = {
    "update",
    "add",
    "keys",
    "values",
    "items",
    "append",
}

ALLOWED_NODES = (
    ast.Module,
    ast.FunctionDef,
    ast.arguments,
    ast.arg,
    ast.Assign,
    ast.AugAssign,
    ast.For,
    ast.If,
    ast.Return,
    ast.Pass,
    ast.Break,
    ast.Continue,
    ast.Expr,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Constant,
    ast.Tuple,
    ast.List,
    ast.Set,
    ast.Dict,
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.Call,
    ast.Attribute,
    ast.Subscript,
    ast.IfExp,
    ast.ListComp,
    ast.SetComp,
    ast.GeneratorExp,
    ast.comprehension,
    ast.keyword,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.USub,
    ast.UAdd,
    ast.Not,
    ast.And,
    ast.Or,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
)

def validate_student_algorithm(source):

    if not source.strip():
        raise ValueError(
            "TODO 6 is empty."
        )

    if len(source) > 8000:
        raise ValueError(
            "Algorithm is too long."
        )

    wrapped = (
        "def student_solution():\n"
        + "\n".join(
            "    " + line
            for line in source.splitlines()
        )
        + "\n"
    )

    tree = ast.parse(
        wrapped,
        mode="exec"
    )

    nodes = list(ast.walk(tree))

    if len(nodes) > 600:
        raise ValueError(
            "Algorithm is too complex."
        )

    for node in nodes:

        if not isinstance(
            node,
            ALLOWED_NODES
        ):
            raise ValueError(
                "Unsupported syntax: "
                + type(node).__name__
            )

        if isinstance(node, ast.FunctionDef):
            if node.name != "student_solution":
                raise ValueError(
                    "Do not define another function."
                )

        if isinstance(node, ast.Name):
            if node.id.startswith("_"):
                raise ValueError(
                    "Invalid variable name."
                )

        if isinstance(node, ast.Attribute):
            if node.attr not in ALLOWED_METHODS:
                raise ValueError(
                    f"Method .{node.attr}() is not allowed."
                )

        if isinstance(node, ast.Call):

            function = node.func

            if isinstance(function, ast.Name):
                if function.id not in ALLOWED_FUNCTIONS:
                    raise ValueError(
                        "Function not allowed: "
                        + function.id
                    )

            elif isinstance(function, ast.Attribute):
                if function.attr not in ALLOWED_METHODS:
                    raise ValueError(
                        "Method not allowed."
                    )

            else:
                raise ValueError(
                    "Unsupported function call."
                )

    return compile(
        tree,
        "<TODO 6>",
        "exec"
    )



def make_student_helpers(expressions, weight):
    def student_cost(selected):
        return evaluate_expression(expressions[3], dict(costs=INSTALLATION_COSTS, selected=selected))
    def student_score(coverage_rate, cost_score):
        return evaluate_expression(expressions[4], dict(coverage_rate=coverage_rate,
            cost_score=cost_score, coverage_weight=weight, cost_weight=1-weight))
    def student_better(score, best_score):
        return evaluate_expression(expressions[5], dict(score=score, best_score=best_score))
    return dict(student_cost=student_cost, student_score=student_score, student_better=student_better)


def _expression_cases():
    """35 cost cases, 8 score cases and 6 comparison cases."""
    cases = []
    for selected in combinations(sorted(ROUTERS), ROUTER_LIMIT):
        cases.append((3, dict(costs=INSTALLATION_COSTS, selected=selected),
                      sum(INSTALLATION_COSTS[r] for r in selected)))
    for rate, cost, weight in [(1,0,.7), (.5,.4,.3), (0,1,1), (1,0,0),
                               (.9,.25,.7), (0,0,.3), (1,1,.7), (.3,.8,1)]:
        cases.append((4, dict(coverage_rate=rate,cost_score=cost,
            coverage_weight=weight,cost_weight=1-weight), weight*rate+(1-weight)*cost))
    for score,best in [(1,0),(0,1),(.5,.5),(0,-1),(.9,.8),(.2,.7)]:
        cases.append((5, dict(score=score,best_score=best), score>best))
    return cases


def check_expression_todos(expressions):
    """Return pass/fail for each TODO expression independently."""
    status = {3: True, 4: True, 5: True}
    for todo, variables, expected in _expression_cases():
        try:
            result = evaluate_expression(expressions[todo], variables)
            if todo == 5:
                correct = type(result) is bool and result == expected
            else:
                correct = (type(result) in (int, float)
                           and math.isfinite(result)
                           and math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-9))
            if not correct:
                status[todo] = False
        except Exception:
            status[todo] = False
    return status


def check_expressions(expressions):
    """35 cost cases, 8 score cases and 6 comparison cases, tested independently."""
    cases = _expression_cases()
    passed=0; errors=[]
    for todo, variables, expected in cases:
        try:
            result=evaluate_expression(expressions[todo], variables)
            correct = (type(result) is bool and result == expected) if todo==5 else (
                type(result) in (int,float) and math.isfinite(result)
                and math.isclose(result, expected, rel_tol=1e-9, abs_tol=1e-9))
            if not correct:
                raise ValueError(f"expected {expected}, got {result}")
            passed+=1
        except Exception as error:
            errors.append(f"TODO {todo}: {error}")
    return passed, len(cases), list(dict.fromkeys(errors))


BLOCK_HINTS = {
 'A': '# A: selected is a tuple of router IDs.\n# Build covered as a set of classroom IDs.\ncovered = set()\nfor router in selected:\n    pass  # merge this router\'s classrooms here',
 'B': '# B: selected and covered are available.\n# Set coverage_rate, total_cost, cost_score and score.\n# Reuse student_cost(selected) and student_score(rate, cost_score).\npass',
 'C': '# C: score, best_score, selected and best_plan are available.\n# Reuse student_better(score, best_score).\n# Update BOTH best_score and best_plan when better.\npass',
}
DEBUG_STARTERS = {
 'Overlap': 'covered_count = 0\nfor router in selected:\n    covered_count += len(ROUTER_COVERAGE[router])',
 'Comparison': 'if score < best_score:\n    best_score = score\n    best_plan = selected',
}


def assemble_algorithm(blocks):
    def indent(code):
        return '\n'.join('    '+line for line in code.splitlines())
    return ('best_plan = None\nbest_score = -1\n'
            'for selected in combinations(sorted(ROUTERS), ROUTER_LIMIT):\n'
            + '\n'.join(indent(blocks[k]) for k in 'ABC') + '\nreturn best_plan\n')


def run_code(source, weight, expressions, variables=None):
    """Called only in the worker process for classroom code."""
    builtins = dict(set=set,len=len,sum=sum,sorted=sorted,range=range,tuple=tuple,
                    list=list,min=min,max=max,enumerate=enumerate)
    env=dict(__builtins__=builtins, ROUTERS=dict(ROUTERS),
             CLASSROOMS=dict(CLASSROOMS), ROUTER_LIMIT=ROUTER_LIMIT,
             ROUTER_COVERAGE={r:list(c) for r,c in ROUTER_COVERAGE.items()},
             INSTALLATION_COSTS=dict(INSTALLATION_COSTS),MAX_COST=MAX_COST,
             coverage_weight=weight,cost_weight=1-weight,combinations=combinations)
    env.update(make_student_helpers(expressions,weight))
    if variables:
        # Bind test inputs inside the function, because student assignments make
        # names such as best_score local under Python scope rules.
        source = "\n".join(f"{name} = {value!r}" for name, value in variables.items()) + "\n" + source
    exec(validate_student_algorithm(source),env)
    return env['student_solution']()


def exercise_worker(kind, source, weight, expressions, output_queue):
    """Independent block tests; never requires unfinished neighboring blocks."""
    from stage3_core import evaluate_plan, calculate_coverage
    try:
        if kind == 'Algorithm':
            result=run_code(source,weight,expressions)
            if not valid_plan(result):
                raise ValueError('Return exactly 3 different valid router IDs.')
            output_queue.put(('plan',tuple(result)))
            return
        cases=[]
        if kind in ('A','B','Overlap'):
            for selected in combinations(sorted(ROUTERS),ROUTER_LIMIT):
                expected=evaluate_plan(selected,weight)
                variables=dict(selected=selected, covered=set(expected['covered']))
                if kind=='A':
                    suffix='\nreturn covered'; target=set(expected['covered'])
                    variables.pop('covered')
                elif kind=='Overlap':
                    suffix='\nreturn covered_count'; target=expected['covered_count']
                else:
                    suffix='\nreturn (coverage_rate, total_cost, cost_score, score)'
                    target=(expected['coverage_rate'],expected['cost'],expected['cost_score'],expected['score'])
                cases.append((variables,suffix,target))
        else:  # C or comparison debugging
            for score,best in [(0,-1),(.5,.2),(.2,.5),(.5,.5),(.9,.8),(.1,.9)]:
                selected=('A','B','C'); old=('D','E','F') if best>=0 else None
                cases.append((dict(score=score,best_score=best,selected=selected,best_plan=old),
                    '\nreturn (best_score, best_plan)', (score,selected) if score>best else (best,old)))
        passed=0;errors=[]
        for variables,suffix,expected in cases:
            try:
                actual=run_code(source+suffix,weight,expressions,variables)
                if kind=='B':
                    ok=(isinstance(actual,tuple) and len(actual)==4 and all(
                        type(x) in (int,float) and math.isclose(x,y,rel_tol=1e-9,abs_tol=1e-9)
                        for x,y in zip(actual,expected)))
                elif kind=='A':
                    ok=type(actual) is set and actual==expected
                elif kind=='Overlap':
                    ok=type(actual) is int and actual==expected
                else:
                    ok=actual==expected
                if not ok:
                    raise ValueError(f"expected {expected}, got {actual}")
                passed+=1
            except Exception as error:
                errors.append(f"{variables.get('selected')}: {type(error).__name__}: {error}")
        output_queue.put(('tests',dict(kind=kind,passed=passed,total=len(cases),errors=errors[:3])))
    except Exception as error:
        output_queue.put(('error',f'{type(error).__name__}: {error}'))
