### Flexible job shop scheduling

Flexible job shop scheduling problem (FJSP) extends the classical job shop problem by allowing each operation of a job to be processed on multiple possible machines, rather than a single dedicated one. The primary challenges in FJSP are:

- **Operation sequencing**: determining the order in which each job’s operations should occur.
- **Machine assignment**: deciding which eligible machine will process each operation.

The objective is typically to minimize the makespan, which is the time by which all operations across all jobs have been completed.

| Sets:           |                                                                          |
|-----------------|--------------------------------------------------------------------------|
| $\mathcal{K}_j$ | Set of operations of job $j$, with indices $k \in \mathcal{K}_j$         |
| $\mathcal{I}$   | Set of machines, with indices $i \in \mathcal{I}$                        |
| $\mathcal{I}_{jk}$ | Set of eligible machines for operation $O_{jk}$                       |

| **Parameters:** |                                                                          |
|-----------------|--------------------------------------------------------------------------|
| $P_{jki}$       | The processing time of operation $O_{jk}$ on machine $i$                 |

| **Sequencing decision:** |                                                                  |
|--------------------------|------------------------------------------------------------------|
| $x_{jkj'k'}$             | Equals 1 if the $k$-th operation of job $j$ is processed **after** the $k'$-th operation of job $j'$, and 0 otherwise (with $j > j'$) |

| **Scheduling decision:** |                                                                  |
|--------------------------|------------------------------------------------------------------|
| $c_{jk}$                 | Completion time of the $k$-th operation of job $j$               |

| **Assignment decision:** |                                                                  |
|--------------------------|------------------------------------------------------------------|
| $z_{jki}$                | Equals 1 if the $k$-th operation of job $j$ is processed by machine $i$, and 0 otherwise |

---

#### MIP

**Objective:**

$$
\min \; C_{\max} 
\quad (\text{MIP-FJSP})
$$

---

**(1)**  
$$
\sum_{i \in \mathcal{I}_{jk}} z_{jki} \;=\; 1,
\quad \forall j \in \mathcal{J},\; k \in \mathcal{K}_j
$$

**(2)**  
$$
c_{jk} \;\ge\; c_{j,k-1} \;+\; \sum_{i \in \mathcal{I}_{jk}} P_{jki}\, z_{jki},
\quad \forall j \in \mathcal{J},\; k \in \mathcal{K}_j
$$

**(3)**  
$$
c_{jk} \;\ge\; c_{j'k'} \;+\; P_{jki}
\;-\; M\bigl(3 - x_{jkj'k'} \;-\; z_{jki} \;-\; z_{j'k'i}\bigr),
\quad \forall j > j' \in \mathcal{J},\;
k \in \mathcal{K}_j,\; k' \in \mathcal{K}_{j'},\;
i \in \mathcal{I}_{jk} \cap \mathcal{I}_{j'k'}
$$

**(4)**  
$$
c_{j'k'} \;\ge\; c_{jk} \;+\; P_{j'k'i}
\;-\; M\bigl(2 + x_{jkj'k'} \;-\; z_{jki} \;-\; z_{j'k'i}\bigr),
\quad \forall j > j' \in \mathcal{J},\;
k \in \mathcal{K}_j,\; k' \in \mathcal{K}_{j'},\;
i \in \mathcal{I}_{jk} \cap \mathcal{I}_{j'k'}
$$

**(5)**  
$$
C_{\max} \;\ge\; c_{jk}, 
\quad \forall j \in \mathcal{J},\; k \in \mathcal{K}_j
$$

**(6)**  
$$
c_{jk} \;\ge\; 0, 
\quad \forall j \in \mathcal{J},\; k \in \mathcal{K}_j
$$

**(7)**  
$$
x_{jkj'k'} \in \{0,1\}, \quad
z_{jki} \in \{0,1\},
\quad \forall j > j' \in \mathcal{J},\;
k \in \mathcal{K}_j,\; k' \in \mathcal{K}_{j'},\;
i \in \mathcal{I}
$$

- **Constraint (1)** assigns each operation to exactly one eligible machine.  
- **Constraint (2)** ensures sequential processing of operations within each job (no overlap among a job’s own operations).  
- **Constraints (3) and (4)** ensure that operations of different jobs assigned to the same machine will not overlap (disjunctive constraints).  
- **Constraint (5)** defines the makespan, which is the maximum completion time across all operations.  
- **Constraints (6) and (7)** define variable domains and non-negativity/binary requirements.

---

#### CP

**Objective:**

$$
\min \; C_{\max}
\quad (\text{CP-FJSP})
$$

---

**(1)**  
```text
Task_{jki} = IntervalVar(P_{jki}, Optional), 
for all j in J, k in K_j, i in I_{jk}
