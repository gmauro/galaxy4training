# Galaxy4Training
[![TravisCI](https://api.travis-ci.org/gmauro/galaxy4training.svg?branch=master)](https://travis-ci.org/gmauro/galaxy4training)    
Build in a snap a Galaxy environment for a training classroom of 20-30 participants to allow high interactivity and shared practical work.

This Ansible playbook has been developed and tested on Debian and Ubuntu 
systems.

## Requirements  
In order to use this playbook, you need:

 * [git](https://git-scm.com/)
 * [ansible >= 2.4](http://docs.ansible.com/ansible/intro_installation.html)

## Ansible roles  
List of roles included in this playbook:

 * [common](https://github.com/gmauro/galaxy4training/tree/master/roles/common/vars) place where variables available to all roles are defined.
 * [ansible-galaxy-os](https://github.com/galaxyproject/ansible-galaxy-os) to configure the base operating system useful for running Galaxy.
 * [ansible-postgresql](https://github.com/gmauro/ansible-postgresql) to setup the PostgreSQL server
 * [ansible-galaxy](https://github.com/galaxyproject/ansible-galaxy) to configure the Galaxy server.
 * [ansible-gx-extras](https://github.com/gmauro/ansible-gx-extras) to configure several production services as Nginx, Uwsgi and Supervisor.
 * [ansible-galaxy-tools](https://github.com/galaxyproject/ansible-galaxy-tools)  for automated installation of tools from a Tool Shed into Galaxy.


## Control flow variables

A first set of variables, that regulate the playbook execution, are available in _group_vars/all_:

 * _g4t_manage_os_setup_: (default yes) to execute or not the ansible-galaxy-os role
 * _g4t_manage_db_setup_: (default yes) to execute or not the ansible-postgresql role
 * _g4t_manage_galaxy_: (default yes) to execute or not the ansible-galaxy role
 * _g4t_manage_extras_: (default yes) to execute or not the ansible-gx-extras role
 * _g4t_manage_tools_: (default no) to execute or not the ansible-galaxy-tools role
 * _g4t_manage_datasets_: (default no) to execute or not the ansible-gx-datasets role
 
 
## Main variables

All the variables that can be configured to execute this playbook are 
collected into  
_roles/common/vars/main.yml_ .

Apply your modifications there.
 
## How to clone this repository

Since this repository makes use of [submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), 
you can pass the --recursive option to git clone and initialize all submodules:


`git clone --recursive https://github.com/gmauro/galaxy4training`

## Deploying on localhost

Clone the repository as described above and then run the playbook:

`ansible-playbook -i inventory g4t.yml -e brand='G4T' -e admin_users='admin@example.com`

## Development

Easily prepare a development setup using [Docker](https://docs.docker.com) in 
this way:

 * Clone the repository  
 `git clone --recursive https://github.com/gmauro/galaxy4training`
 
 * Edit the code on your machine
 
 * start a docker container  
 `docker run -p 8080:80 -v /path/to/galaxy4training:/galaxy4training --rm -ti gmauro/ansible:2.6_ubuntu16.04 /bin/bash`
  
 * Start Galaxy deployment on the docker container  
 `cd galaxy4training && ansible-playbook g4t.yml`

 * Check the result on your browser at [localhost](http://localhost:8080)
 