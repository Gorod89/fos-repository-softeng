from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class KNNClassifier:
    """Минимальный контракт классификатора; векторизацию завершает студент."""

    def __init__(self, n_neighbors: int = 3) -> None:
        if n_neighbors <= 0:
            raise ValueError("n_neighbors должен быть положительным.")
        self.n_neighbors = n_neighbors
        self._x: NDArray[np.float64] | None = None
        self._y: NDArray[np.int64] | None = None

    def fit(self, x: NDArray[np.float64], y: NDArray[np.int64]) -> "KNNClassifier":
        if x.ndim != 2 or y.ndim != 1 or len(x) != len(y):
            raise ValueError("Ожидаются X формы (n, features) и y формы (n,).")
        if self.n_neighbors > len(x):
            raise ValueError("Число соседей не может превышать размер выборки.")
        self._x = np.asarray(x, dtype=np.float64)
        self._y = np.asarray(y, dtype=np.int64)
        return self

    def predict(self, x: NDArray[np.float64]) -> NDArray[np.int64]:
        if self._x is None or self._y is None:
            raise RuntimeError("Сначала вызовите fit().")
        query = np.asarray(x, dtype=np.float64)
        if query.ndim != 2 or query.shape[1] != self._x.shape[1]:
            raise ValueError("Число признаков должно совпадать с обучающей выборкой.")
        # TODO: замените реализацию на экономную векторизованную обработку батчами.
        predictions: list[int] = []
        for row in query:
            distances = np.sqrt(np.sum((self._x - row) ** 2, axis=1))
            neighbors = np.argsort(distances, kind="stable")[: self.n_neighbors]
            labels, counts = np.unique(self._y[neighbors], return_counts=True)
            predictions.append(int(labels[np.argmax(counts)]))
        return np.asarray(predictions, dtype=np.int64)
