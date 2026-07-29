import numpy as np
import pytest

from m5_knn import KNNClassifier


def test_predicts_simple_clusters() -> None:
    x = np.array([[0.0, 0.0], [0.0, 1.0], [10.0, 10.0], [10.0, 11.0]])
    y = np.array([0, 0, 1, 1])
    model = KNNClassifier(1).fit(x, y)
    assert model.predict(np.array([[0.2, 0.1], [9.9, 10.2]])).tolist() == [0, 1]


def test_rejects_predict_before_fit() -> None:
    with pytest.raises(RuntimeError, match="fit"):
        KNNClassifier().predict(np.array([[0.0]]))
