### Non-permutation flow shop scheduling

The non-permutation flow shop scheduling problem (N-FSP) extends the traditional flow shop environment by allowing each machine to arrange jobs in its own order. As in the permutation flow shop setting, a set of jobs passes sequentially through multiple machines, each capable of handling only one job at a time. However, unlike in a permutation flow shop, the sequence of N-FSP on one machine need not match the sequence on another. The objective is often to minimize the makespan, which is the time by which all jobs have completed processing on all required machines.

#### MIP

##### Objective:

$$
\min \quad C_{max} \quad \textbf{MIP-NFSP}
$$

##### Subject to:

$$
c_{j1} \geq P_{j1}, \quad \forall j \in \mathcal{J} \quad \textbf{(1)}
$$

$$
c_{ji} \geq c_{ji - 1} + P_{ji}, \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \setminus \{1\} \quad \textbf{(2)}
$$

$$
c_{ji} \geq c_{j'i} + P_{ji} - M (1 - x_{ijj'}), \quad \forall i \in \mathcal{I}, j, j' \in \mathcal{J}: j > j' \quad \textbf{(3)}
$$

$$
c_{j'i} \geq c_{ji} + P_{j'i} - M \cdot x_{ijj'}, \quad \forall i \in \mathcal{I}, j, j' \in \mathcal{J}: j > j' \quad \textbf{(4)}
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

Constraint (1) ensures that the completion time of each job $j$ on the first machine is greater than its processing time on the machine. Constraint (2) indicates the completion time of job $j$ on different machines. Constraints (3) and (4) ensure that no two operations for two jobs $j$ and $j'$ can be processed at the same machine at the same time. Constraint (5) calculates the makespan. Constraints (6) and (7) define the nature of decision variables.

#### CP

##### Objective:

$$
\min \quad C_{max} \quad \textbf{(CP-NFSP)}
$$

##### Subject to:

$$
Task_{ji} = \text{IntervalVar}(P_{ji}), \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \quad \textbf{(1)}
$$

$$
\text{EndBeforeStart}(Task_{ji}, Task_{ji-1}), \quad \forall j \in \mathcal{J}, i \in \mathcal{I} \setminus \{1\} \quad \textbf{(2)}
$$

$$
\text{NoOverlap}(Task_{ji}: j \in \mathcal{J}), \quad \forall i \in \mathcal{I} \quad \textbf{(3)}
$$

$$
C_{max} = \max_j (\text{EndOf}(Task_{j|\mathcal{I}|})) \quad \textbf{(4)}
$$

Constraint (1) defines the interval variable, one for each job at each stage. Constraint (2) ensures that for job $j$, stage $i$ must start only after stage $i - 1$ has finished. Constraint (3) indicates that machines cannot process more than one job at any time. Constraint (4) is the objective calculation that uses the function "EndOf" over interval variables of jobs at the last stage $|\mathcal{I}|$.
