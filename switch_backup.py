import meraki
import os
import json
import time
import datetime
import argparse
from dotenv import load_dotenv

# load the environment variable

load_dotenv() 

# Initialize the Meraki Dashboard API key from .env file

key = os.environ.get('API_KEY')

# Initialize Organization IDs in a list

org_id = ['464068', '291795']

# Create an instance of Meraki Dashboard API

dashboard = meraki.DashboardAPI(api_key = key, output_log = False, print_console = False)

# Generates a dynamic date/year info

date_created = datetime.datetime.now() 

# Initialize the local path directory

path = os.environ.get('DIR_PATH') + date_created.strftime('%b') + "_" + date_created.strftime('%Y')

# Append a timestamp for folder versioning

version = date_created.strftime('%w_%b_%Y_%H_%M')

# version = date_created.strftime('%w') + "_" + date_created.strftime('%b') + "_" + date_created.strftime('%Y') + "_"  + date_created.strftime('%H') + date_created.strftime('%M')

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
    
# Check if the network has a switch device
    
def has_switch(devices):
    
    for device in devices:
    
        if device['model'].find('MS') != -1:
        
            return True
            
            # continue

# Display a progress bar in the command line

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    
    filledLength = int(length * iteration // total)
    
    bar = fill * filledLength + '-' * (length - filledLength)
    
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
    
        print()
        
# Main function

def main():

    network_count = len(network_id_list)
    
    printProgressBar(0, network_count, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    for i, network_id in enumerate(network_id_list):
        
        devices = get_network_devices(network_id)
        #print("\n ================ " + get_network_name(devices[0]['networkId']) + " ================ \n")
        if len(devices) != 0: # Extract only CMN MS switch devices
        
            network_name = get_network_name(devices[0]['networkId']).upper()
            
            # network_name = get_network_name(network_id).upper() # alternative code for the line above
            
            new_path = org_path + r'\\' + network_name
            
            if network_name.find("LAB") == -1 and has_switch(devices):
            
                #if not os.path.exists(new_path): # Create directory for CMN sites
                
                os.makedirs(new_path)
                
                for device in devices:
                    
                    if device['model'].find('MS') != -1: # Extract only CMN MS switch devices
                        
                        if "name" in device: # Execute if the switch has a label/hostname
                            #print("Switch Name: " + device['name'] + " \n " + "Serial No.: " + device['serial'] + " \n", get_device_switchport(device['serial']))
                            file_path = os.path.join(new_path + '\\', device['name'] + ".txt")
                            
                            with open(file_path, "w") as text_file:
                            
                                device_list = get_device_switchport(device['serial'])
                                
                                text_file.write(device['serial'] + "\n\n" + "".join(str(f) for f in device_list))
                                
                        else: # Execute otherwise (using MAC address as default label/hostname)
                            #print("Switch Name: " + device['mac'] + " \n " + "Serial No.: " + device['serial'] + " \n ", get_device_switchport(device['serial']))
                            file_path = os.path.join(new_path + '\\', device['mac'] + ".txt")
                            
                            with open(file_path, "w") as text_file:
                            
                                device_list = get_device_switchport(device['serial'])
                                
                                text_file.write(device['mac'] + "\n\n" + "".join(str(f) for f in device_list))
            
        time.sleep(0.1)
        
        printProgressBar(i + 1, network_count, prefix = 'Progress:', suffix = 'Complete', length = 50)
 
# Initializes the program and parsing the organization ID from the CLI

# if __name__ == '__main__':

    # parser = argparse.ArgumentParser(prog = '[py | python3] switch_backup.py', description = 'Extracts swichport configurations for all the networks in an organization and save it to a text file', epilog = 'i.e. py switch_backup.py -o 123456')

    # parser.add_argument('-o', '--organization', help = 'A valid Meraki organization ID')

    # args = parser.parse_args()

    # if args.organization != None:
    
        # network_id_list = get_network_id(args.organization) # Call the function to extract all the Network IDs and store in a list
        
        # main() # Invoke the main function
    # else:
    
        # parser.print_help()

if __name__ == '__main__':

    try:

        for org in org_id:
        
            network_id_list = get_network_id(org)
            
            if org == '464068':
            
                # network_id_list = get_network_id(org)
            
                print("APMEA\n")
                # Create dir path w/ timestamp
                
                org_path = path + r'\\' + "APMEA" + "_" + version
                
                main()
                
                #print(org_path + " - OK")
                
            else:
            
                # network_id_list = get_network_id(org)
            
                print("EU\n")
                # Create dir path w/ timestamp
                
                org_path = path + r'\\' + "EU" + "_" + version

                main()
                
                #print(org_path + " - OK")
                
    except KeyboardInterrupt:
        
        print("Program Interrupted")
        
    except:
        
        print("There was an error during the program execution")
 