# pyxen
Interactive xen tool to manage xen hypervisor

## Requirement
* Debian Buster (Tested)
* [xen-hypervisor](https://vidigest.com/2020/11/17/installing-xen-project-hypervisor-on-debian-10/)
* [xen-tools](https://vidigest.com/2020/11/17/installing-xen-project-hypervisor-on-debian-10/#S3)


## Usage
```bash
cd /usr/local/bin
wget -O pyxl https://github.com/faizal2007/pyxen/raw/main/dist/xl
chmod +x pyxl
mkdir /etc/pyxen/
cd /etc/pyxen
wget https://raw.githubusercontent.com/faizal2007/pyxen/main/conf/config.cnf
wget https://raw.githubusercontent.com/faizal2007/pyxen/main/conf/autoload.list
pyxl --help
```

## Systemd auto load vm
```bash
nano /etc/systemd/system/xen-autostart.service
```
```bash

[Unit]
Description=starts all XEN vms in /etc/pyxen/autoload.list
After=xendomains.service
Wants=xendomains.service

[Service]
User=root
Group=root
ExecStart=/usr/local/bin/pyxl autoload

[Install]
WantedBy=default.target
```
> restart service
```bash
systemctl daemon-reload
systemctl enable xen-autostart
```

## Development
```bash
 git https://github.com/faizal2007/pyxen.git
 apt-get install python-venv build-essential
 python3 -m venv venv
 source venv/bin/activate
 pip install -r requirement.txt
 mkdir /etc/pyxen/
 cp ./conf/config.cnf /etc/pyxen/
 ./xl.py
 
 # set virtual server config base on your setting
 # currently only support 1 server at a time
 mv config.conf.example ./conf/config.conf
 # run application
./xl
```
