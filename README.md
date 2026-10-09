# Topic 15 — Adaptive Planning Assessment

## Project Overview

This project implements an adaptive planning system that changes its planning strategy based on recent task performance. It compares a low-cost `fast` strategy with a higher-cost, higher-reliability `careful` strategy, tracks a rolling success window, switches strategies when performance falls below a threshold, compares fixed and adaptive planners, and prevents rapid strategy flip-flopping with a cooldown.

**Project:** Adaptive Planning Assessment  

## Objectives

- Define planning strategies with explicit cost and skill trade-offs.
- Track recent task outcomes using a bounded rolling window.
- Calculate rolling success rates.
- Adapt strategy selection when performance degrades.
- Compare fixed and adaptive planning across five deterministic seeds.
- Prevent rapid switching with a minimum 10-step cooldown.
- Keep behavior deterministic and testable.
- Produce traceable evidence for the assessment.

## Strategy Design

| Strategy | Cost | Skill |
|---|---:|---:|
| `fast` | 1 | 0.45 |
| `careful` | 3 | 0.90 |

The `fast` strategy is cheaper but less reliable. The `careful` strategy costs more but has substantially higher skill.

## Task 1 — Define Strategies

Two validated immutable strategy records are defined, with explicit cost and skill trade-offs.

**Result: 20/20 — PASS**

## Task 2 — Track Rolling Results

The planner maintains a configurable rolling window, defaulting to four results. Only the most recent results are retained, and the rolling success rate is calculated from that window. Switching cannot occur before the window is full.

**Result: 20/20 — PASS**

## Task 3 — Implement Strategy Switching

The planner starts with `fast`. After the rolling window is full, it switches from `fast` to `careful` when the success rate is strictly below `0.5`. An exact rate of `0.5` does not trigger a switch. Switch steps are recorded.

**Result: 20/20 — PASS**

## Task 4 — Compare Fixed vs Adaptive Planners

The workload was five easy tasks followed by fifteen hard tasks:

`[0.1] × 5 + [0.9] × 15`

Five deterministic seeds produced:

| Seed | Fixed Wins | Adaptive Wins | Fixed Cost | Adaptive Cost | Adaptive Switches |
|---:|---:|---:|---:|---:|---|
| 1 | 8 | 13 | 20 | 44 | [8] |
| 2 | 5 | 13 | 20 | 46 | [7] |
| 3 | 10 | 15 | 20 | 34 | [13] |
| 4 | 11 | 16 | 20 | 44 | [8, 20] |
| 5 | 7 | 12 | 20 | 42 | [4, 15] |
| **Total** | **41** | **69** | **100** | **210** | — |

The adaptive planner achieved 69 wins versus 41 for the fixed planner, an improvement of 28 wins, while using more resources because it selected the higher-cost strategy when needed.

**Result: 20/20 — PASS**

## Task 5 — Prevent Flip-Flopping

A default 10-step cooldown prevents rapid strategy switching. After a switch, another switch cannot occur until at least ten steps have elapsed. The implementation records switch steps and tests verify the minimum gap.

**Result: 20/20 — PASS**

## Testing

The cumulative focused test suite passed completely:

```text
54 passed in 0.20s
```

Test progression:

```text
Task 1 cumulative: 10 passed
Task 2 cumulative: 23 passed
Task 3 cumulative: 33 passed
Task 4 cumulative: 43 passed
Task 5 cumulative: 54 passed
```

## Evidence

The five-seed comparison evidence is:

```text
Fixed:
  Wins = 41
  Cost = 100

Adaptive:
  Wins = 69
  Cost = 210
```

The results demonstrate the intended adaptive-planning cost/performance trade-off.

## Assessment Result

| Task | Marks | Status |
|---|---:|---|
| Task 1 — Define Strategies | 20/20 | PASS |
| Task 2 — Track Rolling Results | 20/20 | PASS |
| Task 3 — Implement Switching | 20/20 | PASS |
| Task 4 — Compare Fixed vs Adaptive | 20/20 | PASS |
| Task 5 — Prevent Flip-Flopping | 20/20 | PASS |
| **Core Total** | **100/100** | **PASS** |

The optional +5 stretch task was not implemented.

## Reflection

This activity helped me understand adaptive planning as a practical decision-making mechanism rather than simply choosing the most powerful strategy for every task. The project starts with two strategies that deliberately have different cost and reliability characteristics. The fast strategy is inexpensive but less capable, while the careful strategy costs more and provides higher reliability. This trade-off makes it possible for an agent to spend resources only when the workload justifies doing so.

The rolling-window implementation was particularly useful because it prevents the planner from reacting to one isolated result. By considering a fixed number of recent outcomes, the planner gets a more stable view of current performance. Requiring the window to be full before switching also prevents premature decisions based on insufficient evidence.

The comparison across five deterministic seeds demonstrated the practical value of adaptation. The adaptive planner achieved 69 total wins compared with 41 for the fixed fast planner, although it used more resources. This showed me that adaptive systems should not be evaluated only by cost or only by success rate; both dimensions need to be considered together.

The cooldown mechanism was another important lesson. Without a cooldown, a planner could repeatedly change strategies when results fluctuate around decision thresholds. This kind of flip-flopping can create unnecessary overhead and unstable behavior. Requiring at least ten steps between switches provides a simple but effective form of hysteresis.

Overall, this project improved my understanding of rolling metrics, threshold-based decisions, deterministic simulation, cost-performance trade-offs, and stability controls. These concepts are useful for AI agents that need to adapt their behavior while remaining predictable, bounded, and testable.
