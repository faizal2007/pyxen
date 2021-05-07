#!/usr/bin/env python3
import click, enquiries, os, time
import configparser
from shutil import copyfile
from pathlib import Path
from subprocess import PIPE, run

config = configparser.ConfigParser()
config_path = Path('./conf/config.cnf')
autoload_list = '/etc/pyxen/autoload.list'

if not config_path.is_file():
    config_path.parent.mkdir(parents=True, exist_ok=True)
    copyfile('./config.cnf.example', config_path)

if Path('/etc/pyxen/config.cnf').is_file():
    config.read('/etc/pyxen/config.cnf')
else:
    config.read('./conf/config.cnf')

xen_dir = os.listdir(config['xen']['path'])
xen_cfg = [x for x in xen_dir if x.endswith(".cfg")]

click.clear()

@click.group()
def cli():
    pass

@click.command()
def list():
    click.echo(click.style('List Online Server.', bg='blue'))
    command = ['sudo', '/usr/sbin/xl', 'list']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    click.echo(result.stdout)

@click.command()
def start():
    click.echo(click.style('List available config.', bg='blue'))
    choice = enquiries.choose('Choose one of these options: ', xen_cfg)
    command = ['sudo', '/usr/sbin/xl', 'create', config['xen']['path'] + '/' + choice]
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    click.echo(result.stderr)

@click.command()
def shutdown():
    command = ['sudo', '/bin/bash', './bin/getServer.sh']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    server = []
    for line in result.stdout.splitlines():
        server.append(line)

    if len(server) > 0:
        choice = enquiries.choose('Choose one of these options: ', server)
        click.confirm('Do you want to continue?', abort=True)
        command = ['sudo', '/usr/sbin/xl', 'shutdown', choice]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        click.echo(result.stderr)
    else:
        click.echo('All server are offline')

@click.command()
def create():

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
                '--pygrub'
    ]

    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    click.echo(result.stdout)

@click.command()
def autoload():
    file = open(autoload_list)
    autoxen_cfg = file.read().strip()
    autoxen_list = autoxen_cfg.split('\n')

    for cfg in autoxen_list:
        command = ['sudo', '/usr/sbin/xl', 'create', config['xen']['path'] + '/' + cfg]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        click.echo(result.stderr)



cli.add_command(list)
cli.add_command(start)
cli.add_command(shutdown)
cli.add_command(create)
cli.add_command(autoload)

if __name__ == '__main__':
    cli()

