### Flow shop scheduling

The (permutation or regular) FSP involves processing a set of jobs on multiple machines arranged in series. Each job must pass through the machines in the same order, and each machine can only handle one job at a time. The objective is typically minimize the makespan, which is the time required to complete all jobs.

#### MIP

##### Objective:

$$
\min \quad C_{max} \quad \textbf{(MIP-FSP)}
$$

##### Subject to:

$$
c_{j1} \geq P_{j1}, \quad \forall j \in \mathcal{J} \quad \textbf{(1)}
$$

$$
c_{ji} \geq c_{ji-1} + P_{ji}, \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \setminus \{1\} \quad \textbf{(2)}
$$

$$
c_{ji} \geq c_{j'i} + P_{ji} - M (1 - x_{jj'}), \quad \forall i \in \mathcal{I}, j, j' \in \mathcal{J}: j > j' \quad \textbf{(3)}
$$

$$
c_{j'i} \geq c_{ji} + P_{j'i} - M \cdot x_{jj'}, \quad \forall i \in \mathcal{I}, j, j' \in \mathcal{J}: j > j' \quad \textbf{(4)}
$$

$$
C_{max} \geq c_{ji}, \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \quad \textbf{(5)}
$$

$$
c_{ji} \geq 0, \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \quad \textbf{(6)}
$$

$$
x_{jj'} \in \{0, 1\}, \quad \forall j, j' \in \mathcal{J}: j > j' \quad \textbf{(7)}
$$

Constraint (1) ensures that the completion time of each job $j$ on the first machine is greater than its processing time on that machine. Constraint (2) indicates that the completion time of job $j$ at stages $i$ and $i - 1$ is at least as large as its processing time on machine $i$ plus the processing time on stage $i$. Constraints (3) and (4) ensure that no two operations for two jobs $j$ and $j'$ can be processed at the same machine at the same time. Constraint (5) calculates the makespan. Constraints (6) and (7) define the nature of the decision variables.

#### CP

##### Objective:

$$
\min \quad C_{max} \quad \textbf{(CP-FSP)}
$$

##### Subject to:

$$
Task_{ji} = \text{IntervalVar}(P_{ji}), \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \quad \textbf{(1)}
$$

$$
\text{EndBeforeStart}(Task_{ji}, Task_{ji-1}), \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \setminus \{1\} \quad \textbf{(2)}
$$

$$
SV_i = \text{SequenceVar}(Task_{ji}: j \in \mathcal{J}), \quad \forall i \in \mathcal{I} \quad \textbf{(3)}
$$

$$
\text{NoOverlap}(SV_i), \quad \forall i \in \mathcal{I} \quad \textbf{(4)}
$$

$$
\text{SameSequence}(SV_i, SV_{i - 1}), \quad \forall i \in \mathcal{I} \setminus \{1\} \quad \textbf{(5)}
$$

$$
C_{max} = \max_j (\text{EndOf}(Task_{j|\mathcal{I}|})) \quad \textbf{(6)}
$$

Constraint (1) defines the interval variable, one for each job at each stage. Constraint (2) indicates that the operations for the same job cannot be processed by more than one machine at a time. Constraint (4) indicates that machines cannot process more than one job at any time. To create the same sequence for all machines, we need to convert the interval variables into a sequence variable for each machine using Constraint (3) and limit the search to the same sequence using Constraint (5). Constraint (6) is the objective calculation that uses the function "EndOf" over interval variables of jobs at the last stage $|\mathcal{I}|$.
