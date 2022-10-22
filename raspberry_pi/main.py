STATION_NAME = ""

import RPi.GPIO as GPIO
from picamera import PiCamera
from time import sleep
import board
import busio
import adafruit_bme280
import requests
#Station data (ZOO LJUBLJANA)
long = 14.470848
lat = 46.054454

GPIO.setmode(GPIO.BCM)
GPIO.setup(11, GPIO.IN)

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

camera = PiCamera()

pir_sensor = 14
GPIO.setup(pir_sensor, GPIO.IN)

def sendData(url):  
  global NN_image_id, camera, bme280, long, lat

  camera.capture("temp_photo.jpg")
  image_name = "NN_image(" + str(NN_image_id) + ").jpg"
  data_payload = {}
  data_payload['image_name'] = image_name

  data_payload['long'] = long
  data_payload['lat'] = lat
    
  data_payload['station_name'] = STATION_NAME
  data_payload['temp'] = bme280.temperature
  data_payload['hum'] = bme280.humidity
  data_payload['pres'] = bme280.pressure

  try:
    wake_up_nn = requests.get('http://bn-nn-server.herokuapp.com/')
  except:
    print("NN server is restarting!")
    pass
  finally:
    print("Ready to send data!")
    with open("temp_photo.jpg", "rb") as img:
      files = {'media': img}
      response = requests.post(url, data=data_payload, files=files)
      print(response.text)
      if (response.text == "Rejected!"):
        NN_image_id -= 1
    NN_image_id += 1
    with open('Desktop/bn-network/config.txt', "w") as dat:
      dat.write(str(NN_image_id)) 

NN_image_id = 0
with open('Desktop/bn-network/config.txt', 'r') as dat:
  for line in dat:
    NN_image_id = int(line)    
upload_url = 'http://server-bn.herokuapp.com/data'
err_count = 0
initialTest = True

#MAIN LOOP
print("Starting!")
print("---main loop started---")
print("Last id value:", str(NN_image_id -1))
try:
    while True:
        sleep(0.2)
        current_state = GPIO.input(pir_sensor)
        if current_state == 1 or initialTest:
          initialTest = False
          print('Motion found!')
          try:
            sendData(upload_url)
          except:
            if(err_count >= 50):
              print("Criticall Error Ocurred Multiple Times!")
              break
            else:
              print("An Error Occured!")
              err_count += 1
              sleep(30)
          finally:
            print("Loop complited!")
            print("---------------")
            sleep(10)
except KeyboardInterrupt:
    pass
finally:
    print("PROGRAM STOPPED")
    GPIO.cleanup()
