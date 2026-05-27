"""Test fixtures shared across the suite.

MODULES (aurora_siger.operations.modules) is module-level shared state that
allocation and failures mutate in place. Resetting each module's runtime
fields before every test makes the suite order-independent: no test inherits
another's modes or failures. (run_simulation does the same reset internally;
this fixture protects tests that drive step()/allocate_energy directly.)
"""

import pytest

from aurora_siger.operations.modules import MODULES


@pytest.fixture(autouse=True)
def _reset_module_runtime_state():
    for m in MODULES:
        m["broken"] = False
        m["repair_hours_remaining"] = 0
        m["current_mode"] = "adequate"
    yield
