import keras

class ModelTools:

  def create_model(n_classes, weights):
    trained_model = keras.applications.xception.Xception(
        include_top=False,
        weights=weights,
        input_shape=[150, 150, 3],
        pooling='max')

    kernel_initializer = keras.initializers.glorot_uniform(seed=1337)
    model = keras.Sequential()

    model.add(trained_model)
    model.add(keras.layers.Dense(n_classes, activation='softmax', kernel_initializer = kernel_initializer))

    return model