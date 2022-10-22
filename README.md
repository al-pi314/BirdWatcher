## Bird Watcher

Proof of concept project on automatic bird species detection using AI deep learning.

## Required libaries

- main_server [js] => server for displaying collected data
    - 'as specified in package.json'
- nn_running [python] => flask server that provides on demand classification
    - flask
    - tensorflow
    - keras
    - PIL
    - numpy
- nn_training [python] => model traning on preclassified images
    - keras
    - numpy
    - pandas
    - pathlib
    - transforms
    - PIL
- raspberry_pi [python] => station logic for detecting, photographing and sending data
    - RPi.GPIO as GPIO
    - PiCamera
    - board
    - busio
    - adafruit_bme280
    - requests