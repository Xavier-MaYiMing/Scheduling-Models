### Flexible job shop scheduling

Flexible fob shop scheduling problem (FJSP) extends the classical job shop problem by allowing each operation of a job to be processed on multiple possible machines, rather than a single dedicated one. The primary challenges in FJSP are:

 * Operation sequencing: determining the order in which each job’s operations should occur.
 * Machine assignment: deciding which eligible machine will process each operation.

The objective is typically to minimize the makespan, which is the time by which all operations across all jobs have been completed.

| Sets:                    |                                                              |
| ------------------------ | ------------------------------------------------------------ |
| $\mathcal{K}_j$          | Sets of operations of job $j$, $k \in \mathcal{K}_j$         |
| $\mathcal{I}$            | Set of machines, $i \in \mathcal{I}$                         |
| $\mathcal{I}_{jk}$       | Set of eligible machines for operation $O_{jk}$              |
| **Parameters:**          |                                                              |
| $P_{jki}$                | The processing time of operation $O_{jk}$ on machine $i$     |
| **Sequencing decision:** |                                                              |
| $x_{jkj'k'}$             | 1 if the $k$th operation of job $j$ is processed after the $k'$th operation of job $k'$, 0 otherwise ($j > j'$) |
| **Scheduling decision:** |                                                              |
| $c_{jk}$                 | The completion time of the $k$th operation of job $j$        |
| **Assignment decision:** |                                                              |
| $z_{jki}$                | 1 if the $k$th operation of job $j$ is processed by mahcine $i$, 0 otherwise |

#### MIP

##### Objective: 

$$
\min \quad C_{max} \quad \textbf{(MIP-FJSP)}
$$

##### Subject to:

$$
\sum_{i \in \mathcal{I_{jk}}} z_{jki} = 1, \quad \forall j \in \mathcal{J}, k \in \mathcal{K_j} \quad \textbf{(1)}
$$

$$
c_{jk} \geq c_{j k - 1} + \sum_{i \in \mathcal{I}_{jk}} P_{jki} z_{jki}, \quad \forall j \in \mathcal{J}, k \in \mathcal{K}_j \quad \textbf{(2)}
$$

$$
c_{jk} \geq c_{j'k'} + P_{jki} - M (3 - x_{jkj'k'} - z_{jki} - z_{j'k'i}), \quad \forall j > j' \in \mathcal{J}, k \in \mathcal{K}_j, k' \in \mathcal{K}_{j'}, i \in \mathcal{I}_{jk} \cap \mathcal{I}_{j'k'} \quad \textbf{(3)}
$$

$$
c_{j'k'} \geq c_{jk} + P_{j'k'i} - M (2 + x_{jkj'k'} - z_{jki} - z_{j'k'i}), \quad \forall j > j' \in \mathcal{J}, k \in \mathcal{K}_j, k' \in \mathcal{K}_{j'}, i \in \mathcal{I}_{jk} \cap \mathcal{I}_{j'k'} \quad \textbf{(4)}
$$

$$
C_{max} \geq c_{jk}, \quad \forall j \in \mathcal{J}, k \in \mathcal{K}_j \quad \textbf{(5)}
$$

$$
c_{jk} \geq 0, \quad \forall j \in J, k \in \mathcal{I}_j \quad \textbf{(6)}
$$

$$
x_{jkj'k'}, z_{jki} \in \{0, 1\}, \quad \forall j > j' \in \mathcal{J}, k \in \mathcal{K}_j, k' \in \mathcal{K}_{j'}, i \in \mathcal{I} \quad \textbf{(7)}
$$

Constraint (1) assigns each operation to an eligible machine. Constraint (2) ensure that there is no overlap in the starting times of operations of a job. Constraints (3) and (4) ensure that operations of different jobs assigned to the same machine will not overlap. Constraint (5) defines the makespan, which is the maximum completion time of each machine. Constraints (6) and (7) define the nature of decision variables.

#### CP

##### Objective:

$$
\min \quad C_{max} \quad \textbf{(CP-FJSP)}
$$

##### Subject to:

$$
Task_{jki} = \text{IntervalVar}(P_{jki}, \text{Optional}), \quad \forall j \in \mathcal{J}, k \in \mathcal{K}_j, i \in \mathcal{I}_{jk} \quad \textbf{(1)}
$$

$$
\text{Alternative}(Task_{jk}^*, \{Task_{jki}: i \in \mathcal{I}_{jk}\}), \quad \forall j \in \mathcal{J}, k \in \mathcal{K}_j \quad \textbf{(2)}
$$

$$
\text{EndBeforeStart}(Task_{jk}^*, Task_{jk-1}^*), \quad \forall j \in \mathcal{J}, k \in \mathcal{K}_j \quad \textbf{(3)}
$$

$$
\text{NoOverlap}(Task_{jik}: j \in \mathcal{J}, k \in \mathcal{K}_j \mid i \in \mathcal{I}_{jk}), \quad \forall i \in \mathcal{I} \quad \textbf{(4)}
$$

$$
C_{max} = \max_{j \in \mathcal{J}}(\text{EndOf}(Task_{j|\mathcal{K}_j|}^*)) \quad \textbf{(5)}
$$

Constraint (1) defines interval variables, one for each operation of a job on each eligible machine. Constraint (2) ensures each operation for each job selects exactly one eligible machine. Constraint (3) ensures that operation $k$ starts after operation $k - 1$ is completed for each job $j$. Constraint (4) ensures no more than one operation can be processed on a machine at a time. Constraint (5) calculates the makespan.
