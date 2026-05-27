"""Linear Congruential Generator (LCG) — implemented from scratch.

Ported from the team's `main` branch (colonia_aurora/seed). Parameters from
Numerical Recipes. A `gauss()` method (Box-Muller) is added here because the
climate model needs Gaussian noise and the stdlib `random` module is not used
in this package — all randomness flows through a single seeded LCG instance.
"""

import math
from time import time
from typing import List, Optional, Sequence, TypeVar

T = TypeVar("T")


class RandomLCG:
    """X_{n+1} = (a * X_n + c) mod m, with m = 2^32 (Numerical Recipes)."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self.a = 1664525
        self.c = 1013904223
        self.m = 2 ** 32
        if seed is None:
            seed = int(time() * 1_000_000) % self.m
        self.state = seed % self.m
        self.initial_seed = self.state

    def set_seed(self, seed: int) -> None:
        self.state = seed % self.m
        self.initial_seed = self.state

    def next_int(self) -> int:
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def random(self) -> float:
        """Float in [0, 1)."""
        return self.next_int() / self.m

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self.random()

    def randint(self, low: int, high: int) -> int:
        """Integer in [low, high] (both inclusive)."""
        if low > high:
            raise ValueError("low must be <= high")
        return low + (self.next_int() % (high - low + 1))

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Gaussian sample via the Box-Muller transform."""
        u1 = self.random()
        u2 = self.random()
        if u1 < 1e-12:  # guard against log(0)
            u1 = 1e-12
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mu + sigma * z0

    def choice(self, sequence: Sequence[T]) -> T:
        if not sequence:
            raise ValueError("cannot choose from an empty sequence")
        return sequence[self.randint(0, len(sequence) - 1)]

    def shuffle(self, array: List[T]) -> None:
        for i in range(len(array) - 1, 0, -1):
            j = self.randint(0, i)
            array[i], array[j] = array[j], array[i]

    def get_state(self) -> int:
        return self.state
