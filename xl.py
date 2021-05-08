#!/usr/bin/env python3
import click, enquiries, os, time
import configparser
from shutil import copyfile
from pathlib import Path
from subprocess import PIPE, run
from lib.pyxen import getOffline, getOnline

ver = '0.1.1'
config = configparser.ConfigParser()
config_path = Path('./conf/config.cnf')
autoload_list = '/etc/pyxen/autoload.list'

if Path('/etc/pyxen/config.cnf').is_file():
    config.read('/etc/pyxen/config.cnf')
else:
    if not config_path.is_file():
        print('Config file missing.\n do check /etc/pyxen/config.cnf or ./conf/config.cnf')
    else:
        config.read('./conf/config.cnf')

xen_dir = os.listdir(config['xen']['path'])
xen_cfg = [x for x in xen_dir if x.endswith(".cfg")]

click.clear()

@click.group()
@click.version_option(ver)
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
    server = getOffline(config['app'], xen_cfg)
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
    '''
    getOnline(param1, param2, param3)
    param1 = app setting
    param2 = list xen cfg files 
    param3 = file extension (.cfg)
    '''
    server = getOnline(config['app'], xen_cfg, 1)

    if len(server) > 0:
        choice = enquiries.choose('Choose one of these options: ', server)
        click.confirm('Do you want to continue?', abort=True)

        command = ['sudo', '/usr/sbin/xl', 'shutdown', choice]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        click.echo(result.stderr)
    else:
        click.echo('All Server appeared to be offline.')

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

    server = getOnline(config['app'], xen_cfg)
    offline = []
    for cfg in autoxen_list:
        if cfg not in server:
            offline.append(cfg)

    for cfg in offline:
        command = ['sudo', '/usr/sbin/xl', 'create', config['xen']['path'] + '/' + cfg]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        time.sleep(int(config['app']['autoload_delay']))
        click.echo(result)

cli.add_command(list)
cli.add_command(start)
cli.add_command(shutdown)
cli.add_command(create)
cli.add_command(autoload)

if __name__ == '__main__':
    cli()

