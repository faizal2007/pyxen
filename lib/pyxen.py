from subprocess import PIPE, run
import json
# def getOnline(app, xen_cfg, ext=0):
    # command = ['sudo', '/bin/bash', app['path'] + '/bin/getServer.sh']
    # result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
# 
    # server = []
    # cfg = ''
    # for line in result.stdout.splitlines():
        # cfg = line + '.cfg'
        # if ext:
            # server.append(line)
        # else:
            # server.append(cfg)
# 
    # return server
def getOnline(type = ''):
    command = ['sudo', '/usr/sbin/xl', 'list', '-l']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    output_string = result.stdout.strip()
    data = json.loads(output_string)
    server = []
    server_name = []
    for item in data:
        # print(item['domid'], ' ', item['config']['c_info']['name'])
        domid = item['domid']
        name = item['config']['c_info']['name']
        cpus = item['config']['b_info'].get('max_vcpus')
        memory = item['config']['b_info'].get('max_memkb')/1024
        ip = [nic.get('ip') for nic in item['config'].get('nics', [])]
        server.append(
            {
                'domid': domid,
                'name': name,
                'cpus': cpus,
                'memory': memory,
                'ip': ip
            }
        )
        server_name.append(name)
    return server_name if type == 'name' else server
        
def getOffline(xen_cfg):
    online = getOnline('name')
    server = []
    for cfg in xen_cfg:
        if cfg.replace(".cfg", "") not in online:
            server.append(cfg)

    return server
