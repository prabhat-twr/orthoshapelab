import numpy as np
from orthoshapelab.pca_model import PCAShapeModel


def test_pca():

    X = np.random.randn(10, 300)

    model = PCAShapeModel(X)

    coeffs = np.zeros(3)

    shape = model.reconstruct(coeffs)

    assert shape.shape[1] == 3