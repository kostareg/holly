import copy
import tensorflow as tf

from holly_simulator import VectorizedGeometricBrownianMotion


def test_constant_paths():
    """
    With mu=0 sigma=0, gbm paths should all be constant.
    """
    T = 2
    t = 0
    dt = 1 / 252
    gbm = VectorizedGeometricBrownianMotion(100, 100.0, 0, 0, dt)

    gbm.step()
    s = copy.deepcopy(gbm.s)

    while T > t * dt:
        gbm.step()
        tf.debugging.assert_equal(gbm.s, s)
        t += 1
