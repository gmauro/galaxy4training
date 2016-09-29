# Based on gmauro/debian-ansible
FROM gmauro/debian-ansible
MAINTAINER Gianmauro Cuccuru <gmauro@crs4.it>

ENV DEBIAN_FRONTEND noninteractive

RUN git clone --recursive https://github.com/gmauro/galaxy4training \
 && cd galaxy4training \
 && ansible-playbook -i inventory local.yml -e brand='CI' -e admin_users='admin@example.com'
 