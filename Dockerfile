FROM python:3.9-buster
WORKDIR /app
COPY requirements.txt requirements.txt 
RUN pip3 install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get update
RUN apt-get --fix-missing update && apt-get --fix-broken install && apt-get install -y poppler-utils && apt-get install -y tesseract-ocr && \
    apt-get install -y libtesseract-dev && apt-get install -y libleptonica-dev && ldconfig && apt install -y libsm6 libxext6 && apt install -y python-opencv
COPY . .
CMD ["python","api.py"]