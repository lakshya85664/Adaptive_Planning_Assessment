import pytest

from src.adaptive_planning import (
    STRATEGIES,
    Strategy,
    get_strategy,
    random
)


def test_task1_fast_strategy_exists():
    assert "fast" in STRATEGIES


def test_task1_careful_strategy_exists():
    assert "careful" in STRATEGIES


def test_task1_fast_strategy_values():
    strategy = STRATEGIES["fast"]

    assert isinstance(strategy, Strategy)
    assert strategy.cost == 1
    assert strategy.skill == 0.45


def test_task1_careful_strategy_values():
    strategy = STRATEGIES["careful"]

    assert isinstance(strategy, Strategy)
    assert strategy.cost == 3
    assert strategy.skill == 0.90


def test_task1_careful_is_more_reliable_than_fast():
    assert (
        STRATEGIES["careful"].skill
        > STRATEGIES["fast"].skill
    )


def test_task1_fast_is_cheaper_than_careful():
    assert (
        STRATEGIES["fast"].cost
        < STRATEGIES["careful"].cost
    )


def test_task1_get_strategy_returns_correct_strategy():
    assert get_strategy("fast") == STRATEGIES["fast"]
    assert get_strategy("careful") == STRATEGIES["careful"]


def test_task1_unknown_strategy_is_rejected():
    with pytest.raises(
        ValueError,
        match="unknown strategy",
    ):
        get_strategy("unknown")


def test_task1_invalid_strategy_type_is_rejected():
    with pytest.raises(
        TypeError,
        match="strategy name must be a string",
    ):
        get_strategy(123)


def test_task1_strategies_have_distinct_tradeoff():
    fast = STRATEGIES["fast"]
    careful = STRATEGIES["careful"]

    assert fast.cost < careful.cost
    assert fast.skill < careful.skill

# ============================================================
# Task 2 — Track rolling results
# ============================================================

from src.adaptive_planning import AdaptivePlanner


def test_task2_default_window_is_four():
    planner = AdaptivePlanner()

    assert planner.window == 4


def test_task2_custom_window_is_supported():
    planner = AdaptivePlanner(window=3)

    assert planner.window == 3


def test_task2_recent_results_are_recorded():
    planner = AdaptivePlanner(window=4)

    planner.record(True)
    planner.record(False)

    assert planner.recent == [True, False]


def test_task2_success_rate_is_computed():
    planner = AdaptivePlanner(window=4)

    planner.record(True)
    planner.record(True)
    planner.record(False)
    planner.record(False)

    assert planner.success_rate == 0.5


def test_task2_all_successes_have_rate_one():
    planner = AdaptivePlanner(window=4)

    for _ in range(4):
        planner.record(True)

    assert planner.success_rate == 1.0


def test_task2_all_failures_have_rate_zero():
    planner = AdaptivePlanner(window=4)

    for _ in range(4):
        planner.record(False)

    assert planner.success_rate == 0.0


def test_task2_window_discards_oldest_result():
    planner = AdaptivePlanner(window=3)

    planner.record(True)
    planner.record(False)
    planner.record(False)
    planner.record(True)

    assert planner.recent == [False, False, True]


def test_task2_window_never_exceeds_configured_size():
    planner = AdaptivePlanner(window=3)

    for result in [
        True,
        False,
        True,
        False,
        True,
        False,
    ]:
        planner.record(result)

    assert len(planner.recent) == 3


def test_task2_window_full_only_after_n_results():
    planner = AdaptivePlanner(window=4)

    assert planner.window_full is False

    planner.record(True)
    planner.record(True)
    planner.record(True)

    assert planner.window_full is False

    planner.record(True)

    assert planner.window_full is True


def test_task2_empty_window_rate_is_zero():
    planner = AdaptivePlanner(window=4)

    assert planner.success_rate == 0.0


def test_task2_invalid_window_is_rejected():
    with pytest.raises(
        ValueError,
        match="window must be at least 1",
    ):
        AdaptivePlanner(window=0)


def test_task2_invalid_window_type_is_rejected():
    with pytest.raises(
        TypeError,
        match="window must be an integer",
    ):
        AdaptivePlanner(window="4")


def test_task2_invalid_result_is_rejected():
    planner = AdaptivePlanner(window=4)

    with pytest.raises(
        TypeError,
        match="success must be a boolean",
    ):
        planner.record("success")

