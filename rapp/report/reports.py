import os
import json
import shutil
import subprocess
import logging
log = logging.getLogger('rapp.pipeline')
import joblib

from rapp.report import latex
from rapp.report import resources as rc

from rapp.util import estimator_name


def save_report(pipeline):
    """
    Writes report with results stored in the `pipeline`.

    Parameters
    ----------
    pipeline : Pipeline instance
    """

    if pipeline.report_path is not None:
        path = pipeline.report_path
    else:
        path="reports"

    report_data = {}
    report_data["statistics"] = pipeline.statistics_results
    report_data["fairness"] = pipeline.fairness_results
    report_data["performance"] = pipeline.performance_results
    report_data["cross_validation"] = pipeline.cross_validation

    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        log.error(f"Could not write report to {path}:", e)

    # FIXME: can't dump report as Json because keys need to be str
    # with open(os.path.join(path, "report.json"), 'w') as r:
    #     json.dump(report_data, r, indent=2)

    latex_report_file = os.path.join(path, "report.tex")
    log.info("Writing LaTeX report to %s", latex_report_file)

    if pipeline.type == "classification":
        with open(latex_report_file, 'w') as f:
            tex = latex.tex_classification_report(report_data)
            f.write(tex)

    if pipeline.type == "regression":
        log.error("Regression reports not yet implemented")
        pass

    with rc.get_path("hhulogo.pdf") as logo:
        shutil.copy(logo, path)
    with rc.get_path("hhuarticle.cls") as cls_file:
        shutil.copy(cls_file, path)

    # Attempt to compile latex report
    try:
        log.info("Compiling report.tex with latexmk: %s",
                     latex_report_file)
        subprocess.check_call([
            "latexmk",
            "-pdf",
            # "-jobname=" + os.path.join(path, "report.pdf"),
            r'-pdflatex=pdflatex -interaction=nonstopmode',
            "report.tex"
        ], cwd=path)
    except subprocess.CalledProcessError as e:
        log.error("Unable to compile the report file %s: %s",
                      latex_report_file, e)

    if report_data['performance']:
        for est, data in report_data['performance'].items():
            write_estimator_report(est, data, path)


def write_estimator_report(est, performance_data, path):
    """
    Writes performance data of an estimator. The performance scores are
    saved as a .csv, and the confusion_matrix as a .txt file.

    Parameters
    ----------
    estimator : Scikit-learn estimator
        Evaluated estimator

    performance_data : dict
        Nested dictionary matching the format for Pipeline.performance_results.

    path : str
        path were the reports are saved
    """
    est_name = estimator_name(est)

    set_name = lambda file: os.path.join(path, est_name, file)

    est_path = set_name("")
    try:
        os.makedirs(est_path, exist_ok=True)
    except OSError as e:
        log.error(f"Could not write report to {est_path}:", e)

    scores_file = set_name("scores.csv")
    with open(scores_file, 'w') as scr:
        scr.write("Metric,Train,Test\n")
        for metric in performance_data["train"]["scores"].keys():
            scr.write(metric + ",")
            scr.write(str(performance_data["train"]["scores"][metric]) + ",")
            scr.write(str(performance_data["test"]["scores"][metric]) + "\n")

    cm_file = set_name('confusion_matrix.json')
    with open(cm_file, 'w') as f:
        confusion_dict = {
            'train': performance_data["train"]["confusion_matrix"],
            'test': performance_data["test"]["confusion_matrix"]
        }
        json.dump(confusion_dict, f, indent=2)
