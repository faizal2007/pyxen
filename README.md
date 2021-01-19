# pyxen
Interactive xen tool to manage xen hypervisor

## Requirement
* Debian Buster (Tested)
* xen-hypervisor
* xen-tools
* python3 and above
  * python-venv

## Installation (normal user)
```bash
 git https://github.com/faizal2007/pyxen.git
 apt-get install python-venv
 python3 -m venv venv
 source venv/bin/activate
 pip install -r requirement.txt
 mkdir conf
 # set config base on your server configuration
 mv config.conf.example ./conf/config.conf
 # run application
./xl
```
