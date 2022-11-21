from rapp.pipeline import Pipeline, train_models, evaluate_fairness
from rapp.pipeline import evaluate_performance, calculate_statistics
from rapp.parser import RappConfigParser

from rapp.report import save_report

import sys


if __name__ == "__main__":
    parser = RappConfigParser()
    cf = parser.parse_args(sys.argv[1:])

    pl = Pipeline(cf)

    train_models(pl, cross_validation=True)
    evaluate_fairness(pl)
    evaluate_performance(pl)
    calculate_statistics(pl)

    save_report(pl, cf.report_path)
