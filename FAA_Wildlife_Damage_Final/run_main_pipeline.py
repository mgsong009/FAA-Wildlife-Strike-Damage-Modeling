from __future__ import annotations

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import joblib

# 서버/노트북이 아닌 환경에서도 PNG를 저장할 수 있도록 GUI 없는 백엔드를 씁니다.
# Tkinter 백엔드를 쓰면 uv Python 환경에서 init.tcl 오류가 날 수 있습니다.
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from src.pipeline_core import (
    MAIN_FEATURES,
    TARGET,
    apply_category_maps,
    choose_threshold,
    detect_leakage_columns,
    make_modeling_frame,
    rare_category_maps,
    stratified_splits,
)

RANDOM_STATE = 42
RARE_MIN_COUNT = 50
PROJECT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = PROJECT_DIR.parent
SOURCE_XLSX = WORKSPACE_DIR / "FAA_0619_preprocessed_dataset_for_team.xlsx"

# 문서에서 제시한 Main Pipeline 산출물 폴더 구조입니다.
# 대시보드는 이번 1차 범위에서 제외했기 때문에 08_dashboard는 만들지 않습니다.
DIRS = {
    "config": PROJECT_DIR / "00_config",
    "data": PROJECT_DIR / "01_data",
    "internal_validation": PROJECT_DIR / "01_data" / "internal_validation",
    "models": PROJECT_DIR / "02_models",
    "predictions": PROJECT_DIR / "03_predictions",
    "metrics": PROJECT_DIR / "04_metrics",
    "figures": PROJECT_DIR / "05_figures",
    "tables": PROJECT_DIR / "06_tables",
    "reports": PROJECT_DIR / "07_reports",
    "submission": PROJECT_DIR / "submission_package",
}

# 필수 모델 3종입니다.
# class_weight="balanced"는 손상 클래스가 약 7%인 불균형 데이터를 보정하기 위한 설정입니다.
MODEL_SPECS = {
    "logistic": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE),
    "tree": DecisionTreeClassifier(
        max_depth=8,
        min_samples_leaf=20,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    ),
    "rf": RandomForestClassifier(
        n_estimators=200,
        max_depth=14,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),
}

MODEL_LABELS = {
    "logistic": "Logistic Regression",
    "tree": "Decision Tree",
    "rf": "RandomForest",
}


def ensure_dirs() -> None:
    """산출물 저장 폴더를 미리 생성합니다."""

    for directory in DIRS.values():
        directory.mkdir(parents=True, exist_ok=True)
    for subdir in ["data", "notebooks", "outputs/predictions", "outputs/metrics", "outputs/figures", "models", "report"]:
        (DIRS["submission"] / subdir).mkdir(parents=True, exist_ok=True)


def copy_source_data() -> None:
    """원본 엑셀을 결과 폴더 안에도 복사해 재현 가능한 입력 파일을 남깁니다."""

    target = DIRS["data"] / "processed_modeling_data_source.xlsx"
    if not target.exists():
        shutil.copy2(SOURCE_XLSX, target)


def load_source() -> pd.DataFrame:
    """최종 전처리 엑셀의 Final_Dataset 시트를 읽습니다."""

    if not SOURCE_XLSX.exists():
        raise FileNotFoundError(f"Source workbook not found: {SOURCE_XLSX}")
    return pd.read_excel(SOURCE_XLSX, sheet_name="Final_Dataset")


def fit_preprocessor(X_train: pd.DataFrame) -> dict[str, object]:
    """train 데이터만 사용해 희소 범주 매핑과 One-Hot Encoder를 학습합니다.

    validation/test까지 보고 전처리 기준을 만들면 평가 데이터 정보가 새어 들어가므로,
    이 함수는 반드시 학습용 데이터에만 호출합니다.
    """

    category_maps = rare_category_maps(X_train, MAIN_FEATURES, min_count=RARE_MIN_COUNT)
    X_grouped = apply_category_maps(X_train, category_maps)
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    encoder.fit(X_grouped)
    return {"category_maps": category_maps, "encoder": encoder, "features": MAIN_FEATURES}


def transform(preprocessor: dict[str, object], X: pd.DataFrame) -> pd.DataFrame:
    """학습된 전처리기를 사용해 입력 데이터를 모델용 숫자 행렬로 변환합니다."""

    grouped = apply_category_maps(X[MAIN_FEATURES], preprocessor["category_maps"])
    encoder: OneHotEncoder = preprocessor["encoder"]
    matrix = encoder.transform(grouped)
    columns = encoder.get_feature_names_out(MAIN_FEATURES)
    return pd.DataFrame(matrix, columns=columns, index=X.index)


def score_rows(model_name: str, split: str, y_true: pd.Series, y_proba: np.ndarray, threshold: float) -> dict[str, float | str]:
    """모델 하나와 split 하나에 대한 성능 지표 한 줄을 만듭니다."""

    y_pred = (y_proba >= threshold).astype(int)
    return {
        "model_name": MODEL_LABELS[model_name],
        "split": split,
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
    }


