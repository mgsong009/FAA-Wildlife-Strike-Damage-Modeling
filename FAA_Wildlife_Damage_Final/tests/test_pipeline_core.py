import pandas as pd

# 이 테스트 파일은 전체 파이프라인을 매번 돌리지 않고도
# 프로젝트의 핵심 규칙이 깨졌는지 빠르게 확인하기 위한 안전장치입니다.
from src.pipeline_core import (
    MAIN_FEATURES,
    choose_threshold,
    detect_leakage_columns,
    make_modeling_frame,
    rare_category_maps,
    stratified_splits,
)


def test_detect_leakage_columns_finds_exact_and_prefix_matches():
    # DAMAGE_LEVEL은 target 생성 원본이고, STR_/ING_ 계열은 충돌 이후 기록입니다.
    # 이 컬럼들이 입력 변수로 섞이면 모델이 정답을 미리 보는 데이터 누수가 생깁니다.
    columns = [
        "Damage_Binary",
        "DAMAGE_LEVEL",
        "INCIDENT_MONTH",
        "STR_NOSE",
        "ING_ENG1",
        "SPECIES",
    ]

    leakage = detect_leakage_columns(columns)

    assert leakage == ["DAMAGE_LEVEL", "STR_NOSE", "ING_ENG1"]


def test_make_modeling_frame_uses_only_main_features_and_target():
    # 원본 데이터에 누수 컬럼이 있어도 모델링 프레임에는
    # 문서에서 확정한 Main Feature 15개와 Damage_Binary만 남아야 합니다.
    df = pd.DataFrame(
        {
            "Damage_Binary": [0, 1],
            "DAMAGE_LEVEL": ["N", "M"],
            "STR_NOSE": [1, 0],
            **{feature: ["A", "B"] for feature in MAIN_FEATURES},
        }
    )

    modeling = make_modeling_frame(df)

    assert list(modeling.columns) == MAIN_FEATURES + ["Damage_Binary"]
    assert "DAMAGE_LEVEL" not in modeling.columns
    assert "STR_NOSE" not in modeling.columns


def test_rare_category_maps_keep_frequent_values_and_group_rare_values():
    # SPECIES처럼 고유값이 많은 변수는 희소 범주를 Other로 묶어야 합니다.
    # 여기서는 min_count=2를 기준으로 frequent/rare가 올바르게 갈리는지 확인합니다.
    train = pd.DataFrame(
        {
            "SPECIES": ["Common"] * 3 + ["Rare"] + ["Missing"],
            "STATE": ["TX", "TX", "CA", "AK", "AK"],
        }
    )

    maps = rare_category_maps(train, ["SPECIES", "STATE"], min_count=2)

    assert maps["SPECIES"]["Common"] == "Common"
    assert maps["SPECIES"]["Rare"] == "Other"
    assert maps["STATE"]["AK"] == "AK"
    assert maps["STATE"]["CA"] == "Other"


def test_stratified_splits_preserve_test_and_validation_sizes():
    # 손상 데이터는 약 7% 수준의 불균형 데이터이므로 단순 random split을 쓰면
    # test/validation에 손상 비율이 흔들릴 수 있습니다. stratify 유지 여부를 검증합니다.
    df = pd.DataFrame(
        {
            **{feature: [str(i % 4) for i in range(100)] for feature in MAIN_FEATURES},
            "Damage_Binary": [0] * 80 + [1] * 20,
        }
    )

    splits = stratified_splits(df, random_state=7, test_size=0.2, validation_size=0.25)

    assert len(splits.X_train) == 80
    assert len(splits.X_test) == 20
    assert len(splits.X_fit) == 60
    assert len(splits.X_valid) == 20
    assert splits.y_test.mean() == 0.2
    assert splits.y_valid.mean() == 0.2


def test_choose_threshold_prefers_precision_floor_then_recall():
    # 최종 threshold는 test가 아니라 validation 결과에서 골라야 합니다.
    # 이 테스트는 threshold 비교표가 생성되고, 문서의 선택 기준 중 하나가 반환되는지 확인합니다.
    y_true = pd.Series([0, 0, 0, 1, 1, 1])
    y_proba = pd.Series([0.1, 0.2, 0.8, 0.3, 0.7, 0.9])

    table, selected = choose_threshold(y_true, y_proba)

    assert {"threshold", "precision", "recall", "f1", "f2", "criterion"}.issubset(table.columns)
    assert 0.0 <= selected["threshold"] <= 1.0
    assert selected["criterion"] in {
        "precision_40_recall_max",
        "precision_35_recall_max",
        "max_f2",
        "max_f1",
        "default_0.5",
    }
