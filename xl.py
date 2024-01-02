#!/usr/bin/env python3
import click, enquiries, os, time
import configparser
import signal, sys
from shutil import copyfile
from pathlib import Path
from subprocess import PIPE, run
from lib.pyxen import getOffline, getOnline, xen_info, vg_display, list_server_info, create_disk
from lib.util import generate_password, convert_ram
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from rich.prompt import Confirm
from rich.prompt import Prompt
from rich import print
from rich.panel import Panel
import re

ver = '0.1.9'
config = configparser.ConfigParser()
config_path = Path('./conf/config.cnf')
autoload_list = '/etc/pyxen/autoload.list'

if Path('/etc/pyxen/config.cnf').is_file():
    config.read('/etc/pyxen/config.cnf')
else:
    if not config_path.is_file():
        print('Config file missing.\n do check /etc/pyxen/config.cnf or ./conf/config.cnf')
        sys.exit(1) 
    else:
        config.read('./conf/config.cnf')

if 'xen' in config:
    xen_dir = os.listdir(config['xen']['path'])
    xen_cfg = [x for x in xen_dir if x.endswith(".cfg")]

#click.clear()

@click.group()
@click.version_option(ver)
def cli():
    pass

@click.command()
def list():
    list_server_info()
    
@click.command()
def list_images():
    command = ['sudo', '/usr/bin/xen-list-images']
    click.echo(click.style('List available images.', bg='blue'))
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    # click.echo(result.stdout)
    print(Panel.fit(result.stdout))

@click.command()
def start():
    server = getOffline(xen_cfg)
    if len(server) > 0:
        click.echo(click.style('List available config.', bg='blue'))
        choice = enquiries.choose('Choose one of these options: ', server)
        command = ['sudo', '/usr/sbin/xl', 'create', config['xen']['path'] + '/' + choice]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        click.echo(result.stderr)
    else:
        click.echo(click.style("All Server appeared to be online.", bg='green'))

@click.command()
def shutdown():
    server = getOnline('name')

    if len(server) > 0:
        choice = enquiries.choose('Choose one of these options: ', server)
        confirmation = Confirm.ask('Do you want to continue?')
        if confirmation:
            command = ['sudo', '/usr/sbin/xl', 'shutdown', choice]
            result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            click.echo(result.stderr)
        else:
            click.echo('User cancel')
    else:
        click.echo('All Server appeared to be offline.')

@click.command()
def destroy():
    server = getOnline('name')
    
    if len(server) > 0:
        choice = enquiries.choose('Choose one of these options: ', server)
        # click.confirm('Do you want to continue?', abort=True)
        confirmation = Confirm.ask('Do you want to continue?')
        if confirmation:
            command = ['sudo', '/usr/sbin/xl', 'destroy', choice]
            result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            click.echo(result.stderr)
        else:
            click.echo('User cancel')
    else:
        click.echo('All Server appeared to be offline.')

@click.command()
def create():

    types = [
        'debootstrap',
        'iso',
        'snapshot',
        'disk'
    ]

    choice = enquiries.choose('Choose one of these options: ', types)
    
    if choice == 'debootstrap':
        bridge = Prompt.ask('Enter bridge name')
        command = [
                    'sudo', '/usr/bin/xen-create-image',
                    '--hostname=' + config['template']['hostname'],
                    '--size=' + config['template']['size'],
                    '--memory=' + config['template']['memory'],
                    '--swap=' + config['template']['swap'],
                    '--lvm=' + config['template']['lvm'],
                    '--ip=' + config['template']['ip'],
                    '--netmask=' + config['template']['netmask'],
                    '--gateway=' + config['template']['gateway'],
                    '--arch=' + config['template']['arch'],
                    '--install-method=' + config['template']['install-method'],
                    '--dist=' + config['template']['dist'],
                    '--password='+ generate_password(),
                    '--bridge='+ bridge,
                    '--role=sudoers',
                    '--pygrub'
        ]

        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        click.echo(result.stdout)
    elif choice == 'iso':
        click.echo(click.style("Creating Server using iso.", bg='green'))
        hostname = Prompt.ask('Enter hostname')
        vcpu = Prompt.ask('Enter vCPU no')
        memory = Prompt.ask('Enter memory size in mb')
        swap = Prompt.ask('Enter swap size in mb')
        disk = Prompt.ask('Enter disk size in mb')
        ip_address = Prompt.ask('Enter ip address')
        netmask = Prompt.ask('Enter netmask')
        gateway = Prompt.ask('Enter gateway')
        bridge = Prompt.ask('Enter bridge name')

    elif choice == 'disk':
        click.echo(click.style("Create disk ", bg='green'))
        disk_size = Prompt.ask('Enter disk size')
        vg_name = Prompt.ask('Enter vg name')
        disk_name = Prompt.ask('Enter disk name')

        create_disk(disk_size, vg_name, disk_name)
    else:
        print('Option not available.')

@click.command()
def autoload():
    file = open(autoload_list)
    autoxen_cfg = file.read().strip()
    autoxen_list = autoxen_cfg.split('\n')

    offline_server = getOffline(xen_cfg)

    for cfg in offline_server:
        command = ['sudo', '/usr/sbin/xl', 'create', config['xen']['path'] + '/' + cfg]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        # click.echo(result)

@click.command()
def delete():
    offline_server = getOffline(xen_cfg)
    

    if len(offline_server) < 1:
        click.echo(click.style("No Server Found.", bg='cyan'))
        sys.exit(1)
        
    choice = enquiries.choose('Choose one of these options: ', offline_server)
    confirmation = Confirm.ask('Do you want to continue?')

    if confirmation:
        click.echo('VG Name : ' + vg_display().get('VG Name'))
        vg_group = Prompt.ask('Enter VG Name')
        vm_name = os.path.splitext(choice)[0]
        command = ['sudo', '/usr/bin/xen-delete-image', '--lvm', vg_group, vm_name]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        click.echo(result.stdout)
    else:
        click.echo('User cancel')

cli.add_command(list)
cli.add_command(list_images)
cli.add_command(start)
cli.add_command(shutdown)
cli.add_command(destroy)
cli.add_command(create)
cli.add_command(autoload)
cli.add_command(delete)

if __name__ == '__main__':
    # Register a signal handler for Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))
    cli()

