import numpy as np


class BasisTranslater:
    @classmethod
    def center(cls, points: np.ndarray) -> np.ndarray:
        return points - np.mean(points, axis=0)  # type: ignore[no-any-return]

    @classmethod
    def translate(cls, leading: np.ndarray, translating: np.ndarray) -> np.ndarray:
        leading_centroid = np.mean(leading, axis=0)
        translating_centroid = np.mean(translating, axis=0)

        rotation = cls._kabsch(leading, translating)
        displacement_vector = translating_centroid - rotation @ leading_centroid

        return cls._rotate(translating, rotation) + displacement_vector  # type: ignore[no-any-return]

    @classmethod
    def _rotate(cls, points: np.ndarray, rotation: np.ndarray) -> np.ndarray:
        return (rotation @ points.T).T  # type: ignore[no-any-return]

    @classmethod
    def _kabsch(cls, p: np.ndarray, q: np.ndarray) -> np.ndarray:
        p_centered = cls.center(p)
        q_centered = cls.center(q)

        h = p_centered.T @ q_centered
        [u, _, v] = np.linalg.svd(h)
        v = v.T
        r = v @ u.T

        if np.linalg.det(r) < 0:
            v[:, -1] *= -1
            r = v @ u.T
        return r  # type: ignore[no-any-return]
