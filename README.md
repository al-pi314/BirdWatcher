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

## Acknowledgments 
- Project Team: Kalina Mihelič, Andrej Matevc, Aleksander Piciga
- Project Mentors: Alenka Mozer, Jaka Konda, Barbara Mihelič
- Project Location: Gimnazija Vič & ZOO Ljubljana

Project was also supported by many other people all of who we thank for their efforts.

More about the project can be found on our website linked in github about section.