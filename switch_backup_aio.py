import meraki
import meraki.aio
import asyncio
import datetime
import os
import json
from dotenv import load_dotenv

# load the environment variable

load_dotenv()

# Initialize the Meraki Dashboard API key from .env file

KEY = os.environ.get('API_KEY')

# Initialize Organization IDs in a list

ORGS = ['464068', '291795']

# Generates a dynamic date/year info

date_created = datetime.datetime.now()

# Initialize the local path directory

PATH = os.environ.get('DIR_PATH') + date_created.strftime('%b') + "_" + date_created.strftime('%Y')

# Append a timestamp for folder versioning

VERSION = date_created.strftime('%d_%b_%Y_%H_%M')

# Extract all the Network IDs from an Org ID
        
async def get_network_devices(aiomeraki: meraki.aio.AsyncDashboardAPI, net_id):
    try:    
        response = await aiomeraki.networks.getNetworkDevices(net_id)

    except meraki.AsyncAPIError as e:

        print(f'Meraki API error: {e}')

    except Exception as e:

        print(f'Error during execution: {e}')

    return response

# Check if the network has a switch device

async def has_switch(devices):
    
    for device in devices:
    
        if device['model'].find('MS') != -1:
        
            return True

# Extract all the switchport configuration from a switch serial no.

async def get_device_switchport(aiomeraki: meraki.aio.AsyncDashboardAPI, serial):
    try:
        switchports = await aiomeraki.switch.getDeviceSwitchPorts(serial)
    
    except meraki.AsyncAPIError as e:

        print(f'Meraki API error: {e}')

    except Exception as e:

        print(f'Error during execution: {e}')
    else:
        switchport_list = []
        
        for port in switchports:
        
            switchport_list.append(json.dumps(port, indent = 4))

        return switchport_list

# Save the individial switchport configurations for each network to a text file

async def save_swport_config(aiomeraki: meraki.aio.AsyncDashboardAPI, net, org_path):
    
    net_name = net['name'].strip().upper()

    try:

        devices = await aiomeraki.networks.getNetworkDevices(net['id'])

    except meraki.AsyncAPIError as e:

        print(f'Meraki API error: {e}')

    except Exception as e:

        print(f'Error during execution: {e}')

    else:

        if len(devices) != 0: # Extract only networks with devices

            new_path = org_path + r'\\' + net_name
            
            if net_name.find("LAB") == -1 and await has_switch(devices):

                os.makedirs(new_path)

                for device in devices:
                    
                    if device['model'].find('MS') != -1: # Extract only CMN MS switch devices
                        
                        if device['model'].find('MS') != -1: # Extract only CMN MS switch devices
                            
                            if "name" in device: # Execute if the switch has a label/hostname
                            
                                file_path = os.path.join(new_path + '\\', device['name'] + ".txt")
                                
                                with open(file_path, "w") as text_file:
                                
                                    device_list = await get_device_switchport(aiomeraki, device['serial'])
                                    
                                    text_file.write(device['serial'] + "\n\n" + "".join(str(f) for f in device_list))
                                    
                            else: # Execute otherwise (using MAC address as default label/hostname)
                            
                                file_path = os.path.join(new_path + '\\', device['mac'] + ".txt")
    
                                with open(file_path, "w") as text_file:
                                
                                    device_list = await get_device_switchport(aiomeraki, device['serial'])
        
                                    text_file.write(device['mac'] + "\n\n" + "".join(str(f) for f in device_list))
                        
                return net_name
        
async def main():

    # Initialize the Meraki dashboard API for asynchronous module

    async with meraki.aio.AsyncDashboardAPI(
            KEY,
            base_url="https://api.meraki.com/api/v1",
            output_log = False,
            print_console = False
    ) as aiomeraki:
        
        for org in ORGS:
            try:
                organizations = await aiomeraki.organizations.getOrganization(org)

            except meraki.AsyncAPIError as e:
                print(f'Meraki API error: {e}')
            except Exception as e:
                print(f'Error during execution: {e}')
            else:
                org_path = PATH + r'\\' + organizations['name'].upper() + "_" + VERSION

                networks = await aiomeraki.organizations.getOrganizationNetworks(org)
            
                network_tasks = [save_swport_config(aiomeraki, net, org_path) for net in networks]

                for task in asyncio.as_completed(network_tasks):

                    network_name = await task

                    if network_name != None:

                        print(f"Finished Network: {network_name}")

if __name__ == "__main__":

    try:

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

    except KeyboardInterrupt:
        
        print("Program Interrupted. Closing...")