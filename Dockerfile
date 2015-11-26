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
    python python-dev python-setuptools \
	supervisor \
    libpq-dev git unzip \
    libxml2-dev libxslt1-dev libz-dev libffi-dev \
    libpcre3 libpcre3-dev libssl-dev

# Nginx
RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62
RUN echo "deb http://nginx.org/packages/ubuntu/ trusty nginx" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y nginx-full
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

RUN mkdir /opt/node
RUN chown -R app /opt/node

ENV NODE_VERSION 4.1.1
RUN wget -qO /opt/node.tar.gz https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.gz \
    && tar xfz /opt/node.tar.gz -C /opt/node --strip-components 1 \
    && mv /opt/node/bin/node /usr/local/bin/node \
    && mv /opt/node/lib/node_modules/ /usr/local/lib/ \
    && ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

# Set timezone to Europe/Helsinki
RUN echo 'Europe/Helsinki' > /etc/timezone && rm /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Helsinki /etc/localtime

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN mkdir -p /opt/app
RUN chown app /opt/app

RUN npm install -g bower
RUN npm install -g grunt-cli
RUN gem install compass

COPY package.json /opt/app/package.json
COPY bower.json /opt/app/bower.json
RUN npm install
RUN bower install --allow-root
#--config.interactive=false

ADD docker/supervisord.conf /etc/supervisor/supervisord.conf
ADD docker/nginx.conf /etc/nginx/nginx.conf

COPY . /opt/app/

RUN grunt build

EXPOSE 8000

USER root
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
