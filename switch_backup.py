import meraki
import os
import json
from dotenv import load_dotenv

# load the environment variable

load_dotenv() 

# Initialize the Meraki Dashboard API key from .env file

key = os.environ.get('API_KEY')

dashboard = meraki.DashboardAPI(key)

organization_id = os.environ.get('APMEA_ORG_ID')

# Initialize the local path directory

path = r'C:\Users\nomer.ramos\Documents\CMN_Backup_Jan_2023'

# Extract all the Network IDs from an Org ID

def get_network_id(org_id):

        networks = dashboard.organizations.getOrganizationNetworks(org_id)

        network_list = []
        
        for network in networks:
                
            network_list.append(network['id'])
                
        return network_list
        
# Extract the Network name from a Network ID
        
def get_network_name(net_id):

        response = dashboard.networks.getNetwork(net_id)
        
        network_name = response['name'].strip()
        
        return network_name

# Extract all the Network devices from a Network ID
        
def get_network_devices(net_id):
        
        net_devices = dashboard.networks.getNetworkDevices(net_id)

        return net_devices
        
# Extract all the switchport configuration from a switch serial no.

def get_device_switchport(serial):

        switchports = dashboard.switch.getDeviceSwitchPorts(serial)
        
        switchport_list = []
        
        for port in switchports:
            switchport_list.append(json.dumps(port, indent = 4))
            
            
        #print(switchport_list)

        return switchport_list

# Main program

network_id_list = get_network_id(organization_id)
try:
    for network_id in network_id_list:
        devices = get_network_devices(network_id)
        #print("\n ================ " + get_network_name(devices[0]['networkId']) + " ================ \n")
        if len(devices) != 0: 
            #new_path = path + r'\\' + get_network_name(devices[0]['networkId'])
            #if not os.path.exists(new_path):
            #    os.makedirs(new_path)
            for device in devices:
                if device['model'].find('MS') != -1:
                #print(type(device))
                    if "name" in device:
                        print("Switch Name: " + device['name'] + " \n " + "Serial No.: " + device['serial'] + " \n", get_device_switchport(device['serial']))
                        # file_path = os.path.join(new_path + '\\', device['name'] + ".txt") 
                        # with open(file_path, "w") as text_file:
                            # device_list = get_device_switchport(device['serial'])
                            # text_file.write(device['serial'] + "\n\n" + "".join(str(f) for f in device_list))
                           
                    else:
                        print("Switch Name: " + device['mac'] + " \n " + "Serial No.: " + device['serial'] + " \n ", get_device_switchport(device['serial']))
                        # file_path = os.path.join(new_path + '\\', device['mac'] + ".txt")
                        # with open(file_path, "w") as text_file:
                            # device_list = get_device_switchport(device['serial'])
                            # text_file.write(device['mac'] + "\n\n" + "".join(str(f) for f in device_list))
except KeyboardInterrupt:
    print("Program Interrupted")
except:
    print("There was an error during the program execution")
    