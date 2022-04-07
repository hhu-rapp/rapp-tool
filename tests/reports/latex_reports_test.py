from rapp.report.latex import tex_dataset_report

import tests.resources as rc


def test_dataset_report_table__two_groups__two_labels():
    report = {'train': {},
              'test': {}}

    report["train"] = {
        'groups': {'foo': {'foo1': {'outcomes': {'label1': 40, 'label2': 30},
                                    'total': 70},
                           'foo2': {'outcomes': {'label1': 20, 'label2': 60},
                                    'total': 80}},
                   'bar': {'bar1': {'outcomes': {'label1': 30, 'label2': 40},
                                    'total': 70},
                           'bar2': {'outcomes': {'label1': 30, 'label2': 50},
                                    'total': 80}}},
        'outcomes': {
            'label1': 60,
            'label2': 90,
        },
        'total': 150
    }
    report["test"] = {
        'groups': {'foo': {'foo1': {'outcomes': {'label1': 4, 'label2': 3},
                                    'total': 7},
                           'foo2': {'outcomes': {'label1': 2, 'label2': 6},
                                    'total': 8}},
                   'bar': {'bar1': {'outcomes': {'label1': 3, 'label2': 4},
                                    'total': 7},
                           'bar2': {'outcomes': {'label1': 3, 'label2': 5},
                                    'total': 8}}},
        'outcomes': {
            'label1': 6,
            'label2': 9,
        },
        'total': 15
    }

    expected = rc.get_text('reports/data_table_two_groups_two_labels.tex')
    actual = tex_dataset_report(report)

    assert expected == actual
