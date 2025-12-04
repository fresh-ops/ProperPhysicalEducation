import numpy as np


class BasisTranslator:
    """
    A point translator from one basis to another. Uses the Kabsch algorithm to create a rotation matrix to tranlate matrices.
    """

    def __init__(self, source: np.ndarray, destination: np.ndarray) -> None:
        """
        Initialize the translator.

        Args:
            source (np.ndarray): An n-by-m rectangular matrix. It enumerates the coordinates of points in the initial
                basis. Each of the n rows contains a point from the m-dimensional space.
            destination (np.ndarray): An n-by-m rectangular matrix. It enumerates the coordinates of points in the
                desired basis. The order of the points must exactly match that in matrix P.
            
        """
        self.__centroid_source = np.mean(source, axis=0)
        self.__centroid_destination = np.mean(destination, axis=0)
        self.__rotation_matrix = self.__kabsch(source, destination)
        self.__displacement_vector = self.__centroid_destination - self.__rotation_matrix @ self.__centroid_source

    def center(self, A: np.ndarray) -> np.ndarray:
        """
        Centers the passed matrix.

        Args:
            A (np.ndarray): Matrix.

        Returns:
            np.ndarray: A centered matrix of the same size as the original.
        """
        return A - np.mean(A, axis=0)

    def translate(self, points: np.ndarray) -> np.ndarray:
        """
        Applies full transformation (rotation + displacement) to point(s).
        
        Args:
            points (np.ndarray): Point(s) in source basis (either m-vector or n-by-m matrix)
            
        Returns:
            np.ndarray: Transformed point(s) in destination basis
        """
        return self.__rotate(points) + self.__displacement_vector

    def __rotate(self, points: np.ndarray) -> np.ndarray:
        """
        Rotates the given points using precalculated rotation matrix, so that the result is the same points in the 
        other basis.

        Args:
            points (np.ndarray): A points of the source basis. Its rows must represent the coordinates of the source
                basis points.
        Returns:
            np.ndarray: The rotated array of points in the destination basis.
        """
        return (self.__rotation_matrix @ points.T).T

    def __kabsch(self, P: np.ndarray, Q: np.ndarray) -> np.ndarray:
        """
        Computes the rotation matrix using the Kabsch-Umeyama algorithm.

        Args:
            P (np.ndarray): An n-by-m rectangular matrix. It enumerates the coordinates of points in the initial basis.
                Each of the n rows contains a point from the m-dimensional space.
            Q (np.ndarray): An n-by-m rectangular matrix. It enumerates the coordinates of points in the desired basis.
                The order of the points must exactly match that in matrix P.

        Returns:
            np.ndarray: An m-by-m square rotation matrix for translating points from the point basis P to the point basis Q.
                In general, a complete transformation also requires calculating the displacement vector.
        """
        P_centered = self.center(P)
        Q_centered = self.center(Q)

        H = P_centered.T @ Q_centered
        [U, _, V] = np.linalg.svd(H)
        V = V.T
        R = V @ U.T
        if np.linalg.det(R) < 0:
            V[:, -1] *= -1
            R = V @ U.T
        return R
