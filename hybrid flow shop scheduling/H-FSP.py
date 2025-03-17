import cplex
import gurobipy as gp
from gurobipy import GRB
from docplex.cp.model import CpoModel


class HFSP:
    def __init__(self):
        self.n = 0  # the number of jobs
        self.g = 0  # the number of stages
        self.m = []  # the number of machines
        self.p = []  # the set of processing times


def parser(file_path):
    instance = HFSP()
    with open(file_path, 'r') as f:
        instance.n = int(f.readline().strip().split()[0])
        instance.g = int(f.readline().strip().split()[0])
        instance.m = [int(x) for x in f.readline().strip().split()]
        instance.p = []
        for _ in range(instance.n):
            instance.p.append([int(x) for x in f.readline().strip().split()])
    return instance


def hfsp_mip_cplex_model(file_path, threads=1, time_limit=3600):
    instance = parser(file_path)

    # create the model
    mdl = cplex.Cplex()

    # variable x
    x_names = [f'x_{i}_{j1}_{j2}' for i in range(instance.g) for j1 in range(instance.n - 1) for j2 in range(j1 + 1, instance.n)]
    x_objs = [0] * len(x_names)
    x_lbs = [0] * len(x_names)
    x_ubs = [1] * len(x_names)
    x_types = ['B'] * len(x_names)

    # variable w
    w_names = [f'w_{j}_{i}_{k}' for j in range(instance.n) for i in range(instance.g) for k in range(instance.m[i])]
    w_objs = [0] * len(w_names)
    w_lbs = [0] * len(w_names)
    w_ubs = [1] * len(w_names)
    w_types = ['B'] * len(w_names)

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
        for i in range(instance.g):
            variables = [f'w_{j}_{i}_{k}' for k in range(instance.m[i])]
            coefficients = [1] * instance.m[i]
            constrs.append([variables, coefficients])
            senses.append('E')
            rhs.append(1)

    # constraint (4)
    M = 100000
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for i in range(instance.g):
                for k in range(instance.m[i]):
                    variables = [f'c_{j1}_{i}', f'c_{j2}_{i}', f'x_{i}_{j1}_{j2}', f'w_{j1}_{i}_{k}', f'w_{j2}_{i}_{k}']
                    coefficients = [1, -1, -M, -M, -M]
                    constrs.append([variables, coefficients])
                    senses.append('G')
                    rhs.append(instance.p[j1][i] - 3 * M)

    # constraint (5)
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for i in range(instance.g):
                for k in range(instance.m[i]):
                    variables = [f'c_{j2}_{i}', f'c_{j1}_{i}', f'x_{i}_{j1}_{j2}', f'w_{j1}_{i}_{k}', f'w_{j2}_{i}_{k}']
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
    all_names = x_names + w_names + c_names + Cmax_name
    all_objs = x_objs + w_objs + c_objs + Cmax_obj
    all_lbs = x_lbs + w_lbs + c_lbs + Cmax_lb
    all_ubs = x_ubs + w_ubs + c_ubs + Cmax_ub
    all_types = x_types + w_types + c_types + Cmax_type
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


def hfsp_mip_gurobi_model(file_path, threads=1, time_limit=3600):
    instance = parser(file_path)

    # create the model
    mdl = gp.Model()

    # variable x
    x_vars = {}
    for i in range(instance.g):
        for j1 in range(instance.n - 1):
            for j2 in range(j1 + 1, instance.n):
                x_vars[(i, j1, j2)] = mdl.addVar(vtype=GRB.BINARY, name=f'x_{i}_{j1}_{j2}')

    # variable w
    w_vars = {}
    for j in range(instance.n):
        for i in range(instance.g):
            for k in range(instance.m[i]):
                w_vars[(j, i, k)] = mdl.addVar(vtype=GRB.BINARY, name=f'w_{j}_{i}_{k}')

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
        for i in range(instance.g):
            mdl.addConstr(gp.quicksum([w_vars[(j, i, k)] for k in range(instance.m[i])]) == 1, name=f'constr3_{j}_{i}')

    # constraints (4) and (5)
    M = 100000
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for i in range(instance.g):
                for k in range(instance.m[i]):
                    mdl.addConstr(c_vars[(j1, i)] - c_vars[(j2, i)] - M * x_vars[(i, j1, j2)] - M * w_vars[(j1, i, k)] - M * w_vars[(j2, i, k)] >= instance.p[j1][i] - 3 * M, name=f'constr4_{j1}_{j2}_{i}_{k}')
                    mdl.addConstr(c_vars[(j2, i)] - c_vars[(j1, i)] + M * x_vars[(i, j1, j2)] - M * w_vars[(j1, i, k)] - M * w_vars[(j2, i, k)] >= instance.p[j2][i] - 2 * M, name=f'constr5_{j1}_{j2}_{i}_{k}')

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


