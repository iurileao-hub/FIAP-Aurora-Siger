"""LandingMission — stateful orchestrator for one simulation run.

Owns the four linear structures (queue, landed/waiting vectors, alert stack)
and the environmental conditions dict, replacing the module-level globals
that the original prototype relied on. Two missions can run in parallel
within one notebook session, e.g. to compare scenarios.

Public API:

- :meth:`LandingMission.from_defaults` — build a fresh mission from
  :data:`module.DEFAULT_MODULES`.
- :meth:`LandingMission.randomize_scenario` — reseed every module's volatile
  attributes and resample environmental flags.
- :meth:`LandingMission.simulate` — drain the queue, decide each module,
  return a :class:`SimulationReport`. Pure: does not print.
- :meth:`LandingMission.print_report` — human-readable rendering of a report.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Iterable

from aurora_siger.landing.authorization import Alert, AuthorizationResult, evaluate
from aurora_siger.landing.module import DEFAULT_MODULES, Module
from aurora_siger.landing.structures import Queue, Stack, Vector


# Probability that each environmental flag is OK at scenario start.
# Inspired by realistic mission constraints: Martian dust storms make
# atmosphere the more volatile factor (70%) compared to landing-zone
# clearance under good orbital planning (90%).
CONDITION_PROBABILITIES = {
    "atmosphere_ok": 0.70,
    "landing_zone_free": 0.90,
}


@dataclass
class SimulationReport:
    """Outcome of one :meth:`LandingMission.simulate` call.

    Attributes:
        landed: Modules that received authorization, in landing order.
        waiting: Modules denied, in dequeue order.
        alerts: Alerts generated, ordered as they were pushed (oldest first).
        decisions: Per-module decisions in original processing order, useful
            for auditing without reconstructing the result lists.
    """

    landed: list[Module] = field(default_factory=list)
    waiting: list[Module] = field(default_factory=list)
    alerts: list[Alert] = field(default_factory=list)
    decisions: list[tuple[Module, AuthorizationResult]] = field(default_factory=list)


class LandingMission:
    """Stateful orchestrator of a single landing operation.

    Encapsulates the four linear structures (``landing_queue``,
    ``landed_modules``, ``waiting_modules``, ``alert_stack``) and the
    environmental conditions dict. Construct via :meth:`from_defaults` or by
    passing an iterable of :class:`Module` instances directly.
    """

    def __init__(
        self,
        modules: Iterable[Module] | None = None,
        conditions: dict[str, bool] | None = None,
    ) -> None:
        self.landing_queue: Queue = Queue()
        self.landed_modules: Vector = Vector()
        self.waiting_modules: Vector = Vector()
        self.alert_stack: Stack = Stack()
        self.conditions: dict[str, bool] = conditions or {
            "atmosphere_ok": True,
            "landing_zone_free": True,
        }
        if modules is not None:
            for module in modules:
                self.landing_queue.enqueue(module)

    # --- Construction helpers ---

    @classmethod
    def from_defaults(cls) -> LandingMission:
        """Build a mission seeded with copies of :data:`DEFAULT_MODULES`."""
        return cls(modules=(m.copy() for m in DEFAULT_MODULES))

    def reload(self) -> None:
        """Reset all structures and re-enqueue copies of :data:`DEFAULT_MODULES`."""
        self.landing_queue = Queue()
        self.landed_modules = Vector()
        self.waiting_modules = Vector()
        self.alert_stack = Stack()
        for module in DEFAULT_MODULES:
            self.landing_queue.enqueue(module.copy())

    def randomize_scenario(self) -> None:
        """Resample volatile attributes of every queued module and the
        environmental flags.

        Mutates the queued modules in place — call before :meth:`simulate`.
        """
        for module in self.landing_queue:
            module.randomize()
        for key in self.conditions:
            self.conditions[key] = random.random() < CONDITION_PROBABILITIES[key]

    # --- Core simulation ---

    def simulate(self, *, sort_first: bool = True) -> SimulationReport:
        """Drain the queue, evaluate each module, and return a report.

        Args:
            sort_first: When True (default), apply :meth:`Queue.sort_multi`
                before processing — this is the canonical landing order
                (ETA → priority → fuel).

        Side effects:
            - Modules move from ``landing_queue`` to ``landed_modules`` or
              ``waiting_modules`` depending on the rule outcome.
            - Each denial pushes one :class:`Alert` onto ``alert_stack``.
            - Each module's ``status`` is updated to ``"landed"`` or
              ``"waiting"``.

        Returns:
            A :class:`SimulationReport` summarizing the run.
        """
        if sort_first:
            self.landing_queue.sort_multi()

        report = SimulationReport()

        while not self.landing_queue.is_empty():
            module = self.landing_queue.dequeue()
            result = evaluate(module, self.conditions)
            report.decisions.append((module, result))

            if result.authorized:
                module.status = "landed"
                self.landed_modules.append(module)
                report.landed.append(module)
            else:
                module.status = "waiting"
                self.waiting_modules.append(module)
                report.waiting.append(module)
                alert = Alert(
                    module_id=module.id,
                    module_name=module.name,
                    reason="; ".join(result.reasons),
                    timestamp=module.eta_str,
                )
                self.alert_stack.push(alert)
                report.alerts.append(alert)

        return report

    # --- Convenience: human-readable rendering ---

    def print_report(self, report: SimulationReport) -> None:
        """Print a formatted simulation report to stdout."""
        atm = "OK" if self.conditions["atmosphere_ok"] else "DESFAVORÁVEL"
        zone = "LIVRE" if self.conditions["landing_zone_free"] else "OCUPADA"

        print()
        print("=" * 60)
        print("     SIMULAÇÃO DE POUSO — Colônia Aurora Siger")
        print("=" * 60)
        print()
        print(f"  Condições: Atmosfera={atm} | Zona={zone} | Sensores=por módulo")
        print("  Ordem de pouso: ETA → prioridade → combustível")
        print()
        print(f"  Processando fila de pouso ({len(report.decisions)} módulos)...")
        print("-" * 60)

        for module, result in report.decisions:
            if result.authorized:
                print(f"  [AUTORIZADO] {module.name:<30} ETA {module.eta_str}")
            else:
                reason = "; ".join(result.reasons) or "Desconhecido"
                print(f"  [BLOQUEADO]  {module.name:<30} ETA {module.eta_str}")
                print(f"               Motivo: {reason}")

        print()
        print("-" * 60)
        print("     RESUMO DA SIMULAÇÃO")
        print("-" * 60)
        print(f"  Módulos pousados com sucesso:  {len(report.landed)}")
        print(f"  Módulos em espera (bloqueados): {len(report.waiting)}")
        print(f"  Alertas gerados:               {len(report.alerts)}")
        print()
