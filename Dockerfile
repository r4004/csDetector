FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt install -y build-essential \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa

RUN apt-get install -y libfreetype6-dev libpng-dev
ENV MPLLOCALFREETYPE=1

RUN apt-get update && apt-get install -y python3.8
RUN apt-get install -y python3-pip python3-dev python3-venv python3-wheel
ENV PATH="/usr/bin/python3.8:${PATH}"

RUN apt-get install -y openjdk-8-jdk
ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"
ENV PATH="$JAVA_HOME/bin:${PATH}"

RUN apt-get update && apt-get install -y git
ENV PATH="/usr/bin/git:${PATH}"

WORKDIR /app

COPY . /app

RUN mkdir out
RUN mkdir senti

ADD http://sentistrength.wlv.ac.uk/jkpop/SentiStrength.jar senti
ADD http://sentistrength.wlv.ac.uk/jkpop/SentiStrength_Data.zip senti

RUN apt-get update && apt-get install -y unzip
RUN unzip senti/SentiStrength_Data.zip -d senti/SentiStrength_Data
RUN rm senti/SentiStrength_Data.zip

RUN python3.8 -m pip install --upgrade pip setuptools wheel
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install -r requirements.txt
RUN python3.8 -m pip install spacy

RUN python3.8 -m spacy download en_core_web_sm

RUN echo "import nltk;" > nltk_setup.py \
    && echo "nltk.download('punkt')" >> nltk_setup.py \
    && python3.8 nltk_setup.py

EXPOSE 5001

CMD ["python3.8", "webService/csDetectorWebService.py"]