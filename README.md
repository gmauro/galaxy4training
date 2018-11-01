# G4T
[![TravisCI](https://api.travis-ci.org/gmauro/galaxy4training.svg?branch=master)](https://travis-ci.org/gmauro/galaxy4training)    
Galaxy 4 Training - Build in a snap a Galaxy training environment on Debian 
and Ubuntu systems  


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
 * [ansible-gx-datasets]() to install external datasets


## Main Variables

A first set of variables, that regulate the playbook execution, are available in _group_vars/all_:

 * _g4t_manage_os_setup_: (default yes) to execute or not the ansible-galaxy-os role
 * _g4t_manage_db_setup_: (default yes) to execute or not the ansible-postgresql role
 * _g4t_manage_galaxy_: (default yes) to execute or not the ansible-galaxy role
 * _g4t_manage_extras_: (default yes) to execute or not the ansible-gx-extras role
 * _g4t_manage_tools_: (default no) to execute or not the ansible-galaxy-tools role
 * _g4t_manage_datasets_: (default no) to execute or not the ansible-gx-datasets role
 
In _host_vars/localhost_, there are:

 * _brand_: text to append next to Galaxy logo in the frontpage
 * _admin_users_: a comma separated list of valid administrative users
 
You can create a new file in _host_vars_ directory named as the label used into your inventory file. 
Host specific variables, should be added here.

In _roles/role_label/defaults/main.yml_, each role has his own set of variables.

See the [ansible documentation about group variables](http://docs.ansible.com/ansible/intro_inventory.html) for details.

## How to clone this repository

Start by cloning the repository:

`git clone https://github.com/gmauro/galaxy4training`

Since the repository makes use of [submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), you first need to initialize 
all the submodules:

`cd galaxy4training`  
`git submodule update --init`

### Short way

Alternatively, with version 1.6.5 of git and later, you can pass the --recursive option to git clone and initialize all submodules:

`git clone --recursive https://github.com/gmauro/galaxy4training`

## Deploying on localhost

Clone the repository as described above and then run the playbook:

`ansible-playbook -i inventory local.yml -e brand='G4T' -e admin_users='admin@example.com`
