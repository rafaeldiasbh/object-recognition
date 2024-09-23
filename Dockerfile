# Dockerfile. Image, Container
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

COPY . /object-recognition-api
WORKDIR /object-recognition-api

EXPOSE 5000

VOLUME  ./data /object-recognition-api/data

RUN apt-get update && apt-get install -y --no-install-recommends \
python3.11 python3.11-distutils python3.11-venv python3-pip \
wget \
curl \
libglib2.0-0 \
git \
vim \
libgl1-mesa-glx \
&& rm -rf /var/lib/apt/lists/*

RUN if [ -L /usr/bin/python ]; then rm /usr/bin/python; fi && \
ln -s /usr/bin/python3.11 /usr/bin/python && \
if [ -L /usr/bin/python3 ]; then rm /usr/bin/python3; fi && \
ln -s /usr/bin/python3.11 /usr/bin/python3

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

RUN pip install --no-cache-dir torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118

RUN pip install \
    ultralytics \
    opencv-python \
    comet_ml

CMD python ./app.py