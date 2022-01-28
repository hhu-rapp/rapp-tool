# RAPP_Prediction library

# system
import configargparse


class RappConfigParser(object):

    def __init__(self):
        self.parser = self.setup_parser()

    def parse_args(self):
        return self.parser.parse_args()

    def setup_parser(self):
        """

        Returns
        -------
        ArgParser
        """
        parser = configargparse.ArgParser()
        parser.add('-cf', '--config-file', required=True, is_config_file=True, help='config file path')


        # methodical settings
        parser.add_argument('-f', '--filename', type=str, help='Location of the .db file.',
                                required=True)
        parser.add_argument('-s', '--sql_filename', type=str, help='Location of the sql query file.',
        parser.add_argument('-sid', '--studies_id', type=str, help='Study Id for the sql query file.',
                                                        required=True)
        parser.add_argument('-fid', '--features_id', type=str, help='Feature Id for the sql query file.',
                                required=True)
        parser.add_argument('-lid', '--labels_id', type=str, help='Label Id for the sql query file.',
                                required=True)
        parser.add_argument('-l', '--label_name', type=str, help='Column name of the prediction label.',
                                required=False)
        parser.add_argument('-c', '--categorical', nargs='+', help='List of categorical columns.',
                                required=False, default=[])
        parser.add_argument('-i', '--ignore', nargs='+', help='List of columns to ignore.',
                                required=False, default=[])
        parser.add_argument('--sensitive_attributes', nargs='+', help='List of sensitive attributes',
                                required=False, default=[])
        parser.add_argument('--privileged_groups', nargs='+', help='List of privileged group values; one for each sensitive attribute. The order must match.',
                                required=False, default=[])
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
        parser.add_argument('--report_path', type=str, default=None,
                                help='Path destination of report file. If path is given, then the report file will '
                                        'be saved in path/results_report.csv. Note: Relative path to working directory.')
        parser.add_argument('--classifier', type=str, default=None,
                            choices=['RF', 'DT', 'SVM', 'NB', 'LR'],
                            help='If given then --type is ignored. Takes a single classifier to train on. Choices: RF, DT, '
                                'SVM, NB, LR')

        return parser