def prediction_frame(model_name: str, split: str, y_true: pd.Series, y_proba: np.ndarray, threshold: float) -> pd.DataFrame:
    """발표/검토용으로 실제값, 예측값, 손상 확률을 저장하는 표를 만듭니다."""

    return pd.DataFrame(
        {
            "y_true": y_true.astype(int).to_numpy(),
            "y_pred": (y_proba >= threshold).astype(int),
            "y_proba": y_proba,
            "model_name": MODEL_LABELS[model_name],
            "split": split,
        },
        index=y_true.index,
    ).reset_index(drop=True)


def risk_table(df: pd.DataFrame, column: str, min_count: int = 50) -> pd.DataFrame:
    """조건별 손상률과 전체 대비 위험 배율(risk_lift)을 계산합니다.

    min_count_pass는 표본이 너무 적은 범주를 발표에서 과해석하지 않기 위한 플래그입니다.
    """

    overall = df[TARGET].mean()
    table = (
        df.groupby(column, dropna=False)[TARGET]
        .agg(total_count="count", damage_count="sum", damage_rate="mean")
        .reset_index()
        .rename(columns={column: "category"})
    )
    table["overall_damage_rate"] = overall
    table["risk_lift"] = table["damage_rate"] / overall
    table["min_count_pass"] = table["total_count"] >= min_count
    return table.sort_values(["min_count_pass", "damage_rate", "total_count"], ascending=[False, False, False])


def aggregate_feature_importance(feature_names: list[str], importances: np.ndarray) -> pd.DataFrame:
    """One-Hot으로 쪼개진 중요도를 원래 변수 단위로 다시 합칩니다.

    예를 들어 SPECIES_Unknown bird, SPECIES_Barn swallow 같은 컬럼 중요도를
    발표에서는 SPECIES 하나의 변수 그룹으로 설명할 수 있게 만듭니다.
    """

    rows = []
    for encoded, importance in zip(feature_names, importances):
        base = next((feature for feature in MAIN_FEATURES if encoded.startswith(f"{feature}_")), encoded)
        rows.append({"encoded_feature": encoded, "feature": base, "importance": float(importance)})
    detail = pd.DataFrame(rows)
    grouped = detail.groupby("feature", as_index=False)["importance"].sum()
    return grouped.sort_values("importance", ascending=False), detail.sort_values("importance", ascending=False)


def write_data_outputs(modeling: pd.DataFrame, splits) -> None:
    """문서에서 요구한 train/test/internal_validation CSV 파일을 저장합니다."""

    modeling.to_csv(DIRS["data"] / "processed_modeling_data.csv", index=False, encoding="utf-8-sig")
    splits.X_train.to_csv(DIRS["data"] / "X_train.csv", index=False, encoding="utf-8-sig")
    splits.X_test.to_csv(DIRS["data"] / "X_test.csv", index=False, encoding="utf-8-sig")
    splits.y_train.to_frame(TARGET).to_csv(DIRS["data"] / "y_train.csv", index=False, encoding="utf-8-sig")
    splits.y_test.to_frame(TARGET).to_csv(DIRS["data"] / "y_test.csv", index=False, encoding="utf-8-sig")
    splits.X_fit.to_csv(DIRS["internal_validation"] / "X_fit.csv", index=False, encoding="utf-8-sig")
    splits.X_valid.to_csv(DIRS["internal_validation"] / "X_valid.csv", index=False, encoding="utf-8-sig")
    splits.y_fit.to_frame(TARGET).to_csv(DIRS["internal_validation"] / "y_fit.csv", index=False, encoding="utf-8-sig")
    splits.y_valid.to_frame(TARGET).to_csv(DIRS["internal_validation"] / "y_valid.csv", index=False, encoding="utf-8-sig")


