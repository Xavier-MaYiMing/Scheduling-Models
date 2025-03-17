import cplex
import gurobipy as gp
from gurobipy import GRB
from docplex.cp.model import CpoModel


class DFSP:
    def __init__(self):
        self.n = 0  # the number of jobs
        self.g = 0  # the number of stages
        self.f = 0  # the number of factories
        self.p = []  # the set of processing times


def parser(file_path):
    instance = DFSP()
    with open(file_path, 'r') as f:
        instance.n = int(f.readline().strip().split()[0])
        instance.g = int(f.readline().strip().split()[0])
        instance.f = int(f.readline().strip().split()[0])
        instance.p = []
        for _ in range(instance.n):
            instance.p.append([int(x) for x in f.readline().strip().split()])
    return instance


def dfsp_mip_cplex_model(file_path, threads=1, time_limit=3600):
    instance = parser(file_path)

    # create the model
    mdl = cplex.Cplex()

    # variable x
    x_names = [f'x_{i}_{j1}_{j2}' for i in range(instance.g) for j1 in range(instance.n - 1) for j2 in range(j1 + 1, instance.n)]
    x_objs = [0] * len(x_names)
    x_lbs = [0] * len(x_names)
    x_ubs = [1] * len(x_names)
    x_types = ['B'] * len(x_names)

    # variable q
    q_names = [f'q_{j}_{f}' for j in range(instance.n) for f in range(instance.f)]
    q_objs = [0] * len(q_names)
    q_lbs = [0] * len(q_names)
    q_ubs = [1] * len(q_names)
    q_types = ['B'] * len(q_names)

    # variable c
    c_names = [f'c_{j}_{i}' for j in range(instance.n) for i in range(instance.g)]
    c_objs = [0] * len(c_names)
    c_lbs = [0] * len(c_names)
    c_ubs = [float('inf')] * len(c_names)
    c_types = ['C'] * len(c_names)

    # variable Cmax
    Cmax_name = ['Cmax']
    Cmax_obj = [1]
    Cmax_lb = [0]
    Cmax_ub = [float('inf')]
    Cmax_type = ['C']

    # constraints
    constrs = []
    senses = []
    rhs = []

    # constraint (1)
    for j in range(instance.n):
        variables = [f'c_{j}_{0}']
        coefficients = [1]
        constrs.append([variables, coefficients])
        senses.append('G')
        rhs.append(instance.p[j][0])

    # constraint (2)
    for j in range(instance.n):
        for i in range(1, instance.g):
            variables = [f'c_{j}_{i}', f'c_{j}_{i - 1}']
            coefficients = [1, -1]
            constrs.append([variables, coefficients])
            senses.append('G')
            rhs.append(instance.p[j][i])

    # constraint (3)
    for j in range(instance.n):
        variables = [f'q_{j}_{f}' for f in range(instance.f)]
        coefficients = [1] * instance.f
        constrs.append([variables, coefficients])
        senses.append('E')
        rhs.append(1)

    # constraints (4) and (5)
    M = 100000
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for i in range(instance.g):
                for f in range(instance.f):
                    variables = [f'c_{j1}_{i}', f'c_{j2}_{i}', f'x_{i}_{j1}_{j2}', f'q_{j1}_{f}', f'q_{j2}_{f}']
                    coefficients = [1, -1, -M, -M, -M]
                    constrs.append([variables, coefficients])
                    senses.append('G')
                    rhs.append(instance.p[j1][i] - 3 * M)

                    variables = [f'c_{j2}_{i}', f'c_{j1}_{i}', f'x_{i}_{j1}_{j2}', f'q_{j1}_{f}', f'q_{j2}_{f}']
                    coefficients = [1, -1, M, -M, -M]
                    constrs.append([variables, coefficients])
                    senses.append('G')
                    rhs.append(instance.p[j2][i] - 2 * M)

    # constraint (6)
    for j in range(instance.n):
        variables = ['Cmax', f'c_{j}_{instance.g - 1}']
        coefficients = [1, -1]
        constrs.append([variables, coefficients])
        senses.append('G')
        rhs.append(0)

    # add variables
    all_names = x_names + q_names + c_names + Cmax_name
    all_objs = x_objs + q_objs + c_objs + Cmax_obj
    all_lbs = x_lbs + q_lbs + c_lbs + Cmax_lb
    all_ubs = x_ubs + q_ubs + c_ubs + Cmax_ub
    all_types = x_types + q_types + c_types + Cmax_type
    mdl.variables.add(obj=all_objs, lb=all_lbs, ub=all_ubs, names=all_names, types=all_types)

    # add constraints
    mdl.linear_constraints.add(lin_expr=constrs, senses=senses, rhs=rhs)

    # set the objective sense
    mdl.objective.set_sense(mdl.objective.sense.minimize)

    # solve the model
    mdl.set_warning_stream(None)
    mdl.parameters.threads.set(threads)
    mdl.parameters.timelimit.set(time_limit)
    mdl.solve()

    if mdl.solution.is_primal_feasible():
        Cmax = mdl.solution.get_values('Cmax')
        print(f'Optimal objective value (CPLEX): {Cmax}')
    else:
        print('No feasible solution found by CPLEX!')


