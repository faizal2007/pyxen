from subprocess import PIPE, run

def getOnline(app, xen_cfg, ext=0):
    command = ['sudo', '/bin/bash', app['path'] + '/bin/getServer.sh']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    server = []
    cfg = ''
    for line in result.stdout.splitlines():
        cfg = line + '.cfg'
        if ext:
            server.append(line)
        else:
            server.append(cfg)

    return server

def getOffline(app, xen_cfg):
    online = getOnline(app, xen_cfg)

    server = []
    for cfg in xen_cfg:
        if cfg not in online:
            server.append(cfg)

    return server
