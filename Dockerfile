# Copyright (c) Bioinformatics Core Facility of the Max Planck Institute for Biology of Ageing.
# Distributed under the terms of the Modified BSD License.

# Debian buster-slim (10.1)
FROM mpgagebioinformatics/myapp:latest

LABEL maintainer "bioinformatics@age.mpg.de"

USER root

RUN apt-get update && apt-get -yq dist-upgrade && \
apt-get install -yq texlive \
texlive-latex-extra \
texlive-xetex \
texlive-fonts-recommended \
texlive-plain-generic \
pandoc \
libgirepository1.0-dev && \
apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /pyflaski

COPY . /pyflaski

RUN pip3 install -r /pyflaski/requirements.txt

RUN pip3 install jupyter jupyterlab nbconvert

RUN pip3 install -e /pyflaski

RUN python3 -c 'import pyflaski'

ENTRYPOINT /bin/bash 