import pytest
from rapp.gui.widgets.prediction_views import LoadedModelWidget

from tests.gui.fixture import gui, GuiTestApi
from tests import resources as rc


def test_no_loaded_models(gui: GuiTestApi):
    actual = len(gui.loadedModels)
    expected = 0
    assert actual == expected, \
        f"The Number of loaded models at the beginning should be {expected}, but is {actual}"


def test_load_model_as_dict(gui: GuiTestApi):
    path = rc.get_path('prediction/models/clf_svc.joblib')
    gui.load_model(path)

    actual = len(gui.loadedModels)
    expected = 1
    assert actual == expected, \
        f"The Number of loaded models after loading should be {expected}, but is {actual}"


def test_loaded_model_type(gui: GuiTestApi):
    path = rc.get_path('prediction/models/clf_svc.joblib')
    gui.load_model(path)

    actual = type(gui.loadedModels[0])
    expected = LoadedModelWidget
    assert actual == expected, \
        f"The type of loaded models should be {expected}, but is {actual}"


def test_load_model_as_pickle(gui: GuiTestApi):
    path = rc.get_path('prediction/models/clf_svc.pickle')
    gui.load_model(path)

    actual = len(gui.loadedModels)
    expected = 1
    assert actual == expected, \
        f"The Number of loaded models after loading should be {expected}, but is {actual}"


def test_loaded_model_target_set_on_last_feature(gui: GuiTestApi):
    path = rc.get_path('prediction/models/clf_svc.joblib')
    gui.load_model(path)

    last_feature = gui.get_pred_df().columns[-1]

    actual = gui.loadedModels[0].cbTarget.currentText()
    expected = last_feature
    assert actual == expected, \
        f"The default target should be {expected}, but is {actual}"


def test_loading_model_as_pickle_does_not_update_template_ids(gui: GuiTestApi):
    path = rc.get_path('prediction/models/clf_svc.pickle')

    f_id, l_id = gui.get_pred_template_ids()
    gui.load_model(path)

    actual = f_id, l_id
    expected = None, None
    assert actual == expected, \
        f"The the current templates should be {expected}, but are {actual}"


def test_loading_model_as_dict_updates_template_ids(gui: GuiTestApi):
    path = rc.get_path('prediction/models/clf_svc.joblib')
    gui.load_model(path)

    f_id, l_id = gui.get_pred_template_ids()

    actual = f_id, l_id
    expected = 'cs_first_term_modules', '3_dropout'
    assert actual == expected, \
        f"The the current templates should be {expected}, but are {actual}"


def test_loaded_model_target_does_not_show_prediction(gui: GuiTestApi):
    path = rc.get_path('prediction/models/clf_svc.joblib')
    gui.load_model(path)

    actual = len(gui.loadedModels[0].layout())
    # remove button, model name, stretch, and target comboBox
    expected = 4
    assert actual == expected, \
        f"The loaded model layout length should be {expected}, but is {actual}"


@pytest.fixture
def prediction_clf_reg(gui: GuiTestApi):
    models = ['clf_svc.joblib', 'reg_dt.joblib']

    for model in models:
        path = rc.get_path(f'prediction/models/{model}')
        gui.load_model(path)
    return gui


def test_remove_model(prediction_clf_reg: GuiTestApi):
    # only test removing the first model
    prediction_clf_reg.predictionView._remove_model(0)

    actual = [(model.modelLabel.text(), model.index) for model in prediction_clf_reg.loadedModels]
    # model name and index
    expected = [('reg_dt.joblib', 0)]
    assert actual == expected, \
        f"The loaded model should be {expected}, but is {actual}"


def test_predict_shows_pred_and_proba_labels(prediction_clf_reg: GuiTestApi):
    prediction_clf_reg.predict()

    actual = len(prediction_clf_reg.loadedModels[0].layout())
    # remove button, model name, stretch, target comboBox, stretch, pred label, and proba label
    expected = 7
    assert actual == expected, \
        f"The loaded model layout length should be {expected}, but is {actual}"


def test_predict_shows_correct_values_clf(gui: GuiTestApi):
    path = rc.get_path('prediction/models/clf_svc.joblib')
    gui.load_model(path)
    path = rc.get_path('prediction/models/clf_svc.pickle')
    gui.load_model(path)
    gui.select_pred_row(0, 0)  # predict only the first sample
    gui.predict()

    actual = [(model.predLabel.text(), model.probaLabel.text()) for model in gui.loadedModels]
    expected = [('1', '0.849'), ('1', '0.849')]
    assert actual == expected, \
        f"The predictions of the models should be {expected}, but is {actual}"


def test_predict_shows_correct_values_reg(gui: GuiTestApi):
    path = rc.get_path('prediction/models/reg_dt.joblib')
    gui.load_model(path)
    path = rc.get_path('prediction/models/reg_dt.pickle')
    gui.load_model(path)
    gui.select_pred_row(0, 0)  # predict only the first sample
    gui.predict()

    actual = [(model.predLabel.text(), model.probaLabel.text()) for model in gui.loadedModels]
    expected = [('3.600', '-'), ('3.600', '-')]
    assert actual == expected, \
        f"The predictions of the models should be {expected}, but is {actual}"


def test_predict_without_ensemble(prediction_clf_reg: GuiTestApi):
    prediction_clf_reg.select_pred_row(0, 0)  # predict only the first sample
    prediction_clf_reg.predict()

    actual = len(prediction_clf_reg.ensembleLabels)
    expected = 0
    assert actual == expected, \
        f"The ensemble labels dict length should be {expected}, but is {actual}"


def test_predict_clf_with_ensemble(prediction_clf_reg: GuiTestApi):
    path = rc.get_path('prediction/models/clf_svc.joblib')
    prediction_clf_reg.load_model(path)

    prediction_clf_reg.select_pred_row(0, 0)  # predict only the first sample
    prediction_clf_reg.predict()

    ensemble = prediction_clf_reg.ensembleLabels
    values = {}

    for target, pred in ensemble.items():
        values[target.text()] = pred.text()

    actual = values
    expected = {'Dropout': '1.000'}

    assert actual == expected, \
        f"The ensemble labels dict should be {expected}, but is {actual}"


def test_predict_reg_with_ensemble(prediction_clf_reg: GuiTestApi):
    path = rc.get_path('prediction/models/reg_dt.joblib')
    prediction_clf_reg.load_model(path)

    prediction_clf_reg.select_pred_row(0, 0)  # predict only the first sample
    prediction_clf_reg.predict()

    ensemble = prediction_clf_reg.ensembleLabels
    values = {}

    for target, pred in ensemble.items():
        values[target.text()] = pred.text()

    actual = values
    expected = {'Finalgrade': '3.600'}

    assert actual == expected, \
        f"The ensemble labels dict should be {expected}, but is {actual}"
