#
# To use it, build your image:
# docker build -t ain7/redis .
# docker run --name="ain7-redis" -p 6379:6379 ain7/redis
#

FROM ubuntu:14.04

MAINTAINER Lionel Porcheron <lionel@alveonet.org>

RUN apt-get update && apt-get install -y --force-yes redis-server

ADD redis.conf /etc/redis/redis.conf

EXPOSE 6379

CMD /usr/bin/redis-server
