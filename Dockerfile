FROM ubuntu:14.04
MAINTAINER Jussi Vaihia <jussi.vaihia@futurice.com>

WORKDIR /opt/app
RUN useradd -m app

# Configure apt to automatically select mirror
RUN echo "deb mirror://mirrors.ubuntu.com/mirrors.txt trusty main restricted universe\n\
deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-updates main restricted universe\n\
deb mirror://mirrors.ubuntu.com/mirrors.txt trusty-security main restricted universe" > /etc/apt/sources.list

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
	build-essential vim htop wget \
    python python-dev python-pip \
	supervisor \
    libpq-dev git unzip \
	redis-server \
    libxml2-dev libxslt1-dev libz-dev libffi-dev \
    libpcre3 libpcre3-dev libssl-dev

# Nginx
RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62
RUN echo "deb http://nginx.org/packages/ubuntu/ trusty nginx" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y nginx-full
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# Set timezone to Europe/Helsinki
RUN echo 'Europe/Helsinki' > /etc/timezone && rm /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Helsinki /etc/localtime

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN mkdir -p /opt/app
RUN chown app /opt/app

COPY requirements.txt /opt/app/requirements.txt
RUN pip install -r requirements.txt

ADD docker/supervisord.conf /etc/supervisor/supervisord.conf
ADD docker/nginx.conf /etc/nginx/nginx.conf

COPY . /opt/app/

ENV CELERY_LOG_LEVEL WARNING

EXPOSE 8000

USER root
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
