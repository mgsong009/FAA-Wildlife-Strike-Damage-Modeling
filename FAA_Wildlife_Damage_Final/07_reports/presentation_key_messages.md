# Presentation Key Messages

1. This project predicts aircraft damage risk after FAA wildlife strike incidents.
2. The target class is imbalanced, with damage cases around 7%.
3. Leakage-prone post-incident fields such as DAMAGE_LEVEL, STR_*, and ING_* were excluded.
4. Final model selection focused on Recall and F1, not Accuracy.
5. Validation data was used for threshold selection, while Test data was used only for final evaluation.