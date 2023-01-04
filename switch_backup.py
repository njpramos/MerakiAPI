import meraki
import os
import json
import datetime
import argparse
from dotenv import load_dotenv

# load the environment variable

load_dotenv() 

# Initialize the Meraki Dashboard API key from .env file

key = os.environ.get('API_KEY')

# Create an instance of Meraki Dashboard API

dashboard = meraki.DashboardAPI(key)

date_created = datetime.datetime.now() # Generates a dynamic date/year info

# Initialize the local path directory

path = os.environ.get('DIR_PATH') + date_created.strftime('%b') + "_" + date_created.strftime('%Y')

# path.encode('unicode_escape') # Escape the backslashes '\' 

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

    return switchport_list

# Main function

def main():
    try:
        for network_id in network_id_list:
            devices = get_network_devices(network_id)
            #print("\n ================ " + get_network_name(devices[0]['networkId']) + " ================ \n")
            if len(devices) != 0:
                network_name = get_network_name(devices[0]['networkId'])
                new_path = path + r'\\' + network_name
                if network_name.find("LAB") == -1:
                    if not os.path.exists(new_path): # Create directory for CMN sites
                       os.makedirs(new_path)
                    for device in devices:
                        if device['model'].find('MS') != -1: # Extract only CMN MS switch devices
                        #print(type(device))
                            if "name" in device: # Execute if the switch has a label/hostname
                                #print("Switch Name: " + device['name'] + " \n " + "Serial No.: " + device['serial'] + " \n", get_device_switchport(device['serial']))
                                file_path = os.path.join(new_path + '\\', device['name'] + ".txt") 
                                with open(file_path, "w") as text_file:
                                    device_list = get_device_switchport(device['serial'])
                                    text_file.write(device['serial'] + "\n\n" + "".join(str(f) for f in device_list))
                                   
                            else:
                                #print("Switch Name: " + device['mac'] + " \n " + "Serial No.: " + device['serial'] + " \n ", get_device_switchport(device['serial']))
                                file_path = os.path.join(new_path + '\\', device['mac'] + ".txt")
                                with open(file_path, "w") as text_file:
                                    device_list = get_device_switchport(device['serial'])
                                    text_file.write(device['mac'] + "\n\n" + "".join(str(f) for f in device_list))
    except KeyboardInterrupt:
        print("Program Interrupted")
    except:
        print("There was an error during the program execution")
 
 
# Initializes the program and parsing the organization ID from the CLI

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog = '[py | python3] switch_backup.py', description = 'Extracts swichport configurations for all the networks in an organization and save it to a text file', epilog = 'i.e. py switch_backup.py -o 123456')

    parser.add_argument('-o', '--organization', help = 'A valid Meraki organization ID')

    args = parser.parse_args()

    if args.organization != None:
        network_id_list = get_network_id(args.organization) # Call the function to extract all the Network IDs and store in a list
        main() # Invoke the main function
    else:
        parser.print_help()
