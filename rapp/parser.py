import configargparse


class RappConfigParser(object):

    def __init__(self):
        self.parser = self._setup_parser()

    def parse_args(self, args):
        parsed = self.parser.parse_args(args=args)

        # When `estimators` config is not given, we default based on type.
        if parsed.estimators is None:
            if parsed.type == 'classification':
                parsed.estimators = ['RF', 'DT', 'SVM', 'NB', 'LR', 'NN']
            elif parsed.type == 'regression':
                parsed.estimators = ['LR', 'EL', 'BR']

        # Double Check that the SQL-information was given correctly.
        has_arg = lambda arg: parsed.__dict__[arg] is not None  # Helper fun.
        uses_templating = (has_arg('studies_id') or
                           has_arg('features_id') or
                           has_arg('labels_id'))
        if uses_templating:
            if (not (has_arg('studies_id')
                     and has_arg('features_id')
                     and has_arg('labels_id'))):
                raise Exception("When using either --studies_id, --features_id,"
                                " or --labels_id, all three must be given.")
            # Cannot use --sql_file now.
            if has_arg('sql_file') or has_arg('sql_query'):
                raise Exception("Can only have either sql file, or templating"
                                " engine, or sql query, not multiple.")
        elif has_arg('sql_file') and has_arg('sql_query'):
            raise Exception("Can only have either sql file, or templating"
                            " engine, or sql query, not multiple.")
        elif not (has_arg('sql_file') or has_arg('sql_query')):
            raise Exception("Must have information about which SQL query"
                            " to use.")

        return parsed

    def _setup_parser(self):
        parser = configargparse.ArgParser()
        parser.add('-cf', '--config-file', required=False,
                   is_config_file=True, help='config file path')

        # methodical settings
        parser.add_argument('-f', '--filename', type=str,
                            help='Location of the .db file.',
                            required=True)

        # The SQL settings need to be manually be cross-checked that they
        # are correctly assessed.
        # The following settings are mutually exclusive
        #   --sql_file
        #   --studies_id --features_id --labels_id
        # Note that the logic behind argparse's add_mutually_exclusive_group
        # does not allow for nested groups - which we need here though.

        parser.add_argument('-sf', '--sql_file', type=str,
                            help='Path to a custom SQL query file.',
                            required=False)

        parser.add_argument('-sq', '--sql_query', type=str,
                            help='SQL query',
                            required=False)

        parser.add_argument('-sid', '--studies_id', type=str,
                            help='Study Id for the sql query file.',
                            required=False)
        parser.add_argument('-fid', '--features_id', type=str,
                            help='Feature Id for the sql query file.',
                            required=False)
        parser.add_argument('-lid', '--labels_id', type=str,
                            help='Label Id for the sql query file.',
                            required=False)

        parser.add_argument('-l', '--label_name', type=str,
                            help='Column name of the prediction label.',
                            required=False)

        parser.add_argument('-c', '--categorical', nargs='+',
                            help='List of categorical columns.',
                            required=False, default=[])
        parser.add_argument('-i', '--ignore', nargs='+',
                            help='List of columns to ignore.',
                            required=False, default=[])

        parser.add_argument('--feature_selection', type=str, default='variance',
                            choices=['variance'],
                            help='Feature selection method to reduce the amount of features. Available: variance',
                            required=False)

        parser.add_argument('--imputation', type=str, default='iterative',
                            choices=['knn', 'iterative', 'mean',
                                     'median', 'most_frequent'],
                            help='Imputation method for non-categorical data. Available: knn, iterative, mean, '
                            'median, most_frequent',
                            required=False)

        parser.add_argument('--sensitive_attributes', nargs='+',
                            help='List of sensitive attributes',
                            required=False, default=[])
        parser.add_argument('--privileged_groups', nargs='+',
                            help='List of privileged group values; one for each sensitive attribute. The order must match.',
                            required=False, default=[])

        parser.add_argument('-t', '--type', type=str, default='classification',
                            choices=['classification', 'regression'],
                            help='classification or regression. Default: classification',
                            required=False)
        parser.add_argument('--estimators', nargs='+', default=None,
                            required=False,
                            help='If given then --type is ignored.'
                            'Takes a single classifier to train on.')

        parser.add_argument('--save_report', type=str, default='True',
                            choices=['True', 'False'],
                            help='Boolean value whether a report should be exported',
                            required=False)
        parser.add_argument('--report_path', type=str, default=None,
                            help='Path destination of report file. If path is given, then the report file will '
                            'be saved in path/results_report.csv. Note: Relative path to working directory.')

        return parser
