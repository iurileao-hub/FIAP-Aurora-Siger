from aurora_siger.colony import cli, topology


def test_pt_labels_cover_all_thirteen():
    g = topology.build_graph()
    for module in g.module_list:
        assert module.id in cli.PT_LABELS
        assert cli.PT_LABELS[module.id]            # non-empty PT name


def test_label_renders_pt_for_known_module():
    g = topology.build_graph()
    assert cli.label(g.get_module(1)) == "Centro de Controle"


def test_main_is_callable():
    assert callable(cli.main)
