import sys
import requests, json, time
from apscheduler.schedulers.blocking import BlockingScheduler as scheduler
import subprocess

################# Get Access & Refresh Tokens #########################
def get_tokens(apiKey):      

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = 'grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey='+apiKey

    response = requests.post('https://iam.cloud.ibm.com/identity/token', headers=headers, data=data, auth=('bx', 'bx'))

    API_Data = response.json()

    return API_Data


############################ Create Cart ##############################
def create_cart(access_token,refresh_token):
    # # Header
    headers = { 'Authorization': 'Bearer '+access_token, 'X-Feature-Agents': 'True', 'refresh_token':refresh_token}

    # # Posting data
    url = 'https://eu-de.schematics.cloud.ibm.com/v2/cart'
    payload = {
        "name": "cart-9",
        "cart_order_data": [
            {
                "name": "agent_id",
                "value": "s9-02-11-2023.deA.1390",
                "type": "string"
            },
            {
                "name": "agent_name",
                "value": "s9-02-11-2023",
                "type": "string"
            }
        ],
        "cart_items": [
            {
                "name": "cart-install-23-10-2023",
                "operation": "install",
                "catalog_id": "e42da918-6b6a-4171-b9d9-c78199b420c4",
                "offering_id": "f28d81c6-d9c7-438d-9ba5-68f64b6f0103",
                "owning_account": "fcdb764102154c7ea8e1b79d3a64afe0",
                "offering_target_kind": "terraform",
                "offering_version_id": "d7f454d8-ac93-4680-aa45-137f89ca9a9c",
                "offering_kind": "terraform",
                "offering_fulfilment_kind": "terraform"
            }
        ],
        "service_name": "globalcatalog-collection",
        "resource_group": "19e34037c9fe41e5aa9d682c9089b044",
        "location": "eu-de"
    }
    try:
        response = requests.post(url, json=payload, headers = headers)
        api_response = response.json()
        #print(api_response)
        return api_response
    except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as err:
        print("Error while trying to GET data")
        print(err)
    finally:
        response.close()


############################### Poll for Cart Status ####################################
def poll_cart_status(cart_id):
    response = get_tokens(sys.argv[1])
    access_token = response['access_token']
    #print("***** Inside poll_cart_status *******")
    #auth_token = access_token
    url = 'https://eu-de.schematics.cloud.ibm.com/v2/cart/'+cart_id
    
    # # Header
    headers = { 'Authorization': 'Bearer '+access_token, 'X-Feature-Agents': 'True'}

    # # Posting data
    try:
        request = requests.get(url, headers = headers)
    except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as err:
        print("Error while trying to GET data")
        print(err)
    finally:
        request.close()

    jsonResponse = request.json()
    #print("******* Workspace ID *******")
    ws_id = jsonResponse['cart_items'][0]['itemSKU']['sku_id']
    #print(ws_id)

    ########################## Start : Get Workspace status #########################
    ws_url = 'https://eu-de.schematics.cloud.ibm.com/v1/workspaces/'+ws_id
    # # Header
    ws_headers = { 'Authorization': 'Bearer '+access_token}
    # # Posting data
    try:
        ws_response = requests.get(ws_url, headers = ws_headers)
    except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as err:
        print("Error while trying to GET ws data")
        print(err)
    finally:
        ws_response.close()
    
    ws_jsonResponse = ws_response.json()
    print("****** WS Status *******")
    print(ws_jsonResponse['status'])

    ########################## End : Get Workspace status #########################


    for key, value in jsonResponse.items():
        if key == 'user_state':
            ts = time.time()
            print('******* Cart Status ******')
            print('Current Timestamp',ts)
            print(key, ":", value)

    #return request.content

if __name__ == '__main__':
    #usage: python3 periodic_get_api.py <API_KEY>

    # STEP-1: Get Access & Refresh tokens
    response = get_tokens(sys.argv[1])
    access_token = response['access_token']
    refresh_token = response['refresh_token']

    #print(response['access_token'])

    # STEP-2: Create Cart
    cart_response = create_cart(access_token,refresh_token)

    cart_id = cart_response['_id']
    #print("Cart ID: ",cart_id)

    # STEP-3: Poll for cart status using cart id
    sched = scheduler()
    print(time.time())
    sched.add_job(poll_cart_status, 'interval', seconds=5, args=[cart_id])
    sched.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while true:
            pass
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()