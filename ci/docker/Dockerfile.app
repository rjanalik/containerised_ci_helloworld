ARG IMG
FROM $IMG as builder

COPY . /helloworld/src

RUN apt-get update \
  && env DEBIAN_FRONTEND=noninteractive TZ=Europe/Zurich apt-get -yqq install --no-install-recommends build-essential cmake \
  && mkdir /helloworld/build \
  && cd /helloworld/build \
  && cmake -DCMAKE_INSTALL_PREFIX=/opt/hello ../src \
  && make -j$(cat /proc/cpuinfo | grep '^processor' | wc -l) install \
  && make install
