from aurora_siger.colony import roster


def test_priority_from_criticality_tier():
    assert roster.criticality_of(3) == "Vital"          # Habitat
    assert roster.criticality_of(8) == "Sustenance"     # Food Production
    assert roster.criticality_of(12) == "Expansion"     # Science Lab
    assert roster.priority_of(3) == 10
    assert roster.priority_of(8) == 7
    assert roster.priority_of(12) == 4


def test_generation_capacity_is_sum_of_generators():
    # Solar 100 + Nuclear 80 + Wind 30
    assert roster.generation_capacity_kw() == 210.0


def test_derived_attributes_use_adequate_mode():
    attrs = roster.derived_attributes(3)  # Habitat
    assert attrs["name"] == "Habitat"
    assert attrs["type"] == "consumer"
    assert attrs["consumption"] == 15      # adequate mode
    assert attrs["priority"] == 10


def test_all_thirteen_have_a_tier():
    for mid in range(1, 14):
        assert roster.criticality_of(mid) in ("Vital", "Sustenance", "Expansion")
