#!/usr/bin/python
from cmd import Cmd
from pathlib import Path
import mikrotik
from mikrotik import ApiRos as Mikrotik
import static
import re
import json
import logging

logging.basicConfig(filename='mso.log', format='%(asctime)s %(message)s', level=logging.INFO)

def setup():
    db_path = Path.cwd() / '.mso_db'
    if db_path.is_dir():
        return
    else:
        Path.mkdir(db_path)
        Path.mkdir(db_path / 'devices')
    return

# ToDo: create symlink function for latest file

class MikrotikPrompt(Cmd):
    '''
    CLI for the Mikrotik service orchestrator
    '''

    def do_exit(self, inp):
        print("Quitting Mikrotik Service Orchestrator")
        return True
    
    def do_add_device(self, inp):
        '''
        Add Mikrotik device to database
        '''
        if validate_input(inp):
            try:
                Path.mkdir(Path.cwd() / '.mso_db' / 'devices' / inp)
                device_base = Path(Path.cwd() / '.mso_db' / 'devices' / inp)
                Path.mkdir(device_base / 'config')
                Path.mkdir(device_base / 'backups')
                Path.mkdir(device_base / 'changes')
                ip_address = input('Management IP: ')
                managed_by = input('ssh / api: ')
                local_conf = {'ip_address' : ip_address, 'managed_by' : managed_by}
                open_config = open(Path(device_base / 'local_config.json'), 'w')
                open_config.writelines(json.dumps(local_conf, indent=4))
            except Exception as e:
                print(e)
    
    def do_connect(self, inp):
        '''
        Connect to Mikrotik
        '''
        # To Do: Support SSH connections
        # To Do: Support api_ssl connections
        device_path = Path(Path.cwd() / '.mso_db' / 'devices' / inp)
        with open(device_path / 'local_config.json', 'r') as json_config:
            local_config = json.load(json_config)
            ip_address = local_config['ip_address']
        try:
            s = mikrotik.open_socket(dst=ip_address, port=8728)
            mtk = Mikrotik(s)
            mtk.login(username='admin', pwd='')
        except:
            print('Failed to connect')

    def complete_connect(self, text, line, start_index, end_index):
        '''
        Complete connect
        '''
        devices = find_matching_devices(text)
        return devices

    def do_clean_config(self, inp):
        '''
        Remove device configuration from database
        '''
        print('Nothing here yet')

    def complete_clean_config(self, text, line, start_index, end_index):
        devices = find_matching_devices(text)
        return devices

    def do_backup(self, inp):
        '''
        Create a backup of the Mikrotik device
        '''
        print('Nothing here yet')
    
    def complete_backup(self, text, line, start_index, end_index):
        devices = find_matching_devices(text)
        return devices
    
    def help_exit(self):
        print('exit the application. Shorthand: x q Ctrl-D.')

    def do_list_devices(self, inp):
        p = Path(Path.cwd() / '.mso_db' / 'devices')
        for child in p.iterdir():
            child_str = str(child)
            print(child_str[child_str.rfind('/') + 1 : ])
        inp = ''
        return

    do_EOF = do_exit
    help_EOF = help_exit


class ConfigPrompt(Cmd):
    '''
    CLI for changing Configuration of Mikrotik devices
    '''
    pass


def validate_input(inp):
    if re.match('^[A-Za-z0-9_-]*$', inp):
        p = Path(Path.cwd() / '.mso_db' / 'devices')
        for path in p.iterdir():
            # Compare path of device name to add to already existing
            if str(p / inp) == str(path):
                print('Device with this name already exists.')
                return
        return True
    else:
        print('Device name must only include letters, numbers, dashes or underscores')
    return

def find_matching_devices(text):
    matching_devices = list()
    devices = list()
    p = Path(Path.cwd() / '.mso_db' / 'devices')
    # Create a list of all devices by name
    for device in p.iterdir():
        # create a string of just the device name
        device_name = str(device)[str(device).rfind('/') + 1 : ]
        devices.append(device_name)
    # Check for matching devices against input
    if text:
        for device in devices:
            if device.startswith(text):
                matching_devices.append(device)
        return matching_devices
    else:
        return devices

def find_exact_device(device_to_find):
    '''
    Returns a device's configuration
    '''
    devices = list()
    logging.info('device_to_find: ' + device_to_find)
    p = Path(Path.cwd() / '.mso_db' / 'devices')
    # Create a list of all devices by name
    for device in p.iterdir():
        # create a string of just the device name
        device_name = str(device)[str(device).rfind('/') + 1 : ]
        devices.append(device_name)
    # Check for matching devices against input
    for device in devices:
        if device == device_to_find:
            # Found device
            logging.info('Found device: ' + device)
            device_path = Path(Path.cwd() / '.mso_db' / 'devices' / device)
            return device_path
        

def main():
    setup()
    p = MikrotikPrompt()
    p.cmdloop()
    return

if __name__ == '__main__':
    main()
