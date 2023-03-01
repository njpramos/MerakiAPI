import meraki
import meraki.aio
import asyncio
import os
import csv
import time
import datetime
from dotenv import load_dotenv

# load the environment variable

load_dotenv() 

# Initialize the Meraki Dashboard API key from .env file

KEY = os.environ.get('API_KEY')

# Initialize Organization IDs in a list

ORGANIZATIONS = ['464068', '291795']

# initialize th e monthly PSKs as dictionary

d = datetime.datetime.now()

MONTH = d.strftime('%b')

dashboard = meraki.DashboardAPI(api_key = KEY, output_log = False, print_console = False)

def get_secret():
    with open('guest-psk.csv', 'r') as f:
    
        reader = csv.DictReader(f)
        
        for row in reader:
        
            if row['Month'] == MONTH:

                return row['Secret']

# PSK = {
    # "Jan": "Apple",
    # "Feb": "Chocolate",
    # "Mar": "Strawberry",
    # "Apr": "Mango",
    # "May": "Banana",
    # "Jun": "Coconut",
    # "Jul": "Chicken",
    # "Augt": "Passionfruit",
    # "Sep": "Oreo",
    # "Oct": "Caramel",
    # "Nov": "Pineapple",
    # "Dec": "Cheese",
# }

# Get the current month

# d = datetime.datetime.now()

# MONTH = d.strftime('%b')

# Check if the network has a Wireless device

async def has_wireless(aiomeraki: meraki.aio.AsyncDashboardAPI, net_id):

    response = await aiomeraki.networks.getNetwork(net_id)
   
    if response['productTypes'].count('wireless') >= 1:
    
        return True
        
# Asynchronous function to change the PSK for all the networks using MerakiAuth
    
async def change_psk(aiomeraki: meraki.aio.AsyncDashboardAPI, net):

    if await has_wireless(aiomeraki, net['id']):
        
        # Extract  all the SSIDs

        ssids = await aiomeraki.wireless.getNetworkWirelessSsids(net['id'])
                    
        for ssid in ssids:
        
            # Extract all the McD-Guest SSIDs with Meraki RADIUS authentication

            if ssid['name'] == 'McD-Guest' and ssid['enabled'] == True and ssid['splashPage'] == 'Password-protected with Meraki RADIUS':
            
                # Extract all the MerakiAuth users
                            
                users = await aiomeraki.networks.getNetworkMerakiAuthUsers(net['id'])
        
                for user in users:
                
                    # Extract the guest user account for each network
                
                    if user['id'] == 'dmlzaXRvckBtY2QuY29tLEd1ZXN0':
                        #secret = get_secret()
                        response = dashboard.networks.updateNetworkMerakiAuthUser(net['id'], user['id'], password = get_secret())
                        print(response)
                        return net['name']

# Main function to initialize Meraki Asynchronous API and coroutines

async def main ():

    # Initialize the Meraki dashboard API for asynchronous module

    async with meraki.aio.AsyncDashboardAPI(
            KEY,
            base_url="https://api.meraki.com/api/v1",
            output_log = False,
            print_console = False
    ) as aiomeraki:

        try:
        
            for org in ORGANIZATIONS:
                
                networks = await aiomeraki.organizations.getOrganizationNetworks(org)
                
                network_task = [change_psk(aiomeraki, net) for net in networks]
                
                for task in asyncio.as_completed(network_task):
                
                    network_name = await task
                    
                    time.sleep(0.5)
                    
                    if network_name != None:
                    
                        print("="*50)
                        print(f"{network_name} guest WiFi password changed to {get_secret()}")
                        print("="*50)
                        
        except KeyboardInterrupt:
            print("Program Interrupted. Closing...")

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
