import cplex
import gurobipy as gp
from gurobipy import GRB
from docplex.cp.model import CpoModel


class SDST_FSP:
    def __init__(self):
        self.n = 0  # the number of jobs
        self.g = 0  # the number of machines
        self.p = []  # the set of processing times
        self.s = []  # the set of setup times


def parser(file_path):
    instance = SDST_FSP()
    with open(file_path, 'r') as f:
        instance.n = int(f.readline().strip().split()[0])
        instance.g = int(f.readline().strip().split()[0])
        for _ in range(instance.n):
            instance.p.append([int(x) for x in f.readline().strip().split()])
        for i in range(instance.g):
            instance.s.append([])
            for j in range(instance.n):
                instance.s[i].append([int(x) for x in f.readline().strip().split()])
    return instance


def sdst_fsp_mip_cplex_model(file_path, threads=1, time_limit=3600):
    instance = parser(file_path)

    # create the model
    mdl = cplex.Cplex()

    # variable z
    z_names = [f'z_{j1}_{j2}' for j1 in range(1, instance.n + 1) for j2 in range(instance.n + 1) if j1 != j2]
    z_objs = [0] * len(z_names)
    z_lbs = [0] * len(z_names)
    z_ubs = [1] * len(z_names)
    z_types = ['B'] * len(z_names)

    # variable c
    c_names = [f'c_{j}_{i}' for j in range(instance.n + 1) for i in range(instance.g)]
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
    for j1 in range(1, instance.n + 1):
        variables = [f'z_{j1}_{j2}' for j2 in range(instance.n + 1) if j1 != j2]
        coefficients = [1] * len(variables)
        constrs.append([variables, coefficients])
        senses.append('E')
        rhs.append(1)

    # constraint (2)
    for j2 in range(1, instance.n + 1):
        variables = [f'z_{j1}_{j2}' for j1 in range(1, instance.n + 1) if j1 != j2]
        coefficients = [1] * len(variables)
        constrs.append([variables, coefficients])
        senses.append('L')
        rhs.append(1)

    # constraint (3)
    variables = [f'z_{j}_{0}' for j in range(1, instance.n + 1)]
    coefficients = [1] * instance.n
    constrs.append([variables, coefficients])
    senses.append('E')
    rhs.append(1)

    # constraint (4)
    for j in range(1, instance.n + 1):
        for i in range(1, instance.g):
            variables = [f'c_{j}_{i}', f'c_{j}_{i - 1}']
            coefficients = [1, -1]
            constrs.append([variables, coefficients])
            senses.append('G')
            rhs.append(instance.p[j - 1][i])

    # constraint (5)
    M = 100000
    for j1 in range(1, instance.n + 1):
        for j2 in range(instance.n + 1):
            if j1 != j2:
                for i in range(instance.g):
                    variables = [f'c_{j1}_{i}', f'c_{j2}_{i}', f'z_{j1}_{j2}']
                    coefficients = [1, -1, -M]
                    constrs.append([variables, coefficients])
                    senses.append('G')
                    if j2 == 0:
                        rhs.append(instance.p[j1 - 1][i] - M)
                    else:
                        rhs.append(instance.p[j1 - 1][i] + instance.s[i][j2 - 1][j1 - 1] - M)

    # constraint (6)
    for j in range(1, instance.n + 1):
        variables = ['Cmax', f'c_{j}_{instance.g - 1}']
        coefficients = [1, -1]
        constrs.append([variables, coefficients])
        senses.append('G')
        rhs.append(0)

    # add variables
    all_names = z_names + c_names + Cmax_name
    all_objs = z_objs + c_objs + Cmax_obj
    all_lbs = z_lbs + c_lbs + Cmax_lb
    all_ubs = z_ubs + c_ubs + Cmax_ub
    all_types = z_types + c_types + Cmax_type
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


