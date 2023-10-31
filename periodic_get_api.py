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
                "value": "s9-test2.deA.9627",
                "type": "string"
            },
            {
                "name": "agent_name",
                "value": "s9-test2",
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
        print(api_response)
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
    print("***** Inside poll_cart_status *******")
    #auth_token = access_token
    url = 'https://eu-de.schematics.cloud.ibm.com/v2/cart/'+cart_id
    #url = sys.argv[1]
    #auth_token = sys.argv[2]
    #auth_token = "eyJraWQiOiIyMDIzMDkwODA4MzQiLCJhbGciOiJSUzI1NiJ9.eyJpYW1faWQiOiJJQk1pZC01NTAwMDQ4WVFYIiwiaWQiOiJJQk1pZC01NTAwMDQ4WVFYIiwicmVhbG1pZCI6IklCTWlkIiwianRpIjoiZGEyYTFlMzYtYjEwMC00ZTczLTgzOGEtYWQ4MzVjOTdkNjY3IiwiaWRlbnRpZmllciI6IjU1MDAwNDhZUVgiLCJnaXZlbl9uYW1lIjoiVW1hciBBbGkiLCJmYW1pbHlfbmFtZSI6Ik5hZ29vciBTYWhlYiBTaGFpayIsIm5hbWUiOiJVbWFyIEFsaSBOYWdvb3IgU2FoZWIgU2hhaWsiLCJlbWFpbCI6InVtYXJhbGkubmFnb29yQGluLmlibS5jb20iLCJzdWIiOiJ1bWFyYWxpLm5hZ29vckBpbi5pYm0uY29tIiwiYXV0aG4iOnsic3ViIjoidW1hcmFsaS5uYWdvb3JAaW4uaWJtLmNvbSIsImlhbV9pZCI6IklCTWlkLTU1MDAwNDhZUVgiLCJuYW1lIjoiVW1hciBBbGkgTmFnb29yIFNhaGViIFNoYWlrIiwiZ2l2ZW5fbmFtZSI6IlVtYXIgQWxpIiwiZmFtaWx5X25hbWUiOiJOYWdvb3IgU2FoZWIgU2hhaWsiLCJlbWFpbCI6InVtYXJhbGkubmFnb29yQGluLmlibS5jb20ifSwiYWNjb3VudCI6eyJ2YWxpZCI6dHJ1ZSwiYnNzIjoiZmNkYjc2NDEwMjE1NGM3ZWE4ZTFiNzlkM2E2NGFmZTAiLCJpbXNfdXNlcl9pZCI6Ijc3ODk3NDYiLCJmcm96ZW4iOnRydWUsImltcyI6IjE5ODI5MTIifSwiaWF0IjoxNjk2ODM3MTM1LCJleHAiOjE2OTY4NDA3MzUsImlzcyI6Imh0dHBzOi8vaWFtLmNsb3VkLmlibS5jb20vaWRlbnRpdHkiLCJncmFudF90eXBlIjoidXJuOmlibTpwYXJhbXM6b2F1dGg6Z3JhbnQtdHlwZTphcGlrZXkiLCJzY29wZSI6ImlibSBvcGVuaWQiLCJjbGllbnRfaWQiOiJieCIsImFjciI6NCwiYW1yIjpbIm1mYSIsInB3ZCIsImh3ayJdfQ.JWO2jyK_GrgJHyCCALcInpMzog6Ik4YvxBJFmZnWuCCdlEzJmFcgJOnb3qMZcsiaeE5bWhIROZFxTUVFTfwsQHxMwcbzyu4C400k_m4vbTBHlAFCg-7j_smr7WTvLXpLnJyOiwAKSmYFock8bmPrTIjfDTyEzfyWAYjD-5pVDFuwX3fsPJge86Dc4V_5k5StEI96ViYrZyJWY9IM94CE-tEIsjppmDcXQN3J-HmWFr1y72wlgMSvMYG2V5fvFwS7HdjHzUaRNPX7JNMq4FnsXD1cA5oQ7Vh9ZJYTxUs34atl00DVli8c_qpOTNE0f7wtFVLFAtCjcR75hd5QViDJMA"

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
    # #print(request.json().user_state.state)

    for key, value in jsonResponse.items():
        if key == 'user_state':
            ts = time.time()
            print('Current Timestamp',ts)
            print(key, ":", value)

    #return request.content

if __name__ == '__main__':
    #usage: python3 periodic_get_api.py <API_KEY>

    # STEP-1: Get Access & Refresh tokens
    response = get_tokens(sys.argv[1])
    access_token = response['access_token']
    refresh_token = response['refresh_token']

    print(response['access_token'])

    # STEP-2: Create Cart
    cart_response = create_cart(access_token,refresh_token)

    cart_id = cart_response['_id']
    print("Cart ID: ",cart_id)

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