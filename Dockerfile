#FROM python:3.4-alpine
#FROM arm32v7/python:3

FROM arm32v6/alpine

RUN apk update && apk add build-base \
 python \
 py-setuptools \
 py-pip \
 python-dev \
 # Pillow dependencies
 jpeg-dev \
 zlib-dev \
 freetype-dev \
 lcms2-dev \
 openjpeg-dev \
 tiff-dev \
 tk-dev \
 tcl-dev \
 harfbuzz-dev \
 fribidi-dev \
 libwebp-dev

ADD . /opt/surflog

RUN pip install  -r /opt/surflog/requirements.txt

RUN python /opt/surflog/pil_support.py

RUN apk del build-base

VOLUME ./archive /opt/surflog/archive

CMD ["python", "/opt/surflog/scrape/scrape.py", "/opt/surflog/"]
