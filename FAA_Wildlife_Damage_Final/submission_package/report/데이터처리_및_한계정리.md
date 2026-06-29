# Limitations

- The dataset contains reported strike incidents only; it does not include all flights or non-reported events.
- The model predicts damage after a strike has occurred and should not be described as strike occurrence prediction.
- High-cardinality categories are grouped into Other to reduce overfitting and improve presentation stability.
- Threshold tuning used validation data; the test set was reserved for final evaluation.