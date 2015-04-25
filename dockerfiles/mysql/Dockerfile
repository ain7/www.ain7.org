#
# To use it, build your image:
# docker build -t ain7/mysql .
# docker run --name="ain7-mysql" -p 3306:3306 ain7/mysql
#

FROM ubuntu:14.04

MAINTAINER Lionel Porcheron <lionel@alveonet.org>

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --force-yes mysql-server

ADD local.cnf /etc/mysql/conf.d/local.cnf

EXPOSE 3306

CMD /usr/sbin/mysqld
