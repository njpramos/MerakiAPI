import meraki
import meraki.aio
import asyncio
import os
import time
from dotenv import load_dotenv

# load the environment variable

load_dotenv() 

# Initialize the Meraki Dashboard API key from .env file

key = os.environ.get('API_KEY')

# Initialize Organization IDs in a list

ORGANIZATIONS = ['464068', '291795']
    
async def has_wireless(aiomeraki: meraki.aio.AsyncDashboardAPI, net_id):

    response = await aiomeraki.networks.getNetwork(net_id)
   
    if response['productTypes'].count('wireless') >= 1:
    
        return True
        # if network['productTypes'].find('Wireless') == -1:
            # return True

# def update_secret(net_id, user_id):
    
    # response = dashboard.networks.updateNetworkMerakiAuthUser(network_id, meraki_auth_user_id, secret = 'Strawberry')
    
    
async def change_psk(aiomeraki: meraki.aio.AsyncDashboardAPI, net):

    if await has_wireless(aiomeraki, net['id']):

        ssids = await aiomeraki.wireless.getNetworkWirelessSsids(net['id'])

                    #ssid = dashboard.wireless.getNetworkWirelessSsidSplashSettings(network['id'], 2)
                    #print("="*10)
                    
        for ssid in ssids:

            if ssid['name'] == 'McD-Guest' and ssid['enabled'] == True and ssid['splashPage'] == 'Password-protected with Meraki RADIUS':
                            
                            #print(network_name)
                            #print(ssid['number'], ssid['name'])
                            
                users = await aiomeraki.networks.getNetworkMerakiAuthUsers(net['id'])
        
                for user in users:
                    if user['id'] == 'dmlzaXRvckBtY2QuY29tLEd1ZXN0':
                    
                        #response = dashboard.networks.updateNetworkMerakiAuthUser(network['id'], user['id'], secret = 'Strawberry')
                        
                        #print(user['id'])
                        
                        return net['name']

async def main ():

    async with meraki.aio.AsyncDashboardAPI(
            key,
            base_url="https://api.meraki.com/api/v1",
            output_log = False,
            print_console = False
    ) as aiomeraki:


        for org in ORGANIZATIONS:
            
            networks = await aiomeraki.organizations.getOrganizationNetworks(org)
            
            network_task = [change_psk(aiomeraki, net) for net in networks]
            
            for task in asyncio.as_completed(network_task):
            
                network_name = await task
                
                time.sleep(0.5)
                
                #if network_name != None:
                print(f"{network_name} password changed!")
                
                #print(network_name)
                
                                    #response = dashboard.networks.updateNetworkMerakiAuthUser(network['id'], user['id'], secret = 'Strawberry')
                                    
                                    #print(response)
                
            # if ssid['splashMethod'] == 'Password-protected with Meraki RADIUS':
                # print(network_name, ssid['ssidNumber'])
            
            # get network SSIDS
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    