def plot_target_distribution(df: pd.DataFrame) -> None:
    """손상/비손상 클래스 불균형을 보여주는 첫 번째 발표용 그래프입니다."""

    counts = df[TARGET].value_counts().sort_index()
    plt.figure(figsize=(7, 4))
    bars = plt.bar(["No Damage (0)", "Damage (1)"], counts.values, color=["#4B5563", "#DC2626"])
    plt.title("Target Distribution: Damage_Binary")
    plt.ylabel("Incident Count")
    for bar, count in zip(bars, counts.values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{count:,}", ha="center", va="bottom")
    plt.tight_layout()
    plt.savefig(DIRS["figures"] / "01_target_distribution.png", dpi=160)
    plt.close()


def plot_model_performance(metrics: pd.DataFrame) -> None:
    """기본 threshold 0.5 기준으로 모델별 Recall과 F1을 비교합니다."""

    test = metrics[(metrics["split"] == "test") & (metrics["threshold"] == 0.5)]
    x = np.arange(len(test))
    width = 0.35
    plt.figure(figsize=(8, 4.5))
    plt.bar(x - width / 2, test["recall"], width, label="Recall", color="#2563EB")
    plt.bar(x + width / 2, test["f1"], width, label="F1", color="#16A34A")
    plt.xticks(x, test["model_name"], rotation=15, ha="right")
    plt.ylim(0, 1)
    plt.title("Model Performance on Test Set")
    plt.legend()
    plt.tight_layout()
    plt.savefig(DIRS["figures"] / "02_model_performance_bar.png", dpi=160)
    plt.close()


def plot_confusion_matrix(cm: np.ndarray) -> None:
    """최종 모델과 선택 threshold 기준의 Confusion Matrix를 저장합니다."""

    plt.figure(figsize=(5, 4))
    plt.imshow(cm, cmap="Blues")
    plt.title("Final Model Confusion Matrix")
    plt.xticks([0, 1], ["Pred 0", "Pred 1"])
    plt.yticks([0, 1], ["True 0", "True 1"])
    for i in range(2):
        for j in range(2):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center", color="black")
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.savefig(DIRS["figures"] / "03_confusion_matrix_final.png", dpi=160)
    plt.close()


def plot_named_confusion_matrix(cm: np.ndarray, title: str, output_path: Path) -> None:
    """제출 패키지용 모델별 Confusion Matrix를 지정 파일명으로 저장합니다."""

    plt.figure(figsize=(5, 4))
    plt.imshow(cm, cmap="Blues")
    plt.title(title)
    plt.xticks([0, 1], ["Pred 0", "Pred 1"])
    plt.yticks([0, 1], ["True 0", "True 1"])
    for i in range(2):
        for j in range(2):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center", color="black")
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_curves(y_true: pd.Series, y_proba: np.ndarray) -> None:
    """최종 모델의 ROC Curve와 Precision-Recall Curve를 저장합니다."""

    fpr, tpr, _ = roc_curve(y_true, y_proba)
    precision, recall, _ = precision_recall_curve(y_true, y_proba)

    plt.figure(figsize=(6, 4))
    plt.plot(fpr, tpr, color="#2563EB")
    plt.plot([0, 1], [0, 1], "--", color="#9CA3AF")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.tight_layout()
    plt.savefig(DIRS["figures"] / "04_roc_curve.png", dpi=160)
    plt.close()

    plt.figure(figsize=(6, 4))
    plt.plot(recall, precision, color="#DC2626")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.tight_layout()
    plt.savefig(DIRS["figures"] / "05_pr_curve.png", dpi=160)
    plt.close()


def plot_model_curves(y_true: pd.Series, model_probabilities: dict[str, np.ndarray]) -> None:
    """제출 패키지 기준의 모델별 ROC/PR 통합 그래프를 저장합니다."""

    plt.figure(figsize=(6, 4))
    for model_name, y_proba in model_probabilities.items():
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        auc = roc_auc_score(y_true, y_proba)
        plt.plot(fpr, tpr, label=f"{MODEL_LABELS[model_name]} ({auc:.3f})")
    plt.plot([0, 1], [0, 1], "--", color="#9CA3AF")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve by Model")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(DIRS["submission"] / "outputs" / "figures" / "roc_curve.png", dpi=160)
    plt.close()

    plt.figure(figsize=(6, 4))
    for model_name, y_proba in model_probabilities.items():
        precision, recall, _ = precision_recall_curve(y_true, y_proba)
        ap = average_precision_score(y_true, y_proba)
        plt.plot(recall, precision, label=f"{MODEL_LABELS[model_name]} ({ap:.3f})")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve by Model")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(DIRS["submission"] / "outputs" / "figures" / "pr_curve.png", dpi=160)
    plt.close()


def plot_threshold(table: pd.DataFrame) -> None:
    """validation 데이터에서 threshold 변화에 따른 Precision/Recall/F1을 시각화합니다."""

    grid = table[table["criterion"] == "grid"].sort_values("threshold")
    plt.figure(figsize=(7, 4))
    plt.plot(grid["threshold"], grid["precision"], label="Precision", color="#7C3AED")
    plt.plot(grid["threshold"], grid["recall"], label="Recall", color="#EA580C")
    plt.plot(grid["threshold"], grid["f1"], label="F1", color="#16A34A")
    plt.xlabel("Threshold")
    plt.ylim(0, 1)
    plt.title("Validation Threshold Experiment")
    plt.legend()
    plt.tight_layout()
    plt.savefig(DIRS["figures"] / "06_threshold_precision_recall.png", dpi=160)
    plt.close()


def plot_feature_importance(feature_importance: pd.DataFrame) -> None:
    """최종 모델의 상위 변수 중요도를 발표용 막대그래프로 저장합니다."""

    top = feature_importance.head(20).sort_values("importance")
    plt.figure(figsize=(7, 6))
    plt.barh(top["feature"], top["importance"], color="#0891B2")
    plt.title("Top Feature Importance")
    plt.tight_layout()
    plt.savefig(DIRS["figures"] / "07_feature_importance_top20.png", dpi=160)
    plt.close()


def plot_condition_damage_rate(tables: dict[str, pd.DataFrame]) -> None:
    """조건별 손상률 표에서 표본 기준을 통과한 상위 위험 조건을 시각화합니다."""

    selected = []
    for name, table in tables.items():
        candidates = table[table["min_count_pass"]].head(5).copy()
        candidates["source"] = name
        selected.append(candidates)
    plot_df = pd.concat(selected, ignore_index=True).sort_values("damage_rate", ascending=False).head(15)
    labels = (plot_df["source"].astype(str) + ": " + plot_df["category"].astype(str)).tolist()
    values = plot_df["damage_rate"].astype(float).to_numpy()
    y_pos = np.arange(len(labels))
    plt.figure(figsize=(8, 6))
    plt.barh(y_pos, values[::-1], color="#B45309")
    plt.yticks(y_pos, labels[::-1])
    plt.xlabel("Damage Rate")
    plt.title("High-Risk Conditions by Damage Rate")
    plt.tight_layout()
    plt.savefig(DIRS["figures"] / "08_condition_damage_rate.png", dpi=160)
    plt.close()


def write_reports(
    raw: pd.DataFrame,
    modeling: pd.DataFrame,
    metrics: pd.DataFrame,
    selected_model: str,
    selected_threshold: dict[str, float | str],
    leakage_columns: list[str],
    duplicate_count: int,
    final_metrics: pd.DataFrame,
) -> None:
    """최종 발표와 검토에 바로 쓸 수 있는 Markdown 보고서 묶음을 작성합니다."""

    target_counts = raw[TARGET].value_counts().sort_index()
    missing = modeling[MAIN_FEATURES].isna().mean().mul(100).round(2)
    (DIRS["reports"] / "data_check_summary.md").write_text(
        "\n".join(
            [
                "# Data Check Summary",
                "",
                f"- Source rows: {len(raw):,}",
                f"- Source columns: {raw.shape[1]:,}",
                f"- Duplicate full rows: {duplicate_count:,}",
                f"- Modeling rows after duplicate removal: {len(modeling):,}",
                f"- Target counts: 0={int(target_counts.get(0, 0)):,}, 1={int(target_counts.get(1, 0)):,}",
                f"- Damage rate: {raw[TARGET].mean():.4%}",
                f"- Leakage columns detected and excluded: {', '.join(leakage_columns)}",
                "",
                "## Main Feature Missing Rate",
                missing.to_frame("missing_pct").to_csv(),
            ]
        ),
        encoding="utf-8",
    )

    best = metrics[(metrics["split"] == "valid") & (metrics["model_name"] == MODEL_LABELS[selected_model])].iloc[0]
    final_row = final_metrics.iloc[0]
    (DIRS["reports"] / "final_model_selection.md").write_text(
        "\n".join(
            [
                "# Final Model Selection",
                "",
                "Accuracy alone was not used because the damage class is rare.",
                f"- Selected model: {MODEL_LABELS[selected_model]}",
                f"- Validation F1 at default threshold: {best['f1']:.4f}",
                f"- Validation Recall at default threshold: {best['recall']:.4f}",
                f"- Selected threshold criterion: {selected_threshold['criterion']}",
                f"- Selected threshold: {selected_threshold['threshold']:.2f}",
                f"- Final test Recall: {final_row['recall']:.4f}",
                f"- Final test F1: {final_row['f1']:.4f}",
                f"- Final test PR-AUC: {final_row['pr_auc']:.4f}",
            ]
        ),
        encoding="utf-8",
    )

    (DIRS["reports"] / "insight_summary.md").write_text(
        "\n".join(
            [
                "# Insight Summary",
                "",
                "- The model is a post-strike aircraft damage screening model, not a wildlife strike occurrence model.",
                "- Recall and F1 are emphasized because missed damage cases are more important than raw accuracy.",
                "- Risk tables should be interpreted as conditional damage rates within reported strike incidents.",
                "- Airport or operator risk should not be overclaimed because flight exposure denominators are not included.",
            ]
        ),
        encoding="utf-8",
    )

    (DIRS["reports"] / "limitations.md").write_text(
        "\n".join(
            [
                "# Limitations",
                "",
                "- The dataset contains reported strike incidents only; it does not include all flights or non-reported events.",
                "- The model predicts damage after a strike has occurred and should not be described as strike occurrence prediction.",
                "- High-cardinality categories are grouped into Other to reduce overfitting and improve presentation stability.",
                "- Threshold tuning used validation data; the test set was reserved for final evaluation.",
            ]
        ),
        encoding="utf-8",
    )

    (DIRS["reports"] / "presentation_key_messages.md").write_text(
        "\n".join(
            [
                "# Presentation Key Messages",
                "",
                "1. This project predicts aircraft damage risk after FAA wildlife strike incidents.",
                "2. The target class is imbalanced, with damage cases around 7%.",
                "3. Leakage-prone post-incident fields such as DAMAGE_LEVEL, STR_*, and ING_* were excluded.",
                "4. Final model selection focused on Recall and F1, not Accuracy.",
                "5. Validation data was used for threshold selection, while Test data was used only for final evaluation.",
            ]
        ),
        encoding="utf-8",
    )


def write_minimal_docx(path: Path, title: str, lines: list[str]) -> None:
    """외부 문서 라이브러리 없이 간단한 Word 문서를 생성합니다.

    제출 패키지의 preprocessing_log.docx처럼 형식보다 내용 기록이 중요한 문서에 사용합니다.
    """

    paragraphs = [title] + lines
    body = "".join(
        f"<w:p><w:r><w:t>{escape(str(paragraph))}</w:t></w:r></w:p>"
        for paragraph in paragraphs
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}<w:sectPr/></w:body></w:document>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        "</Relationships>"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/document.xml", document_xml)


def write_notebook(path: Path, title: str, markdown_lines: list[str], code_lines: list[str]) -> None:
    """로드맵에서 요구한 ipynb 파일명을 맞추기 위한 실행 가능한 노트북 틀을 만듭니다."""

    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# {title}\n"] + [f"{line}\n" for line in markdown_lines],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [f"{line}\n" for line in code_lines],
            },
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")