# ============================================================
# Task 3 — Implement switching
# ============================================================

def test_task3_starts_with_fast_strategy():
    planner = AdaptivePlanner()

    assert planner.current == "fast"


def test_task3_does_not_switch_before_window_is_full():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
    )

    planner.record(False, step=1)
    planner.record(False, step=2)
    planner.record(False, step=3)

    assert planner.current == "fast"
    assert planner.switches == []


def test_task3_switches_after_full_window_below_threshold():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
    )

    planner.record(True, step=1)
    planner.record(False, step=2)
    planner.record(False, step=3)
    planner.record(False, step=4)

    assert planner.success_rate == 0.25
    assert planner.current == "careful"
    assert planner.switches == [4]


def test_task3_exact_threshold_does_not_switch():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
    )

    planner.record(True, step=1)
    planner.record(True, step=2)
    planner.record(False, step=3)
    planner.record(False, step=4)

    assert planner.success_rate == 0.5
    assert planner.current == "fast"
    assert planner.switches == []


def test_task3_high_success_rate_does_not_switch():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
    )

    planner.record(True, step=1)
    planner.record(True, step=2)
    planner.record(True, step=3)
    planner.record(False, step=4)

    assert planner.success_rate == 0.75
    assert planner.current == "fast"


def test_task3_switch_step_is_recorded():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
    )

    for step in range(1, 5):
        planner.record(False, step=step)

    assert planner.switches == [4]


def test_task3_switches_only_from_fast_to_careful():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
    )

    for step in range(1, 5):
        planner.record(False, step=step)

    assert planner.current == "careful"

    for step in range(5, 9):
        planner.record(False, step=step)

    assert planner.current == "careful"
    assert planner.switches == [4]


def test_task3_invalid_threshold_is_rejected():
    with pytest.raises(
        ValueError,
        match="switch_below must be between 0 and 1",
    ):
        AdaptivePlanner(
            switch_below=1.5
        )


def test_task3_invalid_threshold_type_is_rejected():
    with pytest.raises(
        TypeError,
        match="switch_below must be numeric",
    ):
        AdaptivePlanner(
            switch_below="0.5"
        )


def test_task3_invalid_step_is_rejected():
    planner = AdaptivePlanner()

    with pytest.raises(
        TypeError,
        match="step must be an integer or None",
    ):
        planner.record(
            True,
            step="1",
        )

# ============================================================
# Task 4 — Compare fixed and adaptive planners
# ============================================================

from src.adaptive_planning import (
    attempt,
    run,
)


def test_task4_attempt_is_deterministic_with_seed():
    rng1 = random.Random(42)
    rng2 = random.Random(42)

    results1 = [
        attempt("fast", 0.5, rng1)
        for _ in range(10)
    ]

    results2 = [
        attempt("fast", 0.5, rng2)
        for _ in range(10)
    ]

    assert results1 == results2


def test_task4_attempt_rejects_invalid_strategy():
    with pytest.raises(
        ValueError,
        match="unknown strategy",
    ):
        attempt(
            "unknown",
            0.5,
            random.Random(1),
        )


def test_task4_attempt_rejects_invalid_difficulty():
    with pytest.raises(
        ValueError,
        match="difficulty must be between 0 and 1",
    ):
        attempt(
            "fast",
            1.5,
            random.Random(1),
        )


def test_task4_fixed_planner_never_switches():
    difficulties = [0.1] * 5 + [0.9] * 15

    result = run(
        difficulties,
        adaptive=False,
        seed=1,
    )

    assert result["switches"] == []


def test_task4_adaptive_planner_can_switch():
    difficulties = [0.1] * 5 + [0.9] * 15

    result = run(
        difficulties,
        adaptive=True,
        seed=1,
    )

    assert len(result["switches"]) >= 1


def test_task4_fixed_planner_always_uses_fast_cost():
    difficulties = [0.1] * 5 + [0.9] * 15

    result = run(
        difficulties,
        adaptive=False,
        seed=1,
    )

    assert result["cost"] == len(difficulties)


def test_task4_adaptive_cost_reflects_strategy_usage():
    difficulties = [0.1] * 5 + [0.9] * 15

    result = run(
        difficulties,
        adaptive=True,
        seed=1,
    )

    assert result["cost"] >= len(difficulties)