def hfsp_cp_model1(file_path, threads=1, time_limit=3600, agent='local', execfile='/Applications/CPLEX_Studio1210/cpoptimizer/bin/x86-64_osx/cpoptimizer'):
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
    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.add(mdl.end_before_start(tasks[j][i - 1], tasks[j][i]))

    # constraint (3)
    for i in range(instance.g):
        mdl.add(mdl.sum([mdl.pulse(tasks[j][i], 1) for j in range(instance.n)]) <= instance.m[i])

    # constraint (4)
    mdl.add(mdl.minimize(mdl.max([mdl.end_of(tasks[j][instance.g - 1]) for j in range(instance.n)])))

    # solve the model
    result = mdl.solve(TimeLimit=time_limit, Workers=threads, LogVerbosity='Quiet', agent=agent, execfile=execfile)

    if result:
        print(f'Optimal objective value (CP Optimizer): {result.get_objective_value()}')
    else:
        print('No feasible solution found by CP Optimizer!')


def hfsp_cp_model2(file_path, threads=1, time_limit=3600, agent='local', execfile='/Applications/CPLEX_Studio1210/cpoptimizer/bin/x86-64_osx/cpoptimizer'):
    instance = parser(file_path)

    # create the model
    mdl = CpoModel()

    # constraint (1)
    tasks = []
    for j in range(instance.n):
        tasks.append([])
        for i in range(instance.g):
            tasks[j].append([])
            for k in range(instance.m[i]):
                tasks[j][i].append(mdl.interval_var(name=f'tasks_{j}_{i}_{k}', optional=True, size=instance.p[j][i]))

    # constraint (2)
    _tasks = []
    for j in range(instance.n):
        _tasks.append([])
        for i in range(instance.g):
            _tasks[j].append(mdl.interval_var(name=f'_tasks_{j}_{i}'))
    for j in range(instance.n):
        for i in range(instance.g):
            mdl.add(mdl.alternative(_tasks[j][i], [tasks[j][i][k] for k in range(instance.m[i])]))

    # constraint (3)
    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.add(mdl.end_before_start(_tasks[j][i - 1], _tasks[j][i]))

    # constraint (4)
    for i in range(instance.g):
        for k in range(instance.m[i]):
            mdl.add(mdl.no_overlap([tasks[j][i][k] for j in range(instance.n)]))

    # constraint (5)
    mdl.add(mdl.minimize(mdl.max([mdl.end_of(_tasks[j][instance.g - 1]) for j in range(instance.n)])))

    # solve the model
    result = mdl.solve(TimeLimit=time_limit, Workers=threads, LogVerbosity='Quiet', agent=agent, execfile=execfile)

    if result:
        print(f'Optimal objective value (CP Optimizer): {result.get_objective_value()}')
    else:
        print('No feasible solution found by CP Optimizer!')


if __name__ == '__main__':
    path = 'test cases/0.txt'
    print('-------------------------------CPLEX-------------------------------')
    hfsp_mip_cplex_model(path, threads=6)
    print('\n\n\n-------------------------------Gurobi-------------------------------')
    hfsp_mip_gurobi_model(path, threads=6)
    print('\n\n\n-------------------------------Constraint Programming------------------------------')
    hfsp_cp_model1(path)
    hfsp_cp_model2(path)
