from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import image_preprocesing as impre
from pdf2image import convert_from_path
import pytesseract
import numpy as np
import requests
import os
import cv2
import json 
import logging
import traceback


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
            gray = impre.get_grayscale(rgb_img)
            thresh = impre.thresholding(gray)
            opening = impre.opening(gray)
            canny = impre.canny(gray)
            images = {'gray': gray, 
                    'thresh': thresh, 
                    'opening': opening, 
                    'canny': canny}
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
    url_file = request.headers.get('url')
    return getPhonePdf(url_file)

if __name__ == "__main__":
    app.debug = True
    app.run(host='localhost', port=9000)