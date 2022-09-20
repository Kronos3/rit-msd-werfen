# Build and run:
#   docker build -t clion/ubuntu/cpp-env:1.0 -f Dockerfile.cpp-env-ubuntu .

FROM ubuntu:20.04

RUN DEBIAN_FRONTEND="noninteractive" apt-get update && apt-get -y install tzdata

RUN apt-get update \
  && apt-get install -y build-essential \
      gcc-10-aarch64-linux-gnu \
      g++-10-aarch64-linux-gnu \
      make \
      cmake \
      autoconf \
      automake \
      locales-all \
      dos2unix \
      rsync \
      tar \
      python \
      python-dev \
      python3 \
    && apt-get clean

RUN apt-get install -y python3-pip \
    && pip3 install fprime fprime-tools
