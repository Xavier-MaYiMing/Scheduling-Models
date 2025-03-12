import cplex
import gurobipy as gp
from gurobipy import GRB
from docplex.cp.model import CpoModel


class FJSP:
    def __init__(self):
        self.n = 0  # the number of jobs
        self.g = 0  # the number of machines
        self.o = []  # the set of operations
        self.p = []  # the set of processing times


def parser(file_path):
    instance = FJSP()
    with open(file_path, 'r') as f:
        instance.n = int(f.readline().strip().split()[0])
        instance.g = int(f.readline().strip().split()[0])
        instance.o = [int(x) for x in f.readline().strip().split()]
        instance.p = [[] for _ in range(instance.n)]
        for j in range(instance.n):
            for k in range(instance.o[j]):
                x = [int(x) for x in f.readline().strip().split()]
                instance.p[j].append(x)
    return instance


def fjsp_mip_cplex_model(file_path, threads=1, time_limit=3600):
    instance = parser(file_path)

    # create the model
    mdl = cplex.Cplex()

    # variable z
    z_names = [f'z_{j}_{k}_{i}' for j in range(instance.n) for k in range(instance.o[j]) for i in range(instance.g) if instance.p[j][k][i] > 0]
    z_objs = [0] * len(z_names)
    z_lbs = [0] * len(z_names)
    z_ubs = [1] * len(z_names)
    z_types = ['B'] * len(z_names)

    # variable x
    x_names = [f'x_{j1}_{k1}_{j2}_{k2}' for j1 in range(instance.n - 1) for j2 in range(j1 + 1, instance.n) for k1 in range(instance.o[j1]) for k2 in range(instance.o[j2])]
    x_objs = [0] * len(x_names)
    x_lbs = [0] * len(x_names)
    x_ubs = [1] * len(x_names)
    x_types = ['B'] * len(x_names)

    # variable c
    c_names = [f'c_{j}_{k}' for j in range(instance.n) for k in range(instance.o[j])]
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
        for k in range(instance.o[j]):
            variables = [f'z_{j}_{k}_{i}' for i in range(instance.g) if instance.p[j][k][i] > 0]
            coefficients = [1] * len(variables)
            constrs.append([variables, coefficients])
            senses.append('E')
            rhs.append(1)

    # constraint (2)
    for j in range(instance.n):
        for k in range(instance.o[j]):
            variables = [f'c_{j}_{k}']
            coefficients = [1]
            if k > 0:
                variables.append(f'c_{j}_{k - 1}')
                coefficients.append(-1)
            variables += [f'z_{j}_{k}_{i}' for i in range(instance.g) if instance.p[j][k][i] > 0]
            coefficients += [-instance.p[j][k][i] for i in range(instance.g) if instance.p[j][k][i] > 0]
            constrs.append([variables, coefficients])
            senses.append('G')
            rhs.append(0)

    # constraint (3)
    M = 100000
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for k1 in range(instance.o[j1]):
                for k2 in range(instance.o[j2]):
                    for i in range(instance.g):
                        if instance.p[j1][k1][i] > 0 and instance.p[j2][k2][i] > 0:
                            variables = [f'c_{j1}_{k1}', f'c_{j2}_{k2}', f'x_{j1}_{k1}_{j2}_{k2}', f'z_{j1}_{k1}_{i}', f'z_{j2}_{k2}_{i}']
                            coefficients = [1, -1, -M, -M, -M]
                            constrs.append([variables, coefficients])
                            senses.append('G')
                            rhs.append(-3 * M + instance.p[j1][k1][i])

    # constraint (4)
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for k1 in range(instance.o[j1]):
                for k2 in range(instance.o[j2]):
                    for i in range(instance.g):
                        if instance.p[j1][k1][i] > 0 and instance.p[j2][k2][i] > 0:
                            variables = [f'c_{j2}_{k2}', f'c_{j1}_{k1}', f'x_{j1}_{k1}_{j2}_{k2}', f'z_{j1}_{k1}_{i}', f'z_{j2}_{k2}_{i}']
                            coefficients = [1, -1, M, -M, -M]
                            constrs.append([variables, coefficients])
                            senses.append('G')
                            rhs.append(-2 * M + instance.p[j2][k2][i])

    # constraint (5)
    for j in range(instance.n):
        variables = ['Cmax', f'c_{j}_{instance.o[j] - 1}']
        coefficients = [1, -1]
        constrs.append([variables, coefficients])
        senses.append('G')
        rhs.append(0)

    # add variables
    all_names = z_names + x_names + c_names + Cmax_name
    all_objs = z_objs + x_objs + c_objs + Cmax_obj
    all_lbs = z_lbs + x_lbs + c_lbs + Cmax_lb
    all_ubs = z_ubs + x_ubs + c_ubs + Cmax_ub
    all_types = z_types + x_types + c_types + Cmax_type
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


