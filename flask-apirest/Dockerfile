#FROM alpine:3.10
#FROM python:3.8.12-alpine3.15
FROM ubuntu:20.04
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y software-properties-common curl


RUN add-apt-repository ppa:deadsnakes/ppa    
RUN apt-get update


#RUN apk add --no-cache python3-dev \
#	&& pip3 install --upgrade pip

RUN apt-get install -y python3.8 python3.8-dev python3.8-distutils

# Asegúrate de que pip está disponible para Python 3.8
RUN curl https://bootstrap.pypa.io/pip/3.8/get-pip.py -o get-pip.py
RUN python3.8 get-pip.py

# (Opcional) Elimina el script de instalación de pip
RUN rm get-pip.py

# Establece Python 3.8 como la versión por defecto
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
RUN update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.8 1

# Verifica la versión instalada
RUN python3 --version
RUN pip --version


WORKDIR /app-flask

COPY . /app-flask

RUN pip --no-cache-dir install -r requirements.txt

#CMD ["python3","src/app.py"]
