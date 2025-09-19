import numpy as np
from numpy.polynomial import Polynomial


class ApproximationService:
    @staticmethod
    def polynomial_fit(x, y, degree=3):
        """
        Polynomial approximation
        Returns:
            tuple: (x_fit, y_fit)
        """
        p = Polynomial.fit(x, y, degree)
        x_fit = np.linspace(min(x), max(x), 1000)
        return x_fit, p(x_fit)