def write_submission_package(
    splits,
    feature_names: list[str],
    metrics: pd.DataFrame,
    final_metrics: pd.DataFrame,
    selected_key: str,
    selected_threshold: dict[str, float | str],
    validation_probs: dict[str, np.ndarray],
    test_predictions: dict[str, np.ndarray],
    leakage_columns: list[str],
    duplicate_count: int,
) -> None:
    """8주차 로드맵 제출 파일명에 맞춘 패키지를 생성합니다."""

    package = DIRS["submission"]
    data_dir = package / "data"
    outputs = package / "outputs"
    predictions_dir = outputs / "predictions"
    metrics_dir = outputs / "metrics"
    figures_dir = outputs / "figures"
    models_dir = package / "models"
    report_dir = package / "report"
    notebooks_dir = package / "notebooks"

    copy_pairs = [
        (DIRS["data"] / "X_train.csv", data_dir / "X_train.csv"),
        (DIRS["data"] / "X_test.csv", data_dir / "X_test.csv"),
        (DIRS["data"] / "y_train.csv", data_dir / "y_train.csv"),
        (DIRS["data"] / "y_test.csv", data_dir / "y_test.csv"),
        (DIRS["predictions"] / "logistic_predictions.csv", predictions_dir / "logistic_predictions.csv"),
        (DIRS["predictions"] / "tree_predictions.csv", predictions_dir / "tree_predictions.csv"),
        (DIRS["predictions"] / "rf_predictions.csv", predictions_dir / "rf_predictions.csv"),
        (DIRS["metrics"] / "metrics_table.csv", metrics_dir / "metrics_table.csv"),
        (DIRS["metrics"] / "final_model_metrics.csv", metrics_dir / "final_model_metrics.csv"),
        (DIRS["metrics"] / "final_confusion_matrix.csv", metrics_dir / "final_confusion_matrix.csv"),
        (DIRS["models"] / "logistic_model.pkl", models_dir / "logistic_model.pkl"),
        (DIRS["models"] / "tree_model.pkl", models_dir / "tree_model.pkl"),
        (DIRS["models"] / "rf_model.pkl", models_dir / "rf_model.pkl"),
        (DIRS["models"] / "final_model.pkl", models_dir / "final_model.pkl"),
        (DIRS["reports"] / "final_model_selection.md", report_dir / "최종모델_선정근거.md"),
        (DIRS["reports"] / "insight_summary.md", report_dir / "최종_인사이트_요약본.md"),
        (DIRS["reports"] / "limitations.md", report_dir / "데이터처리_및_한계정리.md"),
    ]
    for source, target in copy_pairs:
        shutil.copy2(source, target)

    pd.DataFrame({"feature": feature_names}).to_csv(data_dir / "feature_columns.csv", index=False, encoding="utf-8-sig")

    split_summary = pd.DataFrame(
        [
            {"split": "train", "rows": len(splits.X_train), "damage_rate": float(splits.y_train.mean())},
            {"split": "test", "rows": len(splits.X_test), "damage_rate": float(splits.y_test.mean())},
            {"split": "fit", "rows": len(splits.X_fit), "damage_rate": float(splits.y_fit.mean())},
            {"split": "valid", "rows": len(splits.X_valid), "damage_rate": float(splits.y_valid.mean())},
        ]
    )
    column_check = pd.DataFrame(
        {
            "check_item": ["X_train_columns", "X_test_columns", "columns_match"],
            "value": [splits.X_train.shape[1], splits.X_test.shape[1], list(splits.X_train.columns) == list(splits.X_test.columns)],
        }
    )
    leakage_check = pd.DataFrame({"excluded_leakage_column": leakage_columns})
    with pd.ExcelWriter(metrics_dir / "평가데이터_검증표.xlsx", engine="openpyxl") as writer:
        split_summary.to_excel(writer, sheet_name="split_summary", index=False)
        column_check.to_excel(writer, sheet_name="column_check", index=False)
        leakage_check.to_excel(writer, sheet_name="leakage_check", index=False)

    threshold_rows = []
    roc_auc = float(roc_auc_score(splits.y_valid, validation_probs[selected_key]))
    for threshold in [0.5, 0.4, 0.3, 0.2]:
        y_pred = (validation_probs[selected_key] >= threshold).astype(int)
        threshold_rows.append(
            {
                "model": MODEL_LABELS[selected_key],
                "threshold": threshold,
                "accuracy": float(accuracy_score(splits.y_valid, y_pred)),
                "precision": float(precision_score(splits.y_valid, y_pred, zero_division=0)),
                "recall": float(recall_score(splits.y_valid, y_pred, zero_division=0)),
                "f1": float(f1_score(splits.y_valid, y_pred, zero_division=0)),
                "roc_auc": roc_auc,
            }
        )
    pd.DataFrame(threshold_rows).to_csv(metrics_dir / "threshold_result.csv", index=False, encoding="utf-8-sig")

    shutil.copy2(DIRS["figures"] / "02_model_performance_bar.png", figures_dir / "model_performance_bar.png")
    for model_name, y_proba in test_predictions.items():
        y_pred = (y_proba >= 0.5).astype(int)
        cm = confusion_matrix(splits.y_test, y_pred)
        plot_named_confusion_matrix(cm, f"{MODEL_LABELS[model_name]} Confusion Matrix", figures_dir / f"confusion_matrix_{model_name}.png")
    plot_model_curves(splits.y_test, test_predictions)
    shutil.copy2(DIRS["figures"] / "07_feature_importance_top20.png", figures_dir / "feature_importance.png")
    shutil.copy2(DIRS["figures"] / "08_condition_damage_rate.png", figures_dir / "condition_damage_rate.png")

    write_minimal_docx(
        report_dir / "preprocessing_log.docx",
        "전처리 로그",
        [
            "원본 데이터: FAA_0619_preprocessed_dataset_for_team.xlsx / Final_Dataset",
            "목표변수: Damage_Binary",
            "중복 행 처리: 전체 중복 행 5건 제거 후 모델링 데이터 생성",
            "입력변수: 8주차 기준 Main Feature 15개 사용",
            "제외변수: DAMAGE_LEVEL, DAM_*, STR_*, ING_* 등 누수 위험 변수 제외",
            "희소 범주 처리: train 기준 빈도 50 미만 범주는 Other로 통합",
            "인코딩: train 기준 One-Hot Encoder fit, validation/test에는 transform만 적용",
            "분할: Train/Test 80:20 stratify 적용, Train 내부 validation 추가 분리",
        ],
    )

    write_notebook(
        notebooks_dir / "01_preprocessing_pipeline.ipynb",
        "Preprocessing Pipeline",
        ["8주차 변수목록표 기준으로 전처리와 분할 산출물을 생성합니다."],
        ["# 전체 파이프라인 실행", "%run ../../run_main_pipeline.py"],
    )
    write_notebook(
        notebooks_dir / "02_model_training.ipynb",
        "Model Training",
        ["Logistic Regression, Decision Tree, RandomForest 모델 학습 결과를 확인합니다."],
        ["import pandas as pd", "pd.read_csv('../outputs/metrics/metrics_table.csv')"],
    )
    write_notebook(
        notebooks_dir / "03_model_evaluation.ipynb",
        "Model Evaluation",
        ["모델별 성능표, threshold 실험, confusion matrix, ROC/PR 산출물을 확인합니다."],
        ["import pandas as pd", "pd.read_csv('../outputs/metrics/threshold_result.csv')"],
    )
    write_notebook(
        notebooks_dir / "04_interpretation_visualization.ipynb",
        "Interpretation Visualization",
        ["Feature Importance와 조건별 손상률 그래프를 확인합니다."],
        ["import pandas as pd", "pd.read_csv('../../06_tables/feature_importance.csv').head(20)"],
    )
    write_notebook(
        notebooks_dir / "modeling_main.ipynb",
        "Modeling Main",
        ["제출 패키지 전체 실행 진입점입니다."],
        ["# 전체 Main Pipeline 실행", "%run ../../run_main_pipeline.py"],
    )

    with zipfile.ZipFile(outputs / "presentation_figures.zip", "w", zipfile.ZIP_DEFLATED) as zipped:
        for figure in figures_dir.glob("*.png"):
            zipped.write(figure, arcname=figure.name)

    package_zip = PROJECT_DIR / "submission_package.zip"
    with zipfile.ZipFile(package_zip, "w", zipfile.ZIP_DEFLATED) as zipped:
        for file_path in package.rglob("*"):
            if file_path.is_file():
                zipped.write(file_path, arcname=file_path.relative_to(package.parent))

    summary_lines = [
        "# 제출 패키지 요약",
        "",
        "- 기준 문서: 8주차 모델링 설계/변수목록/모델실험/평가시각화 계획 반영",
        f"- 최종 모델: {MODEL_LABELS[selected_key]}",
        f"- 선택 threshold: {float(selected_threshold['threshold']):.2f}",
        f"- threshold 선택 기준: {selected_threshold['criterion']}",
        f"- Test Recall: {float(final_metrics.iloc[0]['recall']):.4f}",
        f"- Test F1: {float(final_metrics.iloc[0]['f1']):.4f}",
        f"- 원본 중복 제거 행 수: {duplicate_count}",
    ]
    (package / "README_SUBMISSION.md").write_text("\n".join(summary_lines), encoding="utf-8")


