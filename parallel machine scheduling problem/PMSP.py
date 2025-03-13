import cplex
import gurobipy as gp
from gurobipy import GRB
from docplex.cp.model import CpoModel


class PMSP:
    def __init__(self):
        self.n = 0  # the number of jobs
        self.g = 0  # the number of machines
        self.p = []  # the set of processing times


def parser(file_path):
    instance = PMSP()
    with open(file_path, 'r') as f:
        instance.n = int(f.readline().strip().split()[0])
        instance.g = int(f.readline().strip().split()[0])
        instance.p = []
        for _ in range(instance.n):
            instance.p.append([int(x) for x in f.readline().strip().split()])
    return instance


def pmsp_mip_cplex_model(file_path, threads=1, time_limit=3600):
    instance = parser(file_path)

    # create the model
    mdl = cplex.Cplex()

    # variable y
    y_names = [f'y_{j}_{i}' for j in range(instance.n) for i in range(instance.g)]
    y_objs = [0] * len(y_names)
    y_lbs = [0] * len(y_names)
    y_ubs = [1] * len(y_names)
    y_types = ['B'] * len(y_names)

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
        variables = [f'y_{j}_{i}' for i in range(instance.g)]
        coefficients = [1] * instance.g
        constrs.append([variables, coefficients])
        senses.append('E')
        rhs.append(1)

    # constraint (2)
    for i in range(instance.g):
        variables = ['Cmax']
        variables += [f'y_{j}_{i}' for j in range(instance.n)]
        coefficients = [1]
        coefficients += [-instance.p[j][i] for j in range(instance.n)]
        constrs.append([variables, coefficients])
        senses.append('G')
        rhs.append(0)

    # add variables
    all_names = y_names + Cmax_name
    all_objs = y_objs + Cmax_obj
    all_lbs = y_lbs + Cmax_lb
    all_ubs = y_ubs + Cmax_ub
    all_types = y_types + Cmax_type
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


def pmsp_mip_gurobi_model(file_path, threads=1, time_limit=3600):
    instance = parser(file_path)

    # create the model
    mdl = gp.Model()

    # variable y
    y_vars = {}
    for j in range(instance.n):
        for i in range(instance.g):
            y_vars[(j, i)] = mdl.addVar(vtype=GRB.BINARY, name=f'y_{j}_{i}')

    # variable Cmax
    Cmax = mdl.addVar(vtype=GRB.CONTINUOUS, name='Cmax', lb=0)

    # constraint (1)
    for j in range(instance.n):
        mdl.addConstr(gp.quicksum([y_vars[(j, i)] for i in range(instance.g)]) == 1, name=f'constr1_{j}')

    # constraint (2)
    for i in range(instance.g):
        mdl.addConstr(Cmax >= gp.quicksum([instance.p[j][i] * y_vars[(j, i)] for j in range(instance.n)]), name=f'constr2_{i}')

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


def pmsp_cp_model1(file_path, threads=1, time_limit=3600, agent='local', execfile='/Applications/CPLEX_Studio1210/cpoptimizer/bin/x86-64_osx/cpoptimizer'):
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
    machine = [mdl.integer_var(min=0, max=instance.g - 1) for _ in range(instance.n)]

    # constraint (2)
    duration = [mdl.element(instance.p[j], machine[j]) for j in range(instance.n)]
    makespan = mdl.max([sum([instance.p[j][i] * (machine[j] == i) for j in range(instance.n)]) for i in range(instance.g)])

    # constraint (3)
    mdl.add(sum([duration[j] for j in range(instance.n)]) <= instance.g * makespan)
    mdl.add(mdl.minimize(makespan))

    # solve the model
    result = mdl.solve(TimeLimit=time_limit, Workers=threads, LogVerbosity='Quiet', agent=agent, execfile=execfile)

    if result:
        print(f'Optimal objective value (CP Optimizer): {result.get_objective_value()}')
    else:
        print('No feasible solution found by CP Optimizer!')


def pmsp_cp_model2(file_path, threads=1, time_limit=3600, agent='local', execfile='/Applications/CPLEX_Studio1210/cpoptimizer/bin/x86-64_osx/cpoptimizer'):
    instance = parser(file_path)

    # create the model
    mdl = CpoModel()

    # constraint (1)
    tasks = []
    for j in range(instance.n):
        tasks.append([])
        for i in range(instance.g):
            tasks[j].append(mdl.interval_var(name=f'tasks_{j}_{i}', optional=True, size=instance.p[j][i]))

    # constraint (2)
    _tasks = []
    for j in range(instance.n):
        _tasks.append(mdl.interval_var(name=f'_tasks_{j}'))
    for j in range(instance.n):
        mdl.add(mdl.alternative(_tasks[j], [tasks[j][i] for i in range(instance.g)]))

    # constraint (3)
    for i in range(instance.g):
        mdl.add(mdl.no_overlap([tasks[j][i] for j in range(instance.n)]))

    # constraint (4)
    mdl.add(mdl.minimize(mdl.max([mdl.end_of(_tasks[j]) for j in range(instance.n)])))

    # solve the model
    result = mdl.solve(TimeLimit=time_limit, Workers=threads, LogVerbosity='Quiet', agent=agent, execfile=execfile)

    if result:
        print(f'Optimal objective value (CP Optimizer): {result.get_objective_value()}')
    else:
        print('No feasible solution found by CP Optimizer!')


def pmsp_cp_model3(file_path, threads=1, time_limit=3600, agent='local', execfile='/Applications/CPLEX_Studio1210/cpoptimizer/bin/x86-64_osx/cpoptimizer'):
    instance = parser(file_path)

    # create the CP model
    mdl = CpoModel()

    # constraint (1)
    Y = []
    for j in range(instance.n):
        Y.append([])
        for i in range(instance.g):
            Y[j].append(mdl.binary_var(name=f'Y_{j}_{i}'))

    # constraint (2)
    processing_time = []
    for i in range(instance.g):
        processing_time.append(mdl.sum(instance.p[j][i] * Y[j][i] for j in range(instance.n)))
    Cmax = mdl.max(processing_time)
    mdl.add(mdl.minimize(Cmax))

    # constraint (3)
    for j in range(instance.n):
        mdl.add(mdl.sum(Y[j][i] for i in range(instance.g)) == 1)

    # solve the model
    result = mdl.solve(TimeLimit=time_limit, Workers=threads, LogVerbosity='Quiet', agent=agent, execfile=execfile)

    if result:
        print(f'Optimal objective value (CP Optimizer): {result.get_objective_value()}')
    else:
        print('No feasible solution found by CP Optimizer!')


if __name__ == '__main__':
    path = 'test cases/0.txt'
    print('-------------------------------CPLEX-------------------------------')
    pmsp_mip_cplex_model(path, threads=6)
    print('\n\n\n-------------------------------Gurobi-------------------------------')
    pmsp_mip_gurobi_model(path, threads=6)
    print('\n\n\n-------------------------------Constraint Programming------------------------------')
    pmsp_cp_model1(path)
    pmsp_cp_model2(path)
    pmsp_cp_model3(path)
