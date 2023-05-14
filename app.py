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
        scale = int(request.form['scale'])

        ee.Initialize()

        poi = ee.Geometry.Point([longitude, latitude])  # [long, lat]
        roi = poi.buffer(distance=scale)

        dataset = ee.ImageCollection(
            "COPERNICUS/Landcover/100m/Proba-V-C3/Global")
        dataset = dataset.select('discrete_classification')

        date_filter = ee.Filter.date('2019-1-1', '2019-12-31')
        dataset = dataset.filter(date_filter)

        image = dataset.mean()
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
        img1 = cv2.imdecode(arr, -1)

        dataset = ee.ImageCollection(
            "COPERNICUS/Landcover/100m/Proba-V-C3/Global")
        dataset = dataset.select('discrete_classification')

        date_filter = ee.Filter.date('2015-1-1', '2015-12-31')
        dataset = dataset.filter(date_filter)

        image = dataset.mean()
        visualisation_params = {
        'min': 0,
        'max': 126,
        'dimensions': 620,
        'region': roi,
        'gamma': 1.00
        }
        urlb = image.getThumbUrl(visualisation_params)


        barry = ""

        with urllib.request.urlopen(urlb) as url:
            barry = url.read()
        arr = np.asarray(bytearray(barry), dtype=np.uint8)
        img2 = cv2.imdecode(arr, -1)



        # Calculate the absolute difference between the two images
        diff = cv2.absdiff(img1, img2)

        # Apply a threshold to the difference image to obtain a binary mask
        thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]

        # Define the colors for highlighting the areas with either red or green
        green = (0, 255, 0)
        red = (0, 0, 255)
        deforestation=0

        # Create a new color image with the same dimensions as the grayscale images
        color_img = np.zeros((img2.shape[0], img2.shape[1], 3), dtype=np.uint8)
        forestationMask=np.zeros((img2.shape[0], img2.shape[1], 3), dtype=np.uint8)
        # Iterate over each pixel in the binary mask and color the corresponding pixel in the color image
        for i in range(thresh.shape[0]):
            for j in range(thresh.shape[1]):
                if thresh[i][j] == 255:
                    if(img1[i][j] < img2[i][j]):
                        deforestation=deforestation+1
                    else:
                        deforestation=deforestation-1
                    color_img[i][j] = green if img1[i][j] < img2[i][j] else red
                    forestationMask[i][j] = green if img1[i][j] < img2[i][j] else red
                else:
                    color_img[i][j]=[img1[i][j],img1[i][j],img1[i][j]]

        # Display the color image with the highlighted areas
        response = requests.get(urla)
        cv2.imwrite('static/img1.png', color_img)
        cv2.imwrite('static/img2.png', forestationMask)

        # Render the index template with the image URL
        return render_template('index.html', image_url=urla,image_url1='img1.png',image_url2='img2.png',deforestation_degree=str(deforestation))

    # Render the index template without an image URL
    return render_template('index.html', image_url=None)

if __name__ == '__main__':
    app.run(debug=True)



