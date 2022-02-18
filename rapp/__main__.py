from rapp.npipeline import Pipeline, train_models
from rapp.parser import RappConfigParser


if __name__ == "__main__":
    parser = RappConfigParser()
    cf = parser.parse_args()

    pl = Pipeline(cf)

    train_models(pl, cross_validation=True)

    # Todo:
    #   * [x] Train models
    #   * [ ] Eval fairness
    #   * [ ] Save report
