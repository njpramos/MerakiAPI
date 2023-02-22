import meraki
import os
import threading
from dotenv import load_dotenv

# load the environment variable

load_dotenv() 

# Initialize the Meraki Dashboard API key from .env file

key = os.environ.get('API_KEY')

# Initialize Organization IDs in a list

ORGANIZATIONS = ['464068', '291795']

# Create an instance of Meraki Dashboard API

dashboard = meraki.DashboardAPI(api_key = key, output_log = False, print_console = False)

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
    
def has_wireless(net_id):

    response = dashboard.networks.getNetwork(net_id)
   
    if response['productTypes'].count('wireless') >= 1:
    
        return True
        # if network['productTypes'].find('Wireless') == -1:
            # return True

# def update_secret(net_id, user_id):
    
    # response = dashboard.networks.updateNetworkMerakiAuthUser(network_id, meraki_auth_user_id, secret = 'Strawberry')

for org in ORGANIZATIONS:
    
    networks = dashboard.organizations.getOrganizationNetworks(org)

    for network in networks:
        #network_id = print(network['id'])
        network_name = get_network_name(network['id'])
        #print(network_name)
        if has_wireless(network['id']):
        

            ssids = dashboard.wireless.getNetworkWirelessSsids(network['id'])

            #ssid = dashboard.wireless.getNetworkWirelessSsidSplashSettings(network['id'], 2)
            #print("="*10)
            
            for ssid in ssids:

                if ssid['name'] == 'McD-Guest' and ssid['enabled'] == True and ssid['splashPage'] == 'Password-protected with Meraki RADIUS':
                    print(network_name)
                    #print(ssid['number'], ssid['name'])
                    
                    users = dashboard.networks.getNetworkMerakiAuthUsers(network['id'])
  
                    for user in users:
                        if user['email'] == 'visitor@mcd.com':
                            print(user['id'])
                            #response = dashboard.networks.updateNetworkMerakiAuthUser(network['id'], user['id'], secret = 'Strawberry')
                            
                            #print(response)
        print("="*10)
        # if ssid['splashMethod'] == 'Password-protected with Meraki RADIUS':
            # print(network_name, ssid['ssidNumber'])
        
        # get network SSIDS
    

