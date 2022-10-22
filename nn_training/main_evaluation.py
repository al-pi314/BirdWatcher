import os
import re
from pathlib import Path
import numpy as np
import pandas as pd
import keras

# Setting up file paths
import sys
abs_path = "/".join(os.path.realpath(__file__).split("/")[:-1]) # Linux
if (abs_path == ""):
  abs_path = "\\".join(os.path.realpath(__file__).split("\\")[:-1]) # Windows 
sys.path.append(abs_path + '/models')

EVALUATION_FOLDER = abs_path + '/images_for_evaluation/'
CHECKPOINT_DIRECTORY = abs_path + '/checkpoints/bird_classifier_keras/xception_pre_trained/'

# Create the model
N_CLASSES = 15
from bird_recon_xception import ModelTools as model_tools
model = model_tools.create_model(N_CLASSES, 'imagenet')

# Load weights into the model
model.load_weights(CHECKPOINT_DIRECTORY + 'current_best.h5')

# Declare generators that read from folders
imageGenerator = keras.preprocessing.image.ImageDataGenerator(
    horizontal_flip=True,
    data_format='channels_last',
    rescale=1. / 255
)

# Prepares the model to run
model.compile(optimizer = keras.optimizers.Adam(),
              loss = 'categorical_crossentropy',
              metrics = ['accuracy']
              )
# Get all the images fro evaulation
test_generator = imageGenerator.flow_from_directory(
    batch_size=1,
    directory=EVALUATION_FOLDER,
    target_size=[150,150],
    class_mode='categorical',
    shuffle=False
    )

# Predict
predictions = model.predict_generator(
    test_generator,
    verbose=0,
     steps=1
)

predictions = np.argmax(predictions, axis=1)
print(predictions)