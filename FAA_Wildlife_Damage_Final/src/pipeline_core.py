from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, fbeta_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

TARGET = "Damage_Binary"

# 문서에서 확정한 Main Model 입력 변수입니다.
# 손상 여부를 직접 알려주는 사후 결과 변수는 넣지 않고,
# 사고 발생 시점/충돌 상황에서 확인 가능한 변수만 사용합니다.
MAIN_FEATURES = [
    "INCIDENT_MONTH",
    "TIME_OF_DAY",
    "PHASE_OF_FLIGHT",
    "ALTITUDE_GROUP",
    "DISTANCE_GROUP",
    "SPECIES",
    "SIZE_CLEAN",
    "NUM_STRUCK",
    "AC_CLASS",
    "AC_MASS",
    "TYPE_ENG",
    "NUM_ENGS",
    "FAAREGION",
    "STATE",
    "SKY_CLEAN",
]

# 모델 입력에 들어가면 정답을 미리 알려줄 수 있는 컬럼입니다.
# 특히 DAMAGE_LEVEL은 Damage_Binary의 원본이므로 반드시 제외해야 합니다.
LEAKAGE_EXACT = {
    "DAMAGE_LEVEL",
    "INDICATED_DAMAGE",
    "COST_REPAIRS",
    "COST_OTHER",
    "AOS",
    "EFFECT",
    "INDEX_NR",
    "index",
    "REG",
    "FLT",
    "REMARKS",
    "COMMENTS",
    "REMAINS_COLLECTED",
    "REMAINS_SENT",
}

# DAM_*, STR_*, ING_* 계열은 충돌 이후 기록된 손상/부위/흡입 정보입니다.
# 항공안전 위험 스크리닝 모델에서는 데이터 누수로 보아 입력에서 제외합니다.
LEAKAGE_PREFIXES = ("DAM_", "STR_", "ING_")


@dataclass
class SplitData:
    """공식 train/test와 threshold 조정용 내부 validation split을 함께 보관합니다."""

    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    X_fit: pd.DataFrame
    X_valid: pd.DataFrame
    y_fit: pd.Series
    y_valid: pd.Series


def detect_leakage_columns(columns: Iterable[str]) -> list[str]:
    """데이터에 존재하는 누수 위험 컬럼을 보고서에 남기기 위해 찾습니다."""

    leakage = []
    for column in columns:
        if column in LEAKAGE_EXACT or column.startswith(LEAKAGE_PREFIXES):
            leakage.append(column)
    return leakage


def make_modeling_frame(df: pd.DataFrame) -> pd.DataFrame:
    """원본 데이터에서 Main Model 변수와 target만 남긴 모델링 프레임을 만듭니다."""

    missing = [column for column in MAIN_FEATURES + [TARGET] if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df[MAIN_FEATURES + [TARGET]].copy()


def rare_category_maps(
    train: pd.DataFrame,
    categorical_columns: list[str],
    min_count: int = 50,
    rare_label: str = "Other",
    missing_label: str = "Unknown",
) -> dict[str, dict[str, str]]:
    """train 데이터 기준으로 희소 범주를 Other로 묶는 매핑을 만듭니다.

    SPECIES처럼 고유값이 많은 변수는 그대로 One-Hot Encoding하면 차원이 커지고
    test/valid에만 등장하는 범주에 취약해집니다. 그래서 train에서 최소 빈도 기준을
    만족하지 못한 범주는 Other로 묶습니다.
    """

    maps: dict[str, dict[str, str]] = {}
    prepared = train[categorical_columns].fillna(missing_label).astype(str)
    for column in categorical_columns:
        counts = prepared[column].value_counts(dropna=False)
        maps[column] = {
            value: value if count >= min_count else rare_label
            for value, count in counts.items()
        }
    return maps


def apply_category_maps(
    frame: pd.DataFrame,
    maps: dict[str, dict[str, str]],
    rare_label: str = "Other",
    missing_label: str = "Unknown",
) -> pd.DataFrame:
    """train에서 만든 희소 범주 매핑을 train/valid/test에 동일하게 적용합니다.

    매핑에 없는 값은 valid/test에서 처음 등장한 범주라는 뜻이므로 Other로 보냅니다.
    이렇게 해야 validation/test 정보를 사용해 전처리 기준을 다시 만들지 않습니다.
    """

    transformed = frame.copy()
    for column, mapping in maps.items():
        values = transformed[column].fillna(missing_label).astype(str)
        transformed[column] = values.map(mapping).fillna(rare_label)
    return transformed


def stratified_splits(
    modeling: pd.DataFrame,
    random_state: int = 42,
    test_size: float = 0.2,
    validation_size: float = 0.2,
) -> SplitData:
    """손상 클래스 비율을 유지하면서 공식 train/test와 내부 validation을 만듭니다.

    Test는 최종 평가 전용으로 남겨두고, threshold 선택은 train 안에서 다시 분리한
    validation으로만 수행합니다.
    """

    X = modeling[MAIN_FEATURES].copy()
    y = modeling[TARGET].astype(int).copy()
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    X_fit, X_valid, y_fit, y_valid = train_test_split(
        X_train,
        y_train,
        test_size=validation_size,
        random_state=random_state,
        stratify=y_train,
    )
    return SplitData(X_train, X_test, y_train, y_test, X_fit, X_valid, y_fit, y_valid)


def metrics_at_threshold(y_true: pd.Series, y_proba: pd.Series, threshold: float) -> dict[str, float]:
    """하나의 threshold에서 불균형 분류 핵심 지표를 계산합니다."""

    y_pred = (np.asarray(y_proba) >= threshold).astype(int)
    return {
        "threshold": float(threshold),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "f2": float(fbeta_score(y_true, y_pred, beta=2, zero_division=0)),
    }


def choose_threshold(y_true: pd.Series, y_proba: pd.Series) -> tuple[pd.DataFrame, dict[str, float | str]]:
    """validation 예측확률로 최종 threshold 후보를 비교하고 선택합니다.

    우선순위는 문서 기준에 맞춰 precision 40% 이상에서 recall 최대,
    precision 35% 이상에서 recall 최대, F2 최대, F1 최대, 기본 0.5 순서입니다.
    """

    candidates = sorted(set([0.5] + [round(x, 2) for x in np.arange(0.05, 0.96, 0.05)]))
    rows = []
    for threshold in candidates:
        row = metrics_at_threshold(y_true, y_proba, threshold)
        row["criterion"] = "grid"
        rows.append(row)

    table = pd.DataFrame(rows)
    selections = []

    for floor, name in [(0.40, "precision_40_recall_max"), (0.35, "precision_35_recall_max")]:
        eligible = table[table["precision"] >= floor]
        if not eligible.empty:
            best = eligible.sort_values(["recall", "f1", "precision"], ascending=False).iloc[0].to_dict()
            best["criterion"] = name
            selections.append(best)

    best_f2 = table.sort_values(["f2", "recall", "precision"], ascending=False).iloc[0].to_dict()
    best_f2["criterion"] = "max_f2"
    selections.append(best_f2)

    best_f1 = table.sort_values(["f1", "recall", "precision"], ascending=False).iloc[0].to_dict()
    best_f1["criterion"] = "max_f1"
    selections.append(best_f1)

    default = table[table["threshold"] == 0.5].iloc[0].to_dict()
    default["criterion"] = "default_0.5"
    selections.append(default)

    selected = selections[0]
    table = pd.concat([table, pd.DataFrame(selections)], ignore_index=True)
    return table, selected
