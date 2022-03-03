from rapp.npipeline import Pipeline, train_models, evaluate_fairness
from rapp.parser import RappConfigParser


if __name__ == "__main__":
    parser = RappConfigParser()
    cf = parser.parse_args()

    pl = Pipeline(cf)

    train_models(pl, cross_validation=True)
    evaluate_fairness(pl)
    evaluate_performance(pl)
    # save_report(pl)

    # Todo:
    #   * [x] Train models
    #   * [x] Eval fairness
    #   * [ ] Save report
