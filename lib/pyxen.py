from subprocess import PIPE, run
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from rich.prompt import Confirm
from rich.prompt import Prompt
from .util import convert_ram, convert_to_short_form

import json, re, sys, glob

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
        
def xen_cfg_ls():
    file_pattern = '/etc/xen/*.cfg'
    configs = glob.glob(file_pattern)
    cfg_ls = []
    for file_path in configs:
        try:
            cfg_ls.append(file_path)
        except:
            print(f"Error listing {file_path}: {e}")
    return cfg_ls

def get_config(xen_cfg):
    with open(xen_cfg, 'r') as config_file:
        config_content = config_file.read()
    # Parse Xen config into a dictionary
    xen_config = {}
    exec(config_content, {}, xen_config)

    return xen_config
    
def vg_display():
    command_output = run(['/usr/sbin/vgdisplay'], capture_output=True, text=True)
    # Check if the command executed successfully
    if command_output.returncode == 0:
        # Split the output into lines and create a dictionary from it
        info_dict = {}
        for line in command_output.stdout.splitlines():
            if line.strip().startswith(('VG Name', 'Format', 'Metadata', 'MAX', 'Cur', 'Open', 'Max', 'Cur', 'Act', 'PE', 'Total', 'Alloc', 'Free', 'VG Size', 'VG UUID')):       
                parts = line.split()
                key = parts[0] + ' ' + parts[1] if len(parts) > 2 else parts[0]
                value = ' '.join(parts[2:])
                info_dict[key] = value
        return info_dict
    else:
        print("Error: Unable to fetch xl info")
def list_server_info():
    total_cpus = xen_info().get('nr_cpus')
    total_memory = xen_info().get('total_memory')
    free_memory =  xen_info().get('free_memory')
    use_memory = int(total_memory) - int(free_memory)
    total_storage = vg_display().get('VG Size')
    use_storage = str(vg_display().get('Alloc PE').split('/')[2]).strip()
    free_storage = str(vg_display().get('Free PE').split('/')[2]).strip()
    table = Table(title=Text("List Online Server", style='bold white on blue'), box=box.ASCII, style='blue')
    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("ID", style="magenta")
    table.add_column("CPU", justify="right", style="green")
    table.add_column("Memory", justify="right", style="green")
    table.add_column("IP Address", justify="right", style="green")

    cpu = 0
    for server in getOnline():
        table.add_row(*(server['name'], str(server['domid']), str(server['cpus']), str(int(server['memory'])), str(server['ip'])))
        cpu += int(server['cpus'])
    console = Console()
    console.print(table)

    table = Table(title=Text("Server Summary", style='bold white on blue'), box=box.ASCII, style='blue')
    table.add_column('Item', style='cyan')
    table.add_column('Total')
    table.add_column('Use')
    table.add_column('Free')
    table.add_row('VCPUs', total_cpus, str(cpu), str(int(total_cpus)-cpu))
    table.add_row('Memory', convert_ram(total_memory), convert_ram(use_memory), convert_ram(free_memory))
    table.add_row('Storage', total_storage, use_storage,free_storage)
    console.print(table)

def create_disk(size, vg_name, disk_name):
    command_create = run(['lvcreate', '-L' + size, '-n', disk_name, vg_name], capture_output=True, text=True)
    if command_create.returncode == 0:    
        print(command_create.stdout)
    else:
        print('Error creating disk')
        print(command_create.stderr)

def create_snapshot():
    print(convert_to_short_form(lv_display()[2].get('LV Size')))

def lv_display(lv_path=None):
    command = [
        '/usr/sbin/lvdisplay',
    ]
    
    if(lv_path):
        command.append(lv_path)
    
    command_output = run(command, capture_output=True, text=True)
    if command_output.returncode == 0:
        logical_volumes = re.split(r'--- Logical volume ---\n',  command_output.stdout.strip())
        logical_volumes = [lv.strip() for lv in logical_volumes if lv.strip()]
        
        return lv_data(logical_volumes)
        
    else:
        print("Error: Unable to fetch lvdisplay")
        sys.exit(0)
    
def lv_data(logical_volumes):
    lv_lists = []    
    for lv_entry in logical_volumes:
        lv_dict = {}
        lv_lines = lv_entry.split('\n')
        for line in lv_lines:
            if line.strip().startswith(('LV Path', 'LV Name', 'VG Name', 'LV Status', 'LV Size')):
                parts = line.split()
                key = parts[0] + ' ' + parts[1] if len(parts) > 2 else parts[0]
                value = ' '.join(parts[2:])
                lv_dict[key] = value
        lv_lists.append(lv_dict)

    return lv_lists    