def sdst_fsp_mip_gurobi_model(file_path, threads=1, time_limit=3600):
    instance = parser(file_path)

    # create the model
    mdl = gp.Model()

    # variable z
    z_vars = {}
    for j1 in range(1, instance.n + 1):
        for j2 in range(instance.n + 1):
            if j1 != j2:
                z_vars[(j1, j2)] = mdl.addVar(vtype=GRB.BINARY, name=f'z_{j1}_{j2}')

    # variable c
    c_vars = {}
    for j in range(instance.n + 1):
        for i in range(instance.g):
            c_vars[(j, i)] = mdl.addVar(vtype=GRB.CONTINUOUS, name=f'c_{j}_{i}', lb=0)

    # variable Cmax
    Cmax = mdl.addVar(vtype=GRB.CONTINUOUS, name='Cmax', lb=0)

    # constraint (1)
    for j1 in range(1, instance.n + 1):
        mdl.addConstr(gp.quicksum(z_vars[(j1, j2)] for j2 in range(instance.n + 1) if j1 != j2) == 1, name=f'constr1_{j1}')

    # constraint (2)
    for j2 in range(1, instance.n + 1):
        mdl.addConstr(gp.quicksum(z_vars[(j1, j2)] for j1 in range(1, instance.n + 1) if j1 != j2) <= 1, name=f'constr2_{j2}')

    # constraint (3)
    mdl.addConstr(gp.quicksum(z_vars[(j1, 0)] for j1 in range(1, instance.n + 1)) == 1, name='constr3')

    # constraint (4)
    for j in range(1, instance.n + 1):
        for i in range(1, instance.g):
            mdl.addConstr(c_vars[(j, i)] >= c_vars[(j, i - 1)] + instance.p[j - 1][i], name=f'constr4_{j - 1}_{i}')

    # constraint (5)
    M = 100000
    for j1 in range(1, instance.n + 1):
        for j2 in range(instance.n + 1):
            if j1 != j2:
                for i in range(instance.g):
                    if j2 == 0:
                        mdl.addConstr(c_vars[(j1, i)] >= c_vars[(j2, i)] + instance.p[j1 - 1][i] - M * (1 - z_vars[(j1, j2)]), name=f'constr5_{i}_{j1}_{j2}')
                    else:
                        mdl.addConstr(c_vars[(j1, i)] >= c_vars[(j2, i)] + instance.p[j1 - 1][i] + instance.s[i][j2 - 1][j1 - 1] - M * (1 - z_vars[(j1, j2)]), name=f'constr5_{i}_{j1}_{j2}')

    # constraint (6)
    for j in range(1, instance.n + 1):
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


def sdst_fsp_cp_model(file_path, threads=1, time_limit=3600, agent='local', execfile='/Applications/CPLEX_Studio1210/cpoptimizer/bin/x86-64_osx/cpoptimizer'):
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
            tasks[j].append(mdl.interval_var(name=f'task_{j}_{i}', size=instance.p[j][i]))

    # constraint (2)
    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.add(mdl.end_before_start(tasks[j][i - 1], tasks[j][i]))

    # constraint (3)
    sequence_variables = []
    for i in range(instance.g):
        sequence_variables.append(mdl.sequence_var([tasks[j][i] for j in range(instance.n)]))

    # constraint (4)
    for i in range(instance.g):
        mdl.add(mdl.no_overlap(sequence_variables[i], instance.s[i]))

    # constraint (5)
    for i in range(instance.g - 1):
        mdl.add(mdl.same_sequence(sequence_variables[i - 1], sequence_variables[i]))

    # constraint (6)
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
    sdst_fsp_mip_cplex_model(path, threads=6)
    print('\n\n\n-------------------------------Gurobi-------------------------------')
    sdst_fsp_mip_gurobi_model(path, threads=6)
    print('\n\n\n-------------------------------Constraint Programming------------------------------')
    sdst_fsp_cp_model(path)
