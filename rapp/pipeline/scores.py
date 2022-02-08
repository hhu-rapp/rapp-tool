from sklearn.metrics import accuracy_score
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score


def classification_scores():
    scores = {
        'Accuracy': accuracy_score,
        'Balanced Accuracy': balanced_accuracy_score,
        'F1': lambda x, y: f1_score(x, y, average='macro'),
        'Recall': lambda x, y: recall_score(x, y, average='macro'),
        'Precision': lambda x, y: precision_score(x, y, average='macro'),
        'Area under ROC': lambda x, y: roc_auc_score(x, y, multi_class='ovr')
    }

    return scores
