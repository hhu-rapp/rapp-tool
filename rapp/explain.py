# rapp
from rapp.pipeline.util import load_pipeline_from_config
from rapp.util import pareto_front

import numpy as np
import sklearn as sk

from sklearn.tree import DecisionTreeClassifier
# plots
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
# plt.rcParams['figure.figsize'] = [60, 20]

db_filepath = "data/rapp.db"


class Explain(object):

    def __init__(self):
        self.pipeline = load_pipeline_from_config()

        # getting objects from MLPipeline
        self.estimator = self.pipeline.get_estimators()[0]
        self.X_train, self.y_train = self.pipeline.X_train, self.pipeline.y_train
        self.X_test, self.y_test = self.pipeline.X_test, self.pipeline.y_test

    def explain(self):
        if self.pipeline.args.classifier == 'DT':
            self.explain_dt()

    def explain_dt(self):
        depths = np.arange(1, 8)

        # testing hyperparameter
        clfs = []
        for depth in depths:
            clf = DecisionTreeClassifier(random_state=0, max_depth=depth,
                                         class_weight="balanced", min_impurity_decrease=0.001)
            clf.fit(self.X_train, self.y_train)
            clfs.append(clf)

        acc_scores = [sk.metrics.balanced_accuracy_score(self.y_test, clf.predict(self.X_test)) for clf in clfs]

        # find pareto optima; negative depth to allow minimising over it
        datapoints = np.array([depths, acc_scores]).T
        pareto_points = _find_tree_optima(datapoints)

        self.selected_idx = None

        # user selects pareto-optimal solution
        def mouse_move(event):
            x, y = event.xdata, event.ydata
            if event.dblclick:
                dists = np.linalg.norm(np.array([x, y]) - pareto_points, axis=1)
                self.selected_idx = np.argmin(dists)
                print(dists)
                plt.close()

        # scatter pareto optimal solutions
        plt.connect('motion_notify_event', mouse_move)
        plt.connect('button_press_event', mouse_move)
        plt.scatter(datapoints[:, 0], datapoints[:, 1], s=8, c='blue', label='Non Pareto-optimal')
        plt.scatter(pareto_points[:, 0], pareto_points[:, 1], s=12, c='red', label='Pareto optimal')
        plt.xlabel('Max Depth')
        plt.ylabel('Accuracy (balanced)')
        plt.show()

        # train with selected hyperparameter
        selected_depth = pareto_points[self.selected_idx, 0]
        print(selected_depth)
        clf = DecisionTreeClassifier(random_state=0, class_weight="balanced", min_impurity_decrease=0.001,
                                     max_depth=selected_depth)

        clf.fit(self.X_train, self.y_train)

        # save estimator into estimators
        self.estimator = clf

        plt.figure(figsize=(12, 8))
        print(clf.classes_)
        plot_tree(clf, feature_names=self.X_train.columns, class_names=list(map(str, clf.classes_)))
        plt.show()


def _find_tree_optima(datapoints):
    """
    Parameters
    ----------
    datapoints: np.array (n_samples, 2)
        Contains `n_samples` entries of the form
        `[tree_depth, performance_score]`.

    Returns
    -------
    array (n_samples, 2)
        Pareto optima in `datapoints` where tree depth is minimised and
        performance score is maximised.
    """
    data = datapoints.copy()
    data[:,0] = -data[:,0]  # Negate depths so we can maximise.
    pf = pareto_front(data)
    return datapoints[pf]


if __name__ == '__main__':
    explain = Explain()
    explain.explain()
