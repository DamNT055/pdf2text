from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import numpy as np
import requests
import os
import cv2
import json 
import logging
import traceback


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# noise removal
def remove_noise(image):
    return cv2.medianBlur(image,5)
 
#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#dilation
def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)
    
#erosion
def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

#opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

#canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)

#skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

#template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 


def getPhonePdf(url_file = ""):
    data_json = {}
    try:
        if url_file is not None and url_file.strip() != "":
            filename = Path('files/anhxuly.pdf')
            response = requests.get(url_file.strip())
            filename.write_bytes(response.content)
            image = np.array(convert_from_path(filename)[0])
            b,g,r = cv2.split(image)
            rgb_img = cv2.merge([r,g,b])
            gray_img = get_grayscale(rgb_img)
            thresh_img = thresholding(gray_img)
            opening_img = opening(gray_img)
            canny_img = canny(gray_img)
            images = {'gray': gray_img, 
                    'thresh': thresh_img, 
                    'opening': opening_img, 
                    'canny': canny_img}
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(images['gray'], config=custom_config).split()
            for txt in text:
                if txt.find("(+84)")>-1:
                    if (int(txt.replace("(+84)",'').strip()) != 355039282):
                        new_name = 'files/anh_' + txt.replace("(+84)",'') + '.pdf'
                        os.rename('files/anhxuly.pdf', new_name) 
                        data_json = {
                            'phone' : txt,
                            'img_link': str(new_name)
                        }
                        return json.dumps(data_json)
    except Exception as e:
        logging.error(traceback.format_exc())
        return json.dumps(data_json)
    return json.dumps(data_json)
        
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods =['POST'])
def api_get_json():
    url_file = request.form['url']
    return getPhonePdf(url_file)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=9000)