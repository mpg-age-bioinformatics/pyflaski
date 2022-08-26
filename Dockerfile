# Copyright (c) Bioinformatics Core Facility of the Max Planck Institute for Biology of Ageing.
# Distributed under the terms of the Modified BSD License.

# Debian buster-slim (10.1)
FROM debian:buster-slim

LABEL maintainer "bioinformatics@age.mpg.de"

USER root

ENV DEBIAN_FRONTEND noninteractive

RUN echo "deb http://ftp.debian.org/debian buster main non-free contrib" >> /etc/apt/sources.list && \
echo "deb-src http://ftp.debian.org/debian buster main non-free contrib" >> /etc/apt/sources.list && \
echo "deb http://ftp.debian.org/debian buster-updates main contrib non-free" >> /etc/apt/sources.list && \
echo "deb-src http://ftp.debian.org/debian buster-updates main contrib non-free" >> /etc/apt/sources.list 

RUN apt-get update && apt-get -yq dist-upgrade && \
apt-get install -yq --no-install-recommends locales && \
apt-get clean && rm -rf /var/lib/apt/lists/* && \
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

ENV SHELL /bin/bash
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN apt-get update && apt-get -yq dist-upgrade && \
apt-get install -yq pkg-config \
libcairo2-dev \
python3 \
python3-pip \
texlive \
texlive-latex-extra \
texlive-xetex \
texlive-fonts-recommended \
texlive-plain-generic \
pandoc && \
python3 -m pip install -U pip && \
pip3 install --ignore-installed pyxdg==0.26 && \
apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /pyflaski

COPY . /pyflaski

RUN pip3 install -r /pyflaski/requirements.txt

RUN pip3 install jupyter jupyterlab nbconvert

RUN pip3 install -e /pyflaski

RUN python3 -c 'import pyflaski'