# rapp
from rapp.pipeline import MLPipeline
from rapp.parser import RappConfigParser

# data analysis
import numpy as np
import sklearn as sk
import oapackage

from sklearn.tree import DecisionTreeClassifier
# plots
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
# plt.rcParams['figure.figsize'] = [60, 20]

db_filepath = "data/rapp.db"


class Explain(object):

    def __init__(self):
        parser = RappConfigParser()
        self.pipeline = MLPipeline(parser.parse_args())

        # getting objects from MLPipeline
        self.estimator = self.pipeline.get_estimators()[0]
        self.X_train, self.y_train = self.pipeline.X_train, self.pipeline.y_train
        self.X_test, self.y_test = self.pipeline.X_test, self.pipeline.y_test

    def explain(self):
        if self.pipeline.args.classifier == 'DT':
            self.explain_dt()

    def explain_dt(self):
        # getting hyperparameter space
        ccp_alphas = self.estimator.cost_complexity_pruning_path(self.X_train, self.y_train).ccp_alphas[:-1]

        # testing hyperparameter
        clfs = []
        for ccp_alpha in ccp_alphas:
            clf = DecisionTreeClassifier(random_state=0, ccp_alpha=ccp_alpha,
                                         class_weight="balanced", min_impurity_decrease=0.001)
            clf.fit(self.X_train, self.y_train)
            clfs.append(clf)

        acc_scores = [sk.metrics.balanced_accuracy_score(self.y_test, clf.predict(self.X_test)) for clf in clfs]

        # find pareto optima
        datapoints = np.array([ccp_alphas, acc_scores]).T
        pareto = oapackage.ParetoDoubleLong()
        for ii in range(0, datapoints.shape[0]):
            w = oapackage.doubleVector((datapoints[ii, 0], datapoints[ii, 1]))
            pareto.addvalue(w, ii)

        # list of indexes of pareto optimal solutions
        lst = pareto.allindices()#[0]

        self.selected_idx = None

        # user selects pareto-optimal solution
        def mouse_move(event):
            x, y = event.xdata, event.ydata
            if event.dblclick:
                pareto_points = datapoints[lst, :]
                dists = np.linalg.norm(np.array([x, y]) - pareto_points, axis=1)
                self.selected_idx = np.argmin(dists)
                print(dists)
                plt.close()

        # scatter pareto optimal solutions
        plt.connect('motion_notify_event', mouse_move)
        plt.connect('button_press_event', mouse_move)
        plt.scatter(datapoints[:, 0], datapoints[:, 1], s=1, c='blue', label='Non Pareto-optimal')
        plt.scatter(datapoints[lst, 0], datapoints[lst, 1], s=3, c='red', label='Pareto optimal')
        plt.xlabel('ccp_alpha')
        plt.ylabel('Accuracy (balanced)')
        plt.show()

        # train with selected hyperparameter
        selected_ccp = datapoints[lst[self.selected_idx], 0]
        print(selected_ccp)
        clf = DecisionTreeClassifier(random_state=0, class_weight="balanced", min_impurity_decrease=0.001,
                                     ccp_alpha=selected_ccp)

        clf.fit(self.X_train, self.y_train)

        # save estimator into estimators
        self.estimator = clf

        plot_tree(clf, feature_names=self.X_train.columns, class_names=["nein", "ja"])
        plt.show()

if __name__ == '__main__':
    explain = Explain()
    explain.explain()
