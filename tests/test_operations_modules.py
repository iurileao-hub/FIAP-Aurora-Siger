import pytest
from aurora_siger.operations.modules import MODULES, find_module


def test_thirteen_modules_with_unique_ids():
    ids = [m["id"] for m in MODULES]
    assert len(MODULES) == 13
    assert sorted(ids) == list(range(1, 14))


def test_each_module_has_four_modes():
    for m in MODULES:
        assert set(m["consumption_by_mode"]) == {"off", "minimum", "adequate", "surplus"}


def test_find_module_returns_dict_and_raises_on_missing():
    assert find_module(1)["name"] == "Command and Control"
    with pytest.raises(KeyError):
        find_module(999)


def test_three_generators_present():
    gens = [m for m in MODULES if "generator" in m["type"]]
    assert {m["type"] for m in gens} == {"solar_generator", "nuclear_generator", "wind_generator"}
