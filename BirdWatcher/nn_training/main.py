import sys
import os
import re
from pathlib import Path
import numpy as np
import pandas as pd
import keras
from keras.optimizers import adam
sys.path.append('./models')

# Get parameters from command line
if(len(sys.argv) != 4):
  print("Usage of python main.py model: python main.py 'xception' 'pre_trained' (0=restart|1=continue ... epoch count)")
  sys.exit()
else:
  model_name = sys.argv[1]
  mode  = sys.argv[2]

N_CLASSES = 15

# Load the corresponding model
if model_name == 'xception':
  from bird_recon_xception import ModelTools as model_tools
  if mode == 'pre_trained':
    model = model_tools.create_model(N_CLASSES, 'imagenet')
  elif mode == 'random_init':
    model = model_tools.create_model(N_CLASSES, None)
else:
  print('Model ' + model_name + ' could not be found.')
  sys.exit()

TOTAL_EPOCHS = 30
BATCH_SIZE = 12
TRAIN_DATASET_PATH = './data/train'
VALIDATION_DATASET_PATH = './data/validation'
CHECKPOINT_DIRECTORY = './checkpoints/bird_classifier_keras/{0}_{1}'.format(model_name, mode)
SAVE_CHECKPOINT_PATH = CHECKPOINT_DIRECTORY + '/{epoch:02d}_{val_acc:.4f}.h5'

if not os.path.exists(CHECKPOINT_DIRECTORY):
  os.makedirs(CHECKPOINT_DIRECTORY)

# Declare generators that read from folders
train_generator = keras.preprocessing.image.ImageDataGenerator(
    horizontal_flip=True,
    data_format='channels_last',
    rescale=1. / 255
)

train_batches = train_generator.flow_from_directory(
    batch_size=BATCH_SIZE,
    directory=TRAIN_DATASET_PATH,
    target_size=[150,150],
    class_mode='categorical'
)

val_generator = keras.preprocessing.image.ImageDataGenerator(
    data_format='channels_last',
    rescale=1. / 255
)

val_batches = train_generator.flow_from_directory(
    batch_size=BATCH_SIZE,
    directory=VALIDATION_DATASET_PATH,
    target_size=[150,150],
    class_mode='categorical'
)

TRAIN_DATASET_SIZE = len(train_batches)
VAL_DATASET_SIZE   = len(val_batches)


# Weighted losses for class equilibrium
unique, counts = np.unique(train_batches.classes, return_counts=True)
class_weigths = dict(zip(unique, np.true_divide(counts.sum(), N_CLASSES*counts)))


# Creates some callbacks to be called each epoch
model_checkpoint_callback = keras.callbacks.ModelCheckpoint(
    SAVE_CHECKPOINT_PATH,
    save_weights_only=True,
    verbose=1,
    monitor='val_acc',
    save_best_only=True,
    mode='max'
)
tensorboard_callback = keras.callbacks.TensorBoard(
    log_dir='./logs/bird_classifier_keras/{0}_{1}'.format(model_name, mode),
    histogram_freq=0,
    batch_size=BATCH_SIZE
)
reduce_lr_callback = keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=3,
    min_lr=1e-6
)

# Loads best weights if avaiable
if Path(CHECKPOINT_DIRECTORY).exists():
  epoch_number_array = []
  val_accuracy_array = []
  file_name_array = []
  for file in os.listdir(CHECKPOINT_DIRECTORY):
    epoch, val_acc = re.search(r'(\d\d)_(\d\.\d{4})\.h5', file).group(1,2)
    epoch_number_array.append(int(epoch))
    val_accuracy_array.append(float(val_acc))
    file_name_array.append(file)

  INITIAL_EPOCH = 0
  if (len(val_accuracy_array) != 0):
    highest_acc = val_accuracy_array.index(max(val_accuracy_array))
    if (sys.argv[3] == "1"):
      print("Intial Epoch continuing!")
      INITIAL_EPOCH = epoch_number_array[highest_acc]
    model_checkpoint_callback.best = val_accuracy_array[highest_acc]
    model.load_weights('./checkpoints/bird_classifier_keras/' + '{0}_{1}/'.format(model_name, mode) + file_name_array[highest_acc])
else:
  os.makedirs(CHECKPOINT_DIRECTORY)
  INITIAL_EPOCH = 0

# Prepares the model to run
model.compile(optimizer = keras.optimizers.Adam(),
              loss = 'categorical_crossentropy',
              metrics = ['accuracy']
              )

# Starts training the model

model.fit_generator(train_batches,
                    epochs=TOTAL_EPOCHS,
                    verbose=1,
                    steps_per_epoch=TRAIN_DATASET_SIZE,
                    validation_data=val_batches,
                    initial_epoch=INITIAL_EPOCH,
                    validation_steps=VAL_DATASET_SIZE,
                    class_weight=class_weigths,
                    callbacks=[model_checkpoint_callback, tensorboard_callback, reduce_lr_callback]
                    )