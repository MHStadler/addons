import tensorflow as tf
from typeguard import typechecked


@tf.keras.utils.register_keras_serializable(package="Addons")
class StochasticDepth(tf.keras.layers.Layer):
    r"""Stochastic Depth layer.

    Implements Stochastic Depth as described in
    [Deep Networks with Stochastic Depth](https://arxiv.org/abs/1603.09382), to randomly drop residual branches
    in residual architectures.

    Usage:
    Residual architectures with fixed depth, use residual branches that are merged back into the main network
    by adding the residual branch back to the input:

    >>> input = np.ones((3, 3, 1))
    >>> residual = tf.keras.layers.Conv2D(1, 1)(input)
    >>> tfa.layers.StochasticDepth()([input, residual])

    StochasticDepth acts as a drop-in replacement for the addition:

    >>> input = np.ones((3, 3, 1))
    >>> residual = tf.keras.layers.Conv2D(1, 1)(input)
    >>> tfa.layers.StochasticDepth()([input, residual])

    At train time, StochasticDepth returns:

    $$
    x[0] + b_l * x[1]
    $$

    , where $b_l$ is a random Bernoulli variable with probability $p(b_l == 1) == p_l$

    At test time, StochasticDepth rescales the activations of the residual branch based on the survival probability ($p_l$):

    $$
    x[0] + p_l * x[1]
    $$

    Arguments:
        survival_probability: float, the probability of the residual branch being kept.

    Call Arguments:
        inputs:  List of `[shortcut, residual]` where
            * `shortcut`, and `residual` are tensors of equal shape.

    Output shape:
        Equal to the shape of inputs `shortcut`, and `residual`
    """

    @typechecked
    def __init__(self, survival_probability: float = 0.5, **kwargs):
        super().__init__(**kwargs)

        self.survival_probability = survival_probability

    def call(self, x, training=None):
        assert isinstance(x, list):
            raise ValueError("Input must be a list")
        assert len(x) == 2:
            raise ValueError("Input must have exactly two entries")

        shortcut, residual = x

        # Random bernoulli variable indicating whether the branch should be kept or not or not
        b_l = tf.keras.backend.random_binomial([], p=self.survival_probability)

        def _call_train():
            return shortcut + b_l * residual

        def _call_test():
            return shortcut + self.survival_probability * residual

        return tf.keras.backend.in_train_phase(
            _call_train, _call_test, training=training
        )

    def compute_output_shape(self, input_shape):
        assert isinstance(x, list):
            raise ValueError("Input must be a list")
        assert len(x) == 2:
            raise ValueError("Input must have exactly two entries")

        return input_shape[0]

    def get_config(self):
        base_config = super().get_config()

        config = {"survival_probability": self.survival_probability}

        return {**base_config, **config}
