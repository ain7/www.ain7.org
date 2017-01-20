#
# To use it, build your image:
# docker build -t ain7/mysql .
# docker run --name="ain7-mysql" -p 3306:3306 ain7/mysql
#

FROM ubuntu:16.04

MAINTAINER Lionel Porcheron <lionel@alveonet.org>

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y dist-upgrade && apt-get install -y mysql-server

ADD local.cnf /etc/mysql/conf.d/local.cnf

EXPOSE 3306

CMD ["/usr/sbin/mysqld"]