def fjsp_mip_gurobi_model(file_path, threads=1, time_limit=3600):
    instance = parser(file_path)

    # create the model
    mdl = gp.Model()

    # variable z
    z_vars = {}
    for j in range(instance.n):
        for k in range(instance.o[j]):
            for i in range(instance.g):
                if instance.p[j][k][i] > 0:
                    z_vars[(j, k, i)] = mdl.addVar(vtype=GRB.BINARY, name=f'z_{j}_{k}_{i}')

    # variable x
    x_vars = {}
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for k1 in range(instance.o[j1]):
                for k2 in range(instance.o[j2]):
                    x_vars[(j1, k1, j2, k2)] = mdl.addVar(vtype=GRB.BINARY, name=f'x_{j1}_{k1}_{j2}_{k2}')

    # variable c
    c_vars = {}
    for j in range(instance.n):
        for k in range(instance.o[j]):
            c_vars[(j, k)] = mdl.addVar(vtype=GRB.CONTINUOUS, name=f'c_{j}_{k}', lb=0)

    # variable Cmax
    Cmax = mdl.addVar(vtype=GRB.CONTINUOUS, name='Cmax', lb=0)

    # constraint (1)
    for j in range(instance.n):
        for k in range(instance.o[j]):
            variables = [z_vars[(j, k, i)] for i in range(instance.g) if instance.p[j][k][i] > 0]
            mdl.addConstr(gp.quicksum(variables) == 1, name=f'constr1_{j}_{k}')

    # constraint (2)
    for j in range(instance.n):
        for k in range(instance.o[j]):
            variables = [c_vars[(j, k)]]
            coefficients = [1]
            if k > 0:
                variables.append(c_vars[(j, k - 1)])
                coefficients.append(-1)
            variables += [z_vars[(j, k, i)] for i in range(instance.g) if instance.p[j][k][i] > 0]
            coefficients += [-instance.p[j][k][i] for i in range(instance.g) if instance.p[j][k][i] > 0]
            mdl.addConstr(gp.quicksum(coefficients[i] * variables[i] for i in range(len(variables))) >= 0, name=f'constr2_{j}_{k}')

    # constraint (3)
    M = 100000
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for k1 in range(instance.o[j1]):
                for k2 in range(instance.o[j2]):
                    for i in range(instance.g):
                        if instance.p[j1][k1][i] > 0 and instance.p[j2][k2][i] > 0:
                            variables = [c_vars[(j1, k1)], c_vars[(j2, k2)], x_vars[(j1, k1, j2, k2)], z_vars[(j1, k1, i)], z_vars[(j2, k2, i)]]
                            coefficients = [1, -1, -M, -M, -M]
                            mdl.addConstr(gp.quicksum(coefficients[i] * variables[i] for i in range(len(variables))) >= instance.p[j1][k1][i] - 3 * M, name=f'constr3_{j1}_{k1}_{j2}_{k2}')

    # constraint (4)
    for j1 in range(instance.n - 1):
        for j2 in range(j1 + 1, instance.n):
            for k1 in range(instance.o[j1]):
                for k2 in range(instance.o[j2]):
                    for i in range(instance.g):
                        if instance.p[j1][k1][i] > 0 and instance.p[j2][k2][i] > 0:
                            variables = [c_vars[(j2, k2)], c_vars[(j1, k1)], x_vars[(j1, k1, j2, k2)], z_vars[(j1, k1, i)], z_vars[(j2, k2, i)]]
                            coefficients = [1, -1, M, -M, -M]
                            mdl.addConstr(gp.quicksum(coefficients[i] * variables[i] for i in range(len(variables))) >= instance.p[j2][k2][i] - 2 * M, name=f'constr4_{j1}_{k1}_{j2}_{k2}')

    # constraint (5)
    for j in range(instance.n):
        mdl.addConstr(Cmax >= c_vars[(j, instance.o[j] - 1)], name=f'constr5_{j}')

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


def fjsp_cp_model(file_path, threads=1, time_limit=3600, agent='local', execfile='/Applications/CPLEX_Studio1210/cpoptimizer/bin/x86-64_osx/cpoptimizer'):
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
        for k in range(instance.o[j]):
            tasks[j].append([])
            for i in range(instance.g):
                tasks[j][k].append(mdl.interval_var(name=f'tasks_{j}_{k}_{i}', optional=True, size=instance.p[j][k][i]))

    # constraint (2)
    _tasks = []
    for j in range(instance.n):
        _tasks.append([])
        for k in range(instance.o[j]):
            _tasks[j].append(mdl.interval_var(name=f'_tasks_{j}_{k}'))
    for j in range(instance.n):
        for k in range(instance.o[j]):
            mdl.add(mdl.alternative(_tasks[j][k], [tasks[j][k][i] for i in range(instance.g) if instance.p[j][k][i] > 0]))

    # constraint (3)
    for j in range(instance.n):
        for k in range(1, instance.o[j]):
            mdl.add(mdl.end_before_start(_tasks[j][k - 1], _tasks[j][k]))

    # constraint (4)
    for i in range(instance.g):
        task_list = []
        for j in range(instance.n):
            for k in range(instance.o[j]):
                if instance.p[j][k][i] > 0:
                    task_list.append(tasks[j][k][i])
        mdl.add(mdl.no_overlap(task_list))

    # constraint (5)
    mdl.add(mdl.minimize(mdl.max([mdl.end_of(_tasks[j][instance.o[j] - 1]) for j in range(instance.n)])))

    # solve the model
    result = mdl.solve(TimeLimit=time_limit, Workers=threads, LogVerbosity='Quiet', agent=agent, execfile=execfile)

    if result:
        print(f'Optimal objective value (CP Optimizer): {result.get_objective_value()}')
    else:
        print('No feasible solution found by CP Optimizer!')


if __name__ == '__main__':
    path = 'test cases/test cases/1.txt'
    print('-------------------------------CPLEX-------------------------------')
    fjsp_mip_cplex_model(path, threads=6)
    print('\n\n\n-------------------------------Gurobi-------------------------------')
    fjsp_mip_gurobi_model(path, threads=6)
    print('\n\n\n-------------------------------Constraint Programming------------------------------')
    fjsp_cp_model(path)