def main() -> None:
    """Main Pipeline 전체 실행 순서입니다.

    큰 흐름은 데이터 검증 -> split -> validation 기반 모델/threshold 선택 ->
    train 전체 재학습 -> test 최종 평가 -> 산출물 저장입니다.
    """

    ensure_dirs()
    copy_source_data()
    raw = load_source()

    # 원본 데이터 품질과 누수 후보는 보고서에 남기되,
    # 실제 모델 입력은 make_modeling_frame에서 Main 변수만 선택합니다.
    leakage_columns = detect_leakage_columns(raw.columns)
    duplicate_count = int(raw.duplicated().sum())
    raw_no_duplicates = raw.drop_duplicates().reset_index(drop=True)
    modeling = make_modeling_frame(raw_no_duplicates)

    # 공식 test는 최종 평가 전용입니다.
    # threshold 조정은 train 내부의 validation에서만 수행합니다.
    splits = stratified_splits(modeling, random_state=RANDOM_STATE)
    write_data_outputs(modeling, splits)
    plot_target_distribution(raw_no_duplicates)

    # 1단계 학습: X_fit으로 학습하고 X_valid로 모델 비교와 threshold 선택을 합니다.
    validation_preprocessor = fit_preprocessor(splits.X_fit)
    X_fit_encoded = transform(validation_preprocessor, splits.X_fit)
    X_valid_encoded = transform(validation_preprocessor, splits.X_valid)
    metrics_rows = []
    validation_probs = {}

    for model_name, model in MODEL_SPECS.items():
        model.fit(X_fit_encoded, splits.y_fit)
        valid_proba = model.predict_proba(X_valid_encoded)[:, 1]
        validation_probs[model_name] = valid_proba
        metrics_rows.append(score_rows(model_name, "valid", splits.y_valid, valid_proba, 0.5))

    metrics_valid = pd.DataFrame(metrics_rows)

    # 최종 후보 모델은 validation의 F1, Recall, PR-AUC 순으로 고릅니다.
    # Accuracy는 불균형 데이터에서 과대평가될 수 있어 선택 기준으로 쓰지 않습니다.
    selected_model = (
        metrics_valid.sort_values(["f1", "recall", "pr_auc"], ascending=False).iloc[0]["model_name"]
    )
    selected_key = {v: k for k, v in MODEL_LABELS.items()}[selected_model]

    # threshold 역시 test가 아니라 validation 예측확률로만 선택합니다.
    threshold_table, selected_threshold = choose_threshold(splits.y_valid, validation_probs[selected_key])
    threshold_table.insert(0, "model_name", MODEL_LABELS[selected_key])
    threshold_table.to_csv(DIRS["metrics"] / "threshold_experiment_valid.csv", index=False, encoding="utf-8-sig")

    # 2단계 학습: 모델과 threshold가 결정된 뒤 train 전체로 다시 학습해 test에 평가합니다.
    full_preprocessor = fit_preprocessor(splits.X_train)
    X_train_encoded = transform(full_preprocessor, splits.X_train)
    X_test_encoded = transform(full_preprocessor, splits.X_test)
    feature_names = list(X_train_encoded.columns)
    joblib.dump(full_preprocessor, DIRS["models"] / "preprocessing_pipeline.pkl")

    test_metric_rows = []
    fitted_models = {}
    test_predictions = {}
    for model_name, model in MODEL_SPECS.items():
        model.fit(X_train_encoded, splits.y_train)
        fitted_models[model_name] = model
        joblib.dump(model, DIRS["models"] / f"{model_name if model_name != 'tree' else 'tree'}_model.pkl")
        test_proba = model.predict_proba(X_test_encoded)[:, 1]
        test_predictions[model_name] = test_proba
        test_metric_rows.append(score_rows(model_name, "test", splits.y_test, test_proba, 0.5))
        prediction_frame(model_name, "test", splits.y_test, test_proba, 0.5).to_csv(
            DIRS["predictions"] / f"{model_name}_predictions.csv",
            index=False,
            encoding="utf-8-sig",
        )

    metrics = pd.concat([metrics_valid, pd.DataFrame(test_metric_rows)], ignore_index=True)
    metrics.to_csv(DIRS["metrics"] / "metrics_table.csv", index=False, encoding="utf-8-sig")
    plot_model_performance(metrics)

    # 최종 평가는 validation에서 고른 모델과 threshold를 test에 한 번만 적용합니다.
    final_model = fitted_models[selected_key]
    final_threshold = float(selected_threshold["threshold"])
    final_proba = test_predictions[selected_key]
    final_pred = (final_proba >= final_threshold).astype(int)
    final_metrics = pd.DataFrame([score_rows(selected_key, "test_final_threshold", splits.y_test, final_proba, final_threshold)])
    final_metrics.to_csv(DIRS["metrics"] / "final_model_metrics.csv", index=False, encoding="utf-8-sig")
    final_cm = confusion_matrix(splits.y_test, final_pred)
    pd.DataFrame(final_cm, index=["true_0", "true_1"], columns=["pred_0", "pred_1"]).to_csv(
        DIRS["metrics"] / "final_confusion_matrix.csv",
        encoding="utf-8-sig",
    )
    prediction_frame(selected_key, "test", splits.y_test, final_proba, final_threshold).to_csv(
        DIRS["predictions"] / "final_model_predictions.csv",
        index=False,
        encoding="utf-8-sig",
    )
    joblib.dump(
        {
            "model_name": MODEL_LABELS[selected_key],
            "preprocessor": full_preprocessor,
            "model": final_model,
            "threshold": final_threshold,
            "threshold_criterion": selected_threshold["criterion"],
            "features": MAIN_FEATURES,
        },
        DIRS["models"] / "final_model.pkl",
    )

    plot_confusion_matrix(final_cm)
    plot_curves(splits.y_test, final_proba)
    plot_threshold(threshold_table)

    # Tree/RF는 feature_importances_, Logistic은 절댓값 계수를 중요도 대용으로 사용합니다.
    if hasattr(final_model, "feature_importances_"):
        grouped_importance, detail_importance = aggregate_feature_importance(feature_names, final_model.feature_importances_)
    else:
        grouped_importance, detail_importance = aggregate_feature_importance(feature_names, np.abs(final_model.coef_[0]))
    grouped_importance.to_csv(DIRS["tables"] / "feature_importance.csv", index=False, encoding="utf-8-sig")
    detail_importance.to_csv(DIRS["tables"] / "feature_importance_encoded.csv", index=False, encoding="utf-8-sig")
    plot_feature_importance(grouped_importance)

    risk_columns = {
        "month": "INCIDENT_MONTH",
        "time_of_day": "TIME_OF_DAY",
        "phase": "PHASE_OF_FLIGHT",
        "altitude_group": "ALTITUDE_GROUP",
        "distance_group": "DISTANCE_GROUP",
        "species": "SPECIES",
        "size": "SIZE_CLEAN",
        "num_struck": "NUM_STRUCK",
        "ac_class": "AC_CLASS",
        "ac_mass": "AC_MASS",
    }

    # 조건별 손상률 표는 모델 성능이 아니라 해석/발표용 EDA 산출물입니다.
    risk_tables = {}
    for file_stem, column in risk_columns.items():
        table = risk_table(modeling, column)
        risk_tables[file_stem] = table
        table.to_csv(DIRS["tables"] / f"risk_by_{file_stem}.csv", index=False, encoding="utf-8-sig")
    plot_condition_damage_rate(risk_tables)

    write_reports(
        raw,
        modeling,
        metrics,
        selected_key,
        selected_threshold,
        leakage_columns,
        duplicate_count,
        final_metrics,
    )

    write_submission_package(
        splits,
        feature_names,
        metrics,
        final_metrics,
        selected_key,
        selected_threshold,
        validation_probs,
        test_predictions,
        leakage_columns,
        duplicate_count,
    )

    summary = {
        "rows": int(len(modeling)),
        "damage_rate": float(modeling[TARGET].mean()),
        "selected_model": MODEL_LABELS[selected_key],
        "selected_threshold": final_threshold,
        "selected_threshold_criterion": selected_threshold["criterion"],
        "final_metrics": final_metrics.iloc[0].to_dict(),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        raise
