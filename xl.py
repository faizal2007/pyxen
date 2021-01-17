#!/usr/bin/env python3
import click, enquiries, os
from subprocess import PIPE, run
import configparser

config = configparser.ConfigParser()
config.read('config.cnf')
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

cli.add_command(list)
cli.add_command(start)
cli.add_command(shutdown)

if __name__ == '__main__':
    cli()

