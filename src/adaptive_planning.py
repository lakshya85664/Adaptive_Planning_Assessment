"""
Topic 15: Adaptive Planning

Tasks 1-5:
- Define planning strategies.
- Track a rolling window of results.
- Switch strategies based on recent performance.
- Compare fixed and adaptive planners.
- Prevent rapid strategy flip-flopping with a cooldown.
"""

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Strategy:
    """A planning strategy with cost and reliability characteristics."""

    name: str
    cost: int
    skill: float


STRATEGIES = {
    "fast": Strategy(
        name="fast",
        cost=1,
        skill=0.45,
    ),
    "careful": Strategy(
        name="careful",
        cost=3,
        skill=0.90,
    ),
}


def get_strategy(name: str) -> Strategy:
    """Return a strategy by name."""
    if not isinstance(name, str):
        raise TypeError(
            "strategy name must be a string"
        )

    if name not in STRATEGIES:
        raise ValueError(
            f"unknown strategy: {name}"
        )

    return STRATEGIES[name]


class AdaptivePlanner:
    """
    Track recent results and adapt the current strategy.

    A switch is allowed only when:
    1. The rolling window is full.
    2. The success rate crosses the relevant threshold.
    3. The cooldown since the previous switch has elapsed.
    """

    def __init__(
        self,
        window: int = 4,
        switch_below: float = 0.5,
        switch_above: float = 0.75,
        cooldown: int = 10,
    ):
        if not isinstance(window, int):
            raise TypeError(
                "window must be an integer"
            )

        if window < 1:
            raise ValueError(
                "window must be at least 1"
            )

        if not isinstance(
            switch_below,
            (int, float),
        ):
            raise TypeError(
                "switch_below must be numeric"
            )

        if not 0 <= switch_below <= 1:
            raise ValueError(
                "switch_below must be between 0 and 1"
            )

        if not isinstance(
            switch_above,
            (int, float),
        ):
            raise TypeError(
                "switch_above must be numeric"
            )

        if not 0 <= switch_above <= 1:
            raise ValueError(
                "switch_above must be between 0 and 1"
            )

        if switch_above <= switch_below:
            raise ValueError(
                "switch_above must be greater than switch_below"
            )

        if not isinstance(cooldown, int):
            raise TypeError(
                "cooldown must be an integer"
            )

        if cooldown < 1:
            raise ValueError(
                "cooldown must be at least 1"
            )

        self.window = window
        self.switch_below = float(switch_below)
        self.switch_above = float(switch_above)
        self.cooldown = cooldown

        self.current = "fast"
        self.recent = []
        self.switches = []
        self.last_switch_step = None

    def record(
        self,
        success: bool,
        step: int | None = None,
    ) -> None:
        """
        Record a result and evaluate whether to switch.

        The rolling window must be full before any switch.
        Once a switch occurs, another switch cannot happen
        until the cooldown has elapsed.
        """
        if not isinstance(success, bool):
            raise TypeError(
                "success must be a boolean"
            )

        if step is not None and not isinstance(
            step,
            int,
        ):
            raise TypeError(
                "step must be an integer or None"
            )

        self.recent.append(success)

        if len(self.recent) > self.window:
            self.recent = self.recent[-self.window :]

        if not self.window_full:
            return

        current_step = (
            step
            if step is not None
            else len(self.recent)
        )

        if self.last_switch_step is not None:
            if (
                current_step - self.last_switch_step
                < self.cooldown
            ):
                return

        if (
            self.current == "fast"
            and self.success_rate < self.switch_below
        ):
            self._switch(
                "careful",
                current_step,
            )

        elif (
            self.current == "careful"
            and self.success_rate > self.switch_above
        ):
            self._switch(
                "fast",
                current_step,
            )

    def _switch(
        self,
        strategy: str,
        step: int,
    ) -> None:
        """Record a strategy switch."""
        self.current = strategy
        self.switches.append(step)
        self.last_switch_step = step

    @property
    def success_rate(self) -> float:
        """Return the current rolling success rate."""
        if not self.recent:
            return 0.0

        return sum(self.recent) / len(self.recent)

    @property
    def window_full(self) -> bool:
        """Return True when the rolling window is full."""
        return len(self.recent) == self.window


def attempt(
    strategy: str,
    difficulty: float,
    rng: random.Random,
) -> bool:
    """
    Execute one deterministic simulated attempt.

    Higher skill increases the chance of success.
    Difficulty makes success harder.
    """
    if strategy not in STRATEGIES:
        raise ValueError(
            f"unknown strategy: {strategy}"
        )

    if not isinstance(
        difficulty,
        (int, float),
    ):
        raise TypeError(
            "difficulty must be numeric"
        )

    if not 0 <= difficulty <= 1:
        raise ValueError(
            "difficulty must be between 0 and 1"
        )

    probability = max(
        0.05,
        STRATEGIES[strategy].skill
        - difficulty * 0.4
        + 0.3,
    )

    probability = min(
        probability,
        0.98,
    )

    return rng.random() < probability


def run(
    difficulties,
    adaptive: bool,
    seed: int = 1,
):
    """
    Run fixed or adaptive planning on a sequence of tasks.

    Returns wins, total cost, and switch steps.
    """
    if not isinstance(
        adaptive,
        bool,
    ):
        raise TypeError(
            "adaptive must be a boolean"
        )

    rng = random.Random(seed)
    planner = AdaptivePlanner()

    wins = 0
    cost = 0

    for step, difficulty in enumerate(
        difficulties,
        start=1,
    ):
        strategy = (
            planner.current
            if adaptive
            else "fast"
        )

        ok = attempt(
            strategy,
            difficulty,
            rng,
        )

        wins += ok
        cost += STRATEGIES[strategy].cost

        if adaptive:
            planner.record(
                ok,
                step=step,
            )

    return {
        "wins": wins,
        "cost": cost,
        "switches": planner.switches,
    }