def test_task4_comparison_is_reproducible():
    difficulties = [0.1] * 5 + [0.9] * 15

    first = run(
        difficulties,
        adaptive=True,
        seed=7,
    )

    second = run(
        difficulties,
        adaptive=True,
        seed=7,
    )

    assert first == second


def test_task4_five_seeds_produce_complete_results():
    difficulties = [0.1] * 5 + [0.9] * 15

    for seed in range(1, 6):
        fixed = run(
            difficulties,
            adaptive=False,
            seed=seed,
        )

        adaptive = run(
            difficulties,
            adaptive=True,
            seed=seed,
        )

        assert set(fixed) == {
            "wins",
            "cost",
            "switches",
        }

        assert set(adaptive) == {
            "wins",
            "cost",
            "switches",
        }


def test_task4_adaptive_has_switch_trace():
    difficulties = [0.1] * 5 + [0.9] * 15

    result = run(
        difficulties,
        adaptive=True,
        seed=1,
    )

    assert all(
        isinstance(step, int)
        for step in result["switches"]
    )

# ============================================================
# Task 5 — Prevent flip-flopping
# ============================================================

def test_task5_default_cooldown_is_ten():
    planner = AdaptivePlanner()

    assert planner.cooldown == 10


def test_task5_custom_cooldown_is_supported():
    planner = AdaptivePlanner(
        cooldown=5,
    )

    assert planner.cooldown == 5


def test_task5_first_switch_is_allowed():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
        cooldown=10,
    )

    for step in range(1, 5):
        planner.record(
            False,
            step=step,
        )

    assert planner.current == "careful"
    assert planner.switches == [4]


def test_task5_second_switch_before_cooldown_is_blocked():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
        switch_above=0.75,
        cooldown=10,
    )

    for step in range(1, 5):
        planner.record(
            False,
            step=step,
        )

    assert planner.switches == [4]

    for step in range(5, 14):
        planner.record(
            True,
            step=step,
        )

    assert planner.switches == [4]


def test_task5_switch_allowed_after_cooldown():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
        switch_above=0.75,
        cooldown=10,
    )

    for step in range(1, 5):
        planner.record(
            False,
            step=step,
        )

    assert planner.current == "careful"
    assert planner.switches == [4]

    for step in range(5, 14):
        planner.record(
            True,
            step=step,
        )

    # Step 14 is ten steps after step 4.
    planner.record(
        True,
        step=14,
    )

    assert planner.switches == [4, 14]
    assert planner.current == "fast"


def test_task5_switch_gap_is_at_least_cooldown():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
        switch_above=0.75,
        cooldown=10,
    )

    # First switch.
    for step in range(1, 5):
        planner.record(
            False,
            step=step,
        )

    # Build enough successful results for a possible
    # switch back after the cooldown.
    for step in range(5, 25):
        planner.record(
            True,
            step=step,
        )

    for previous, current in zip(
        planner.switches,
        planner.switches[1:],
    ):
        assert current - previous >= 10


def test_task5_invalid_cooldown_is_rejected():
    with pytest.raises(
        ValueError,
        match="cooldown must be at least 1",
    ):
        AdaptivePlanner(
            cooldown=0,
        )


def test_task5_invalid_cooldown_type_is_rejected():
    with pytest.raises(
        TypeError,
        match="cooldown must be an integer",
    ):
        AdaptivePlanner(
            cooldown="10",
        )


def test_task5_switch_above_must_exceed_switch_below():
    with pytest.raises(
        ValueError,
        match="switch_above must be greater",
    ):
        AdaptivePlanner(
            switch_below=0.7,
            switch_above=0.6,
        )


def test_task5_switch_trace_is_monotonic():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
        switch_above=0.75,
        cooldown=10,
    )

    for step in range(1, 5):
        planner.record(
            False,
            step=step,
        )

    for step in range(5, 25):
        planner.record(
            True,
            step=step,
        )

    assert planner.switches == sorted(
        planner.switches
    )


def test_task5_no_switches_can_occur_within_cooldown():
    planner = AdaptivePlanner(
        window=4,
        switch_below=0.5,
        switch_above=0.75,
        cooldown=10,
    )

    for step in range(1, 5):
        planner.record(
            False,
            step=step,
        )

    first_switch = planner.switches[0]

    for step in range(
        first_switch + 1,
        first_switch + 10,
    ):
        planner.record(
            True,
            step=step,
        )

    assert len(planner.switches) == 1