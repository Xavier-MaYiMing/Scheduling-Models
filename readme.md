## Description

This repository provides Mixed Integer Programming (MIP) and Constraint Programming (CP) models for various scheduling problems, including flow shop and job shop scheduling. For each problem, we offer:

- A problem description
- MIP and CP models
- Corresponding Python codes using **CPLEX** and **Gurobi**

We plan to gradually update this repository with more scheduling problems over time.

### Constraint programming overview

In CP, we introduce **interval variables**, each representing an interval of time during which a job is processed. The start and end times of an interval variable (within a larger interval $[\alpha, \beta)$) are decision variables. Formally, an interval variable $ x $ has a domain of: $\{[\alpha, \beta) \mid \alpha, \beta \in \mathbb{Z}, \alpha \leq \beta\}$ where $ s $ and $ e $ are the start and end points of the interval, and $ l = e - s $ denotes its length. Interval variables can also be **optional**, meaning part of the solution involves deciding whether an interval is present at all. In this case, the domain expands to: $\{\perp\} \cup \{[\alpha, \beta) \mid \alpha, \beta \in \mathbb{Z}, \alpha \leq \beta\}$, where $ x = \{\perp\} $ means the interval is absent, and $ x = [s, e) $ means it is present.

**Functions used in the CP models**

| Global constraints |                                                              |
| ------------------ | ------------------------------------------------------------ |
| EndBeforeStart     | It constrains minimum delay between the end of one interval variable and start of another one. |
| EndAtStart         | It constrains the delay between the end of one interval variable and start of another one. |
| Alternative        | It creates an alternative constraint between interval variables. |
| NoOverlap          | It constraints a set of interval variables not to overlap each other. |
| SameSequence       | It creates a same-sequence constraint between two sequence variables. |
| **Functions**      |                                                              |
| EndOf              | It returns the end of an interval variable.                  |
| Pulse              | It returs an interval variable (or a fixed interval) whose value is equal to 0 outside the interval and equal to a nonnegative constant on the interval. |
| Element            | It returns an element of an array.                           |
| PresenceOf         | It returns the presence status of an interval variable.      |

**Sets and variables used in models**

| Sets            |                                                              |
| --------------- | ------------------------------------------------------------ |
| $\mathcal{J}$   | Sets of jobs, $j \in \mathcal{J}$                            |
| $\mathcal{I}$   | Set of stages, $i \in \mathcal{I}$                           |
| $\mathcal{F}$   | Set of factories, $f \in \mathcal{F}$                        |
| $\mathcal{M}_i$ | Set of machines at stage $i$, $k \in \mathcal{M}_i$          |
| **Parameters**  |                                                              |
| $D_j$           | Due data of job $j$                                          |
| $P_{ji}$        | Processing time of job $j$ on machine $i$                    |
| $S_{jj'i}$      | Setup time of job $j$ after job $j'$ on machine $i$          |
| **Sequencing**  |                                                              |
| $x_{jj'}$       | 1 if job $j$ is processed after job $j'$, 0 otherwise $(j > j')$ |
| $x_{ijj'}$      | 1 if machine $i$ processes job $j$ after job $j'$, 0 otherwise $(j > j')$ |
| $h_{jii'}$      | 1 if for job $j$ visits machine $i$ after machine $i'$, 0 otherwise $(i > i')$ |
| $z_{jj'}$       | 1 if job $j$ is processed immediately after job $j'$, 0 otherwise $(j \neq j')$ |
| **Scheduling**  |                                                              |
| $c_{ji}$        | Completion time of job $j$ on machine $i$                    |
| $t_j$           | Tardiness of job $j$                                         |
| $C_{max}$       | Makespan                                                     |
| **Assignment**  |                                                              |
| $w_{jik}$       | 1 if job $j$ is assigned to machine $k$ at stage $i$, 0 otherwise |
| $y_{jk}$        | 1 if job $j$ is assigned to machine $k$, 0 otherwise         |
| $q_{jf}$        | 1 if job $j$ is assigned to factory $f$, 0 otherwise         |

### Contributing

Contributions, suggestions, and bug reports are welcome. If you have ideas for additional scheduling problems or improvements, feel free to open an issue or submit a pull request.

---

**Thank you for visiting our repository!** We hope our collection of MIP and CP models for scheduling problems will be useful in your research or practice. Stay tuned for more updates.
