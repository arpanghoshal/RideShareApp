FROM ubuntu:18.04

ENV TEAM_NAME=CC_0240_0251_0268

RUN apt update && \
    apt install -y python3 && \
    apt-get install -y python3-pip && \
    pip3 install flask pymongo requests

WORKDIR /app

COPY . /app

EXPOSE 80

CMD ["python3","rides.py"]

