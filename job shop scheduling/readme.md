### Job shop scheduling

The JSP involves assigning a set of jobs - each comprising a sequence of operations - to a set of machines. Each machine can only process one operation at a time, and the order of operations within each job must be respected. The goal is to minimize the makespan, which is the time at which all jobs have finished processing on all required machines.

#### MIP

##### Objective:

$$
\min \quad C_{max} \quad \textbf{(MIP-JSP)}
$$

##### Subject to:

$$
c_{j1} \geq P_{j1}, \quad \forall j \in \mathcal{J} \quad \textbf{(1)}
$$

$$
c_{ji} \geq c_{ji'} + P_{ji}, \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \quad \textbf{(2)}
$$

$$
c_{ji} \geq c_{j'i} + P_{ji} - M (1 - x_{ijj'}), \quad \forall i \in \mathcal{I}, j, j' \in \mathcal{J}: j > j' \quad \textbf{(3)}
$$

$$
c_{j'i} \geq c_{ji} + P_{j'i} - M \cdot x_{ijj'}, \forall i \in \mathcal{I}, j, j' \in \mathcal{J}: j > j' \quad \textbf{(4)}
$$

$$
C_{max} \geq c_{ji}, \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \quad \textbf{(5)}
$$

$$
c_{ji} \geq 0, \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \quad \textbf{(6)}
$$

$$
x_{ijj'} \in \{0, 1\}, \quad \forall i \in \mathcal{I}, j, j' \in \mathcal{J}: j > j' \quad \textbf{(7)}
$$

Constraint (1) ensures that the completion time of each job $j$ on the first machine is greater than the processing time on that machine. Constraint (2) respects the processing route of a job, and $i'$ denotes the stage before stage $i$ in job $j$. Constraints (3) and (4) enforce disjunctive constraints on the same machine $i$ such that job $j$ and job $j'$ do not overlap. Constraint (5) defines the makespan, which is the maximum completion time of all jobs on all stages. Constraints (6) and (7) define the nature of the decision variables.

#### CP

##### Objective:

$$
\min \quad C_{max} \quad \textbf{(CP-JSP)}
$$

##### Subject to:

$$
Task_{ji} = \text{IntervalVar}(P_{ji}), \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \quad \textbf{(1)}
$$

$$
\text{NoOverlap}(Task_{ji}: j \in \mathcal{J}), \quad \forall i \in \mathcal{I} \quad \textbf{(2)}
$$

$$
\text{EndBeforeStart}(Task_{ji}, Task_{ji'}), \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \quad \textbf{(3)}
$$

$$
C_{max} = \max_{j}(\text{EndOf}(Task_{j|\mathcal{I}|})) \quad \textbf{(4)}
$$

Constraint (1) define the interval variables, one for each job at each stage. Constraint (2) ensures that no two operations from different jobs can be processed on the same machine at the same time. Constraint (3) respects the processing route of a job, and $i'$ denotes the stage before stage $i$ in job $j$. Constraint (4) is the objective function that uses the "EndOf" over interval variables of jobs at the last stage $|\mathcal{I}|$. 
