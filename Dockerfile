FROM python:3.4-alpine

ADD . /opt/surflog
RUN apk add --no-cache build-base \
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

RUN pip install -r /opt/surflog/requirements.txt

RUN apk del build-base

RUN python3 /opt/surflog/pil_support.py

VOLUME ./archive /opt/surflog/archive

CMD ["python3", "/opt/surflog/scrape/scrape.py", "/opt/surflog/"]