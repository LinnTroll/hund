FROM python:2.7
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get -y install mysql-client xfonts-base xfonts-75dpi xvfb

RUN wget https://bitbucket.org/wkhtmltopdf/wkhtmltopdf/downloads/wkhtmltox-0.13.0-alpha-7b36694_linux-jessie-amd64.deb
RUN dpkg -i wkhtmltox-0.13.0-alpha-7b36694_linux-jessie-amd64.deb

RUN pip install --upgrade pip

RUN mkdir /project
ADD . /project/
WORKDIR /project/

RUN pip install -r requirements.txt