from rapp.parser import RappConfigParser
from rapp.pipeline import MLPipeline


if __name__ == "__main__":
    parser = RappConfigParser()
    MLPipeline(parser.parse_args())
