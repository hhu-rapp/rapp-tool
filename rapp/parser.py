# RAPP_Prediction library
from rapp.pipeline import MLPipeline

# system
import configargparse


class RappConfigParser(object):

    def __init__(self):
        self.parser = configargparse.ArgParser()
        self.parser.add('-cf', '--config-file', required=True, is_config_file=True, help='config file path')

        # parsing arguments from the config file
        self.parser = parse_rapp_args(self.parser)
        self.args = self.parser.parse_args()

        MLPipeline(self.args)


def parse_rapp_args(parser):
    """
    
    Parameters
    ----------
    parser: ArgParser

    Returns
    -------
    ArgParser
    """

    # methodical settings
    parser.add_argument('-f', '--filename', type=str, help='Location of the .db file.',
                             required=True)
    parser.add_argument('-s', '--sql_filename', type=str, help='Location of the sql query file.',
                             required=True)
    parser.add_argument('-l', '--label_name', type=str, help='Column name of the prediction label.',
                             required=True)
    parser.add_argument('-c', '--categorical', nargs='+', help='List of categorical columns.',
                             required=True)
    parser.add_argument('-t', '--type', type=str, default='classification',
                             choices=['classification', 'regression'],
                             help='classification or regression. Default: classification',
                             required=False)
    parser.add_argument('--imputation', type=str, default='iterative',
                             choices=['knn', 'iterative', 'mean', 'median', 'most_frequent'],
                             help='Imputation method for non-categorical data. Available: knn, iterative, mean, '
                                  'median, most_frequent',
                             required=False)
    parser.add_argument('--feature_selection', type=str, default='variance',
                             choices=['variance'],
                             help='Feature selection method to reduce the amount of features. Available: variance, '
                                  '',
                             required=False)

    # additional settings
    parser.add_argument('--save_report', type=str, default='True',
                             choices=['True', 'False'],
                             help='Boolean value whether a report should be exported',
                             required=False)
    parser.add_argument('--report_path', type=str, default='',
                             help='Path destination of report file. If path is given, then the report file will '
                                  'be saved in path/results_report.csv. Note: Relative path to working directory.')
    parser.add_argument('--plot_confusion_matrix', type=str, default='False',
                             help='Boolean value whether to plot confusion matrices for each classifier. '
                                  'Is only applied for classification.',
                             required=False)
    parser.add_argument('--classifier', type=str, default=None,
                        choices=['RF', 'DT', 'SVM', 'NB', 'LR'],
                        help='If given then --type is ignored. Takes a single classifier to train on. Choices: RF, DT, '
                             'SVM, NB, LR')

    return parser
