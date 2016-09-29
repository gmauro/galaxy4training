# G4T
Galaxy 4 Training - Builder for Galaxy training environment
[![TravisCI](https://api.travis-ci.org/gmauro/galaxy4training.svg?branch=master)](https://travis-ci.org/gmauro/galaxy4training)

## Ansible roles
 * [common]() place where variables available to all roles are defined.
 * [ansible-galaxy-os](https://github.com/galaxyproject/ansible-galaxy-os) to configure the base operating system useful for running Galaxy.
 * [ansible-postgresql](https://github.com/gmauro/ansible-postgresql) to setup the PostgreSQL server
 * [ansible-galaxy](https://github.com/galaxyproject/ansible-galaxy) to configure the Galaxy server.
 * [ansible-gx-extras](https://github.com/gmauro/ansible-gx-extras) to configure several production services as Nginx, Uwsgi and Supervisor.
 * [ansible-galaxy-tools](https://github.com/galaxyproject/ansible-galaxy-tools)  for automated installation of tools from a Tool Shed into Galaxy.
 * [ansible-gx-datasets]() to install external datasets
