FROM ubuntu:20.04

RUN apt update
RUN apt-get install -y python3 python3-pip build-essential python3-dev patchelf
RUN pip3 install nuitka
RUN apt-get install -y libz-dev

RUN pip3 install pymcuprog
