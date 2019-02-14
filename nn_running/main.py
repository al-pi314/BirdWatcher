import flask
import os
from flask import Flask
from PIL import Image
from neuralNetwork import NeuralNetwork
from io import BytesIO

model_ready = False
NN = None
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def evalImage():
    global NN
    print(flask.request.values['password'])
    print(flask.request.files['image'])
    if (flask.request.method == 'POST' and flask.request.values['password'] == '***REMOVED***'):
        print("Password OK!")

        image = flask.request.files['image'].read()
        image = Image.open(BytesIO(image))

        data = { 
            'success': False,
            'message': 'NN running!',
            'predictions': []
        }

        if NN is None:
            data['message'] = 'Starting..'
        else:
            predictions = NN.evaluateImage(image)
            for prediction in predictions:
                print("Predictions in list:", prediction)
                data['predictions'].append(prediction)
            data['success'] = True

        print("Reuqest compilited!")
        return flask.jsonify(data)
    else:
        return "Index Page"

@app.before_first_request
def init():
    global model_ready
    global NN
    
    if (model_ready):
        print("Model already created!")
        return

    print("Creating new model...")
    NN = NeuralNetwork(15, 'bird_classifier/current_best.h5')
    model_ready = True
    print("Model created server is ready!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    init()