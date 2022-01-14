FROM python:3.9

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

ENV LANG de_DE.UTF-8
ENV LC_ALL de_DE.UTF-8

WORKDIR /booker

# Install backend requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && rm requirements.txt

COPY ./app ./app
COPY ./ui ./ui

CMD [ "python3", "app/booker.py"]