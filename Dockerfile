#FROM ubuntu
#
#
#COPY . /app
#WORKDIR /app
#
#RUN pip install -r requirements-dev.txt
#RUN python setup.py develop
#RUN alembic upgrade head
#RUN cd atramhasis/static && \
#    bower install && \
#    cd admin && \
#    bower install
#
FROM ubuntu:16.04

COPY . /app
WORKDIR /app

########################################################### ENVIRONMENT: base ################################################
USER root

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install --upgrade setuptools

########################################################### Application needed: ################################################
# ------- Install additionnal libraries with "apt-get -y"
# RUN apt-get install -y libsm6 libxext6 libglib2.0-0 libxrender-dev
RUN apt-get install -y python-software-properties
RUN apt-get install -y curl
RUN apt-get install -y git
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g bower
# ------- Or annd needed libraries into "requirements.txt" file and use it:

RUN python3.6 -m pip install -r requirements-dev.txt
RUN python3.6 setup.py develop
RUN alembic upgrade head
RUN cd atramhasis/static && \
    bower install --allow-root && \
    cd admin && \
    bower install --allow-root

RUN python3.6 setup.py compile_catalog
EXPOSE 6543

CMD pserve development.ini