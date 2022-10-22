import sys
import numpy as np
from PIL import Image
import tensorflow as tf
import keras
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils

class NeuralNetwork:
  def __init__(self, classes, weights_file):
    self.classes = classes

    # Include module builder
    sys.path.append('./models')
    from Xception import ModelTools as model_tools

    # Build a model and import weights into it
    self.model = model_tools.create_model(self.classes, 'imagenet')
    self.model.load_weights('./checkpoints/' + weights_file)
    
    self.graph = tf.get_default_graph()

  def evaluateImage(self, image):
    image = self.prepareImage(image)
    with self.graph.as_default():  
  
      # Run images through neural network
      predictions = self.model.predict(image)
      # Edit predictions array to only include output neurons with highest value
      predictions = np.argmax(predictions, axis=1).tolist()
      print("PREDICTED:", predictions)

      return predictions

  def prepareImage(self, image):
    w, h = image.size
    image = image.crop((280, 120, w, h))
    image.thumbnail((150,150))
    if image.mode != 'RGB':
        image = image.convert('RGB')
        
    # Preprocess Image
    image = img_to_array(image)
    image = image /255
    image = np.expand_dims(image, axis=0)
    return image

if __name__ == '__main__':
  NN = NeuralNetwork(15, 'bird_classifier/current_best.h5')
  im = Image.open('./test.jpeg')
  for i in range(3):
    print("##############################")
    print(NN.evaluateImage(im))