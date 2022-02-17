from rapp.npipeline import Pipeline
from rapp.parser import RappConfigParser


if __name__ == "__main__":
    parser = RappConfigParser()
    cf = parser.parse_args()

    pl = Pipeline(cf)

    # Todo:
    #   * [ ] Train models
    #   * [ ] Eval fairness
    #   * [ ] Save report
