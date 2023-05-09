from flask import Flask, render_template, request
import requests
import ee
import geehydro
import cv2
import urllib
import numpy as np

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the latitude and longitude from the form and convert them to float
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        scale = float(request.form['scale'])

        ee.Initialize()

        poi = ee.Geometry.Point([longitude, latitude])  # [long, lat]
        roi = poi.buffer(distance=9.2e5)

        dataset = ee.ImageCollection(
            "COPERNICUS/Landcover/100m/Proba-V-C3/Global")
        dataset = dataset.select('discrete_classification')

        date_filter = ee.Filter.date('2019-1-1', '2019-12-31')
        dataset = dataset.filter(date_filter)

        image = dataset.mean()
        image = image.multiply(scale)
        visualisation_params = {
        'min': 0,
        'max': 126,
        'dimensions': 620,
        'region': roi,
        'gamma': 1.00
        }
        urla = image.getThumbUrl(visualisation_params)
        print(urla)

        barry = ""

        with urllib.request.urlopen(urla) as url:
            barry = url.read()
        arr = np.asarray(bytearray(barry), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)

        response = requests.get(urla)

        # Render the index template with the image URL
        return render_template('index.html', image_url=urla)

    # Render the index template without an image URL
    return render_template('index.html', image_url=None)

if __name__ == '__main__':
    app.run(debug=True)
