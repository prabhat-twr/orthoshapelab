import numpy as np
from sklearn.decomposition import PCA


class PCAShapeModel:

    def __init__(self, X):

        self.mean = np.mean(X, axis=0)

        Xc = X - self.mean

        self.pca = PCA()
        self.pca.fit(Xc)

        self.eigenvectors = self.pca.components_.T
        self.eigenvalues = self.pca.explained_variance_
        self.variance_ratio = self.pca.explained_variance_ratio_

    def reconstruct(self, coeffs):

        shape = self.mean.copy()

        for i in range(len(coeffs)):
            shape += coeffs[i] * np.sqrt(self.eigenvalues[i]) * self.eigenvectors[:, i]

        return shape.reshape(-1,3)