from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.adaptive_planning import run


DIFFICULTIES = [0.1] * 5 + [0.9] * 15


def main():
    print("=" * 70)
    print("Topic 15 — Fixed vs Adaptive Planner Comparison")
    print("=" * 70)

    print("\nWorkload:")
    print("5 easy tasks + 15 hard tasks")

    print("\nFive-seed comparison:")

    fixed_results = []
    adaptive_results = []

    for seed in range(1, 6):
        fixed = run(
            DIFFICULTIES,
            adaptive=False,
            seed=seed,
        )

        adaptive = run(
            DIFFICULTIES,
            adaptive=True,
            seed=seed,
        )

        fixed_results.append(fixed)
        adaptive_results.append(adaptive)

        print(f"\nSeed {seed}")
        print("fixed fast:", fixed)
        print("adaptive:  ", adaptive)

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    fixed_wins = sum(
        result["wins"]
        for result in fixed_results
    )

    fixed_cost = sum(
        result["cost"]
        for result in fixed_results
    )

    adaptive_wins = sum(
        result["wins"]
        for result in adaptive_results
    )

    adaptive_cost = sum(
        result["cost"]
        for result in adaptive_results
    )

    print(
        "Fixed total wins:",
        fixed_wins,
    )

    print(
        "Fixed total cost:",
        fixed_cost,
    )

    print(
        "Adaptive total wins:",
        adaptive_wins,
    )

    print(
        "Adaptive total cost:",
        adaptive_cost,
    )

    print("\nComparison completed successfully.")


if __name__ == "__main__":
    main()