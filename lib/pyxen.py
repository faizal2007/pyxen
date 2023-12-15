from subprocess import PIPE, run
import json

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
        if domid != 0:
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

def xen_info():

    # Run the `xl info` command
    command_output = run(['xl', 'info'], capture_output=True, text=True)

    # Check if the command executed successfully
    if command_output.returncode == 0:
        # Split the output into lines and create a dictionary from it
        info_dict = {}
        for line in command_output.stdout.splitlines():
            key, value = line.split(':', 1)
            info_dict[key.strip()] = value.strip()

        return info_dict
    else:
        print("Error: Unable to fetch xl info")
def vg_display():
    command_output = run(['/usr/sbin/vgdisplay'], capture_output=True, text=True)
    # Check if the command executed successfully
    if command_output.returncode == 0:
        # Split the output into lines and create a dictionary from it
        info_dict = {}
        for line in command_output.stdout.splitlines():
            if line.strip():
                key, value = line.split(maxsplit=1)
                if key != '---':      
                     info_dict[key.strip()] = value.strip()
                     

        return info_dict
    else:
        print("Error: Unable to fetch xl info")