def dfsp_mip_gurobi_model(file_path, threads=1, time_limit=3600):
    instance = parser(file_path)

    # create the model
    mdl = gp.Model()

    # variable x
    x_vars = {}
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for i in range(instance.g):
                x_vars[(i, j1, j2)] = mdl.addVar(vtype=GRB.BINARY, name=f'x_{i}_{j1}_{j2}')

    # variable q
    q_vars = {}
    for j in range(instance.n):
        for f in range(instance.f):
            q_vars[(j, f)] = mdl.addVar(vtype=GRB.BINARY, name=f'q_{j}_{f}')

    # variable c
    c_vars = {}
    for j in range(instance.n):
        for i in range(instance.g):
            c_vars[(j, i)] = mdl.addVar(vtype=GRB.CONTINUOUS, name=f'c_{j}_{i}', lb=0)

    # variable Cmax
    Cmax = mdl.addVar(vtype=GRB.CONTINUOUS, name='Cmax', lb=0)

    # constraint (1)
    for j in range(instance.n):
        mdl.addConstr(c_vars[(j, 0)] >= instance.p[j][0], name=f'constr1_{j}')

    # constraint (2)
    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.addConstr(c_vars[(j, i)] >= c_vars[(j, i - 1)] + instance.p[j][i], name=f'constr2_{j}_{i}')

    # constraint (3)
    for j in range(instance.n):
        mdl.addConstr(gp.quicksum(q_vars[(j, f)] for f in range(instance.f)) == 1, name=f'constr3_{j}')

    # constraint (4) and (5)
    M = 100000
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for i in range(instance.g):
                for f in range(instance.f):
                    mdl.addConstr(c_vars[(j1, i)] >= c_vars[(j2, i)] + instance.p[j1][i] - M * (3 - x_vars[(i, j1, j2)] - q_vars[(j1, f)] - q_vars[(j2, f)]), name=f'constr4_{j1}_{j2}_{i}_{f}')
                    mdl.addConstr(c_vars[(j2, i)] >= c_vars[(j1, i)] + instance.p[j2][i] - M * (2 + x_vars[(i, j1, j2)] - q_vars[(j1, f)] - q_vars[(j2, f)]), name=f'constr5_{j1}_{j2}_{i}_{f}')

    # constraint (6)
    for j in range(instance.n):
        mdl.addConstr(Cmax >= c_vars[(j, instance.g - 1)], name=f'constr6_{j}')

    # set the objective
    mdl.setObjective(Cmax, GRB.MINIMIZE)

    # solve the model
    mdl.setParam('Threads', threads)
    mdl.setParam('TimeLimit', time_limit)
    mdl.optimize()

    if mdl.status == GRB.OPTIMAL or mdl.status == GRB.SUBOPTIMAL:
        Cmax_value = Cmax.X
        print(f'Optimal objective value (Gurobi): {Cmax_value}')
    else:
        print('No feasible solution found by Gurobi!')


def dfsp_cp_model(file_path, threads=1, time_limit=3600, agent='local', execfile='/Applications/CPLEX_Studio1210/cpoptimizer/bin/x86-64_osx/cpoptimizer'):
    """
    The execfile parameter specifies the path to the CP Optimizer executable.
    This is required to run the solver, as it defines the core binary that handles the solving process.
    The exact path depends on the installation location of IBM ILOG CPLEX Optimization Studio.
    For example:
      - On macOS: '/Applications/CPLEX_Studio1210/cpoptimizer/bin/x86-64_osx/cpoptimizer'
      - On Windows: 'C:\\Program Files\\IBM\\ILOG\\CPLEX_Studio1210\\cpoptimizer\\bin\\x64_win64\\cpoptimizer.exe'
      - On Linux: '/opt/ibm/ILOG/CPLEX_Studio1210/cpoptimizer/bin/x86-64_linux/cpoptimizer'
    Ensure the provided path matches the location of the installed CP Optimizer executable on your system.
    """
    instance = parser(file_path)

    # create the model
    mdl = CpoModel()

    # constraint (1)
    tasks = []
    for j in range(instance.n):
        tasks.append([])
        for i in range(instance.g):
            tasks[j].append(mdl.interval_var(name=f'tasks_{j}_{i}', size=instance.p[j][i]))

    # constraint (2)
    _tasks = []
    for j in range(instance.n):
        _tasks.append([])
        for i in range(instance.g):
            _tasks[j].append([])
            for f in range(instance.f):
                _tasks[j][i].append(mdl.interval_var(name=f'_tasks_{j}_{i}_{f}', optional=True, size=instance.p[j][i]))

    # constraint (3)
    for j in range(instance.n):
        for i in range(1, instance.g):
            for f in range(instance.f):
                mdl.add(mdl.presence_of(_tasks[j][0][f]) == mdl.presence_of(_tasks[j][i][f]))

    # constraint (4)
    for j in range(instance.n):
        for i in range(instance.g):
            mdl.add(mdl.alternative(tasks[j][i], [_tasks[j][i][f] for f in range(instance.f)]))

    # constraint (5)
    for i in range(instance.g):
        for f in range(instance.f):
            mdl.add(mdl.no_overlap([_tasks[j][i][f] for j in range(instance.n)]))

    # constraint (6)
    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.add(mdl.end_before_start(tasks[j][i - 1], tasks[j][i]))

    # constraint (5)
    mdl.add(mdl.minimize(mdl.max([mdl.end_of(tasks[j][instance.g - 1]) for j in range(instance.n)])))

    # solve the model
    result = mdl.solve(TimeLimit=time_limit, Workers=threads, LogVerbosity='Quiet', agent=agent, execfile=execfile)

    if result:
        print(f'Optimal objective value (CP Optimizer): {result.get_objective_value()}')
    else:
        print('No feasible solution found by CP Optimizer!')


if __name__ == '__main__':
    path = 'test cases/0.txt'
    print('-------------------------------CPLEX-------------------------------')
    dfsp_mip_cplex_model(path, threads=6)
    print('\n\n\n-------------------------------Gurobi-------------------------------')
    dfsp_mip_gurobi_model(path, threads=6)
    print('\n\n\n-------------------------------Constraint Programming------------------------------')
    dfsp_cp_model(path)
