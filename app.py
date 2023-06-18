import os
from dotenv import load_dotenv
import requests
import json
from urllib.parse import urlencode
from datetime import datetime

load_dotenv()



BASE_URL = os.getenv('BASE_URL')
USER_NAME = os.getenv('USER_NAME')
PASSWORD = os.getenv('PASSWORD')
AUTH_SPID = os.getenv('AUTH_SPID')
SPID = os.getenv('SPID')

JWT = ""

def Auth():
    AUTH_URL = "{}{}{}".format(BASE_URL,AUTH_SPID,"/auth_check")
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    
    jsonData = {
        "IdentityProvider": "LOCAL",
        "AuthID": USER_NAME,
        "AuthCode": PASSWORD,
        "IncludeRoles": True
    }
    
    r = requests.post(AUTH_URL,data=json.dumps(jsonData),headers=headers)
    
    resp = r.json()
    JWT = resp.get("JWT")
    return JWT

def getAllServices():
    JWT = Auth()
    
    headers = {'Content-type': 'application/json', 'Accept': 'application/json','X-Auth-Token':JWT}
    params = {'SPID':SPID,"SearchOptions.PageSize":100}
    
    SERVICE_URL = "{}{}?{}".format(BASE_URL,"v4/mobile/addons",urlencode(params))
    
    
    
    r = requests.get(SERVICE_URL,headers=headers)
    resp = r.json()
    
    totalCount = resp.get("PageInfo")["TotalItemCount"]
    
    MobileAddons =  resp.get("MobileAddons")
    print("Account ID,title,first_name,last_name,full_name,email_address,mobile_number,product_name,product_activation_date")
    for Addon in MobileAddons:
        CustomerUUID = Addon.get("CustomerUUID")
        MobileUUID = Addon.get("MobileUUID")
        Service = getService(JWT,MobileUUID)
        getAllCustomers(JWT,CustomerUUID,Addon,Service)
        
    print(totalCount)
        
def getService(JWT, UUID):
    
    headers = {'Content-type': 'application/json', 'Accept': 'application/json','X-Auth-Token':JWT}
    params = {'SPID':SPID,"UUID":UUID}
    
    SERVICE_URL = "{}{}?{}".format(BASE_URL,"v4/mobile",urlencode(params))
    r = requests.get(SERVICE_URL,headers=headers)
    resp = r.json()
    
    
    
    
    return resp
    

def getAllCustomers(JWT,CustomerUUID,Addon,Service):
    
    headers = {'Content-type': 'application/json', 'Accept': 'application/json','X-Auth-Token':JWT}
    CUSTOMER_URL = "{}{}/{}{}{}".format(BASE_URL,"v2",SPID,"/customer/",CustomerUUID)
    
    r = requests.get(CUSTOMER_URL,headers=headers)
    resp = r.json()
    FirstName = resp.get("FirstName")
    LastName = resp.get("LastName")
    Email = resp.get("Email")
    
    createdDate = Addon.get("CreatedAtNanos")
    secs = createdDate / 1e9
    dt = datetime.fromtimestamp(secs)
    
    
    print("{},{},{},{},{},{},{},{},{}".format(CustomerUUID,"",FirstName,LastName,"{} {}".format(FirstName,LastName),Email,Service.get("MSISDN"),Addon.get("Name"),dt.strftime('%Y-%m-%dT%H:%M:%S.%f')))
        
getAllServices()
    