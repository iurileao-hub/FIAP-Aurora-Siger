"""Linear data structures: ``Vector``, ``Queue`` and ``Stack``.

These are didactic re-implementations of standard linear ADTs over a Python
``list``. ``Vector`` exposes index-based access plus search and sort
algorithms operating on :class:`Module` attributes; ``Queue`` and ``Stack``
inherit those algorithms while restricting access to FIFO / LIFO discipline.

The hierarchy mirrors Figure A.1 of the Phase 2 report. The container is
polymorphic — :attr:`alert_stack` (defined in :mod:`mission`) carries
:class:`Alert` records rather than modules, so the search/sort methods are
documented as Module-specific and should not be invoked on alert stacks.
"""

from __future__ import annotations

from typing import Any

from aurora_siger.landing.module import Module


class Vector:
    """Ordered list with arbitrary-position insert and remove.

    Centralizes search and sort algorithms over modules so :class:`Queue` and
    :class:`Stack` inherit them without duplication.
    """

    def __init__(self) -> None:
        self._data: list[Any] = []

    # --- Vector interface ---

    def append(self, item: Any) -> None:
        """Append an item to the end."""
        self._data.append(item)

    def insert(self, index: int, item: Any) -> None:
        """Insert an item at a specific position."""
        self._data.insert(index, item)

    def remove_at(self, index: int) -> Any:
        """Pop the item at ``index``. Raises ``IndexError`` if out of range."""
        if index < 0 or index >= len(self._data):
            raise IndexError("Index out of range.")
        return self._data.pop(index)

    def get(self, index: int) -> Any:
        """Return the item at ``index`` without removing it."""
        return self._data[index]

    def size(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def to_list(self) -> list[Any]:
        """Return a shallow copy of the internal list."""
        return list(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index: int) -> Any:
        return self._data[index]

    def __iter__(self):
        return iter(self._data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data})"

    # --- Search (linear, O(n)) — Module-specific ---

    def search_by_type(self, module_type: str) -> list[Module]:
        """Linear search returning every module whose ``type`` matches."""
        return [item for item in self._data if item.type == module_type]

    def search_min_fuel(self) -> Module | None:
        """Linear search for the module with the lowest ``fuel_level``."""
        if self.is_empty():
            return None
        minimum = self._data[0]
        for i in range(1, len(self._data)):
            if self._data[i].fuel_level < minimum.fuel_level:
                minimum = self._data[i]
        return minimum

    def search_highest_priority(self) -> Module | None:
        """Linear search for the module with the highest priority (lowest number)."""
        if self.is_empty():
            return None
        best = self._data[0]
        for i in range(1, len(self._data)):
            if self._data[i].priority < best.priority:
                best = self._data[i]
        return best

    def find_by_id(self, module_id: int) -> Module | None:
        """Linear search for the module with the given ``id``."""
        for item in self._data:
            if item.id == module_id:
                return item
        return None

    # --- Sort — Module-specific ---

    def sort_multi(self) -> None:
        """Bubble sort by (eta, priority, fuel_level) ascending, in place.

        Tie-break order: ETA first (whoever arrives first lands first), then
        mission priority, then fuel level (the running-low module gets through
        when everything else is equal).

        Complexity: O(n²) worst case, O(n) best case (early-exit on no swaps).
        """
        n = len(self._data)
        for i in range(n):
            swapped = False
            for j in range(n - i - 1):
                a = self._data[j]
                b = self._data[j + 1]
                if (a.eta, a.priority, a.fuel_level) > (b.eta, b.priority, b.fuel_level):
                    self._data[j], self._data[j + 1] = self._data[j + 1], self._data[j]
                    swapped = True
            if not swapped:
                break

    def sort_by_priority(self) -> None:
        """Bubble sort by ``priority`` ascending, in place. O(n²) / O(n)."""
        n = len(self._data)
        for i in range(n):
            swapped = False
            for j in range(n - i - 1):
                if self._data[j].priority > self._data[j + 1].priority:
                    self._data[j], self._data[j + 1] = self._data[j + 1], self._data[j]
                    swapped = True
            if not swapped:
                break

    def sort_by_fuel(self) -> None:
        """Selection sort by ``fuel_level`` ascending, in place. O(n²) always."""
        n = len(self._data)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if self._data[j].fuel_level < self._data[min_idx].fuel_level:
                    min_idx = j
            if min_idx != i:
                self._data[i], self._data[min_idx] = self._data[min_idx], self._data[i]


class Queue(Vector):
    """FIFO queue built on :class:`Vector`. Restricts access to enqueue / dequeue."""

    def enqueue(self, item: Any) -> None:
        self.append(item)

    def dequeue(self) -> Any | None:
        """Pop the first item, or ``None`` if empty."""
        if self.is_empty():
            return None
        return self.remove_at(0)

    def peek(self) -> Any | None:
        """Inspect the first item without removing it."""
        if self.is_empty():
            return None
        return self.get(0)


class Stack(Vector):
    """LIFO stack built on :class:`Vector`. Restricts access to push / pop."""

    def push(self, item: Any) -> None:
        self.append(item)

    def pop(self) -> Any | None:
        """Pop the top item, or ``None`` if empty."""
        if self.is_empty():
            return None
        return self.remove_at(len(self._data) - 1)

    def peek(self) -> Any | None:
        """Inspect the top item without removing it."""
        if self.is_empty():
            return None
        return self.get(-1)
