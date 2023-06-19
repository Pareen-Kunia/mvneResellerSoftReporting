import os
from dotenv import load_dotenv
import requests
import json
from urllib.parse import urlencode
from datetime import datetime
import logging
from logging import StreamHandler
from datadog_api_client.v2 import ApiClient, ApiException, Configuration
from datadog_api_client.v2.api import logs_api
from datadog_api_client.v2.models import *

load_dotenv()



BASE_URL = os.getenv('BASE_URL')
USER_NAME = os.getenv('USER_NAME')
PASSWORD = os.getenv('PASSWORD')
AUTH_SPID = os.getenv('AUTH_SPID')
SPID = os.getenv('SPID')
XVNE_API_KEY = os.getenv('XVNE_API_KEY')
PLAN_VALUES = []
LOG_VALUES = []

class DDHandler(StreamHandler):
    def __init__(self, configuration, service_name, ddsource):
        StreamHandler.__init__(self)
        self.configuration = configuration
        self.service_name = service_name
        self.ddsource = ddsource
 
    def emit(self, record):
        msg = self.format(record)
 
        with ApiClient(self.configuration) as api_client:
            api_instance = logs_api.LogsApi(api_client)
            body = HTTPLog(
                [
                    HTTPLogItem(
                        ddsource=self.ddsource,
                        ddtags="env:{}".format(
                            os.getenv("ENV"),
 
                        ),
                        message=msg,
                        service=self.service_name,
                    ),
                ]
            )
 
            try:
                # Send logs
                
                api_response = api_instance.submit_log(body)
                
            except ApiException as e:
                print("Exception when calling LogsApi->submit_log: %s\n" % e)

def push2Datadog(service_name,ddsource,data):
    configuration = Configuration()
    with ApiClient(configuration) as api_client:
            api_instance = logs_api.LogsApi(api_client)
            body = HTTPLog(
                [
                    HTTPLogItem(
                        ddsource=ddsource,
                        ddtags="env:{}".format(
                            os.getenv("ENV"),
 
                        ),
                        message=json.dumps(data),
                        service=service_name,
                    ),
                ]
            )
    try:
        # Send logs
        api_response = api_instance.submit_log(body)
        
    except ApiException as e:
        print("Exception when calling LogsApi->submit_log: %s\n" % e)
                                
def getAllServices():
   
    
    getAllPlans()
    
    headers = {'Content-type': 'application/json', 'Accept': 'application/json','x-api-key':XVNE_API_KEY}
    params = {'SearchOptions.PageNumber':1,"SearchOptions.PageSize":100,"SearchOptions.IndexStart":0,"SPID":SPID,"IncludeDeleted":False}
    
    
    SERVICE_URL = "{}{}?{}".format(BASE_URL,"v4/mobiles",urlencode(params))
    
    
    
    r = requests.get(SERVICE_URL,headers=headers)
    resp = r.json()
    
    totalCount = resp.get("PageInfo")["TotalItemCount"]
    _data = {
            "Total": totalCount
        }
   
    push2Datadog('xvnestpmreportingsvc','app.py',_data)
    
    Mobiles =  resp.get("Mobiles")
    print("Account ID,title,first_name,last_name,full_name,email_address,mobile_number,product_name,product_activation_date")
    for Mobile in Mobiles:
        CustomerUUID = Mobile.get("CustomerUUID")
        getAllCustomers(CustomerUUID,Mobile)
        
        
        
        
# def getAllServices(JWT):
    
#     headers = {'Content-type': 'application/json', 'Accept': 'application/json','x-api-key':JWT}
#     params = {'SearchOptions.PageNumber':1,"SearchOptions.PageSize":100,"SearchOptions.IndexStart":0,"SPID":SPID,"IncludeDeleted":False}
    
#     SERVICE_URL = "{}{}?{}".format(BASE_URL,"v4/mobile",urlencode(params))
#     r = requests.get(SERVICE_URL,headers=headers)
#     resp = r.json()
    
    
    
    
#     return resp
    
def getAllPlans():
    
    
    headers = {'Content-type': 'application/json', 'Accept': 'application/json','x-api-key':XVNE_API_KEY}
    params = {'SPID':68}
    PLANS_URL = "{}{}{}?{}".format(BASE_URL,"v4/","mobile/addon_plans",urlencode(params))
    
    
    r = requests.get(PLANS_URL,headers=headers)
    resp = r.json()
    
    MobileAddonPlans = resp.get("MobileAddonPlans")
    
    for Addon in MobileAddonPlans:
        
        PLAN_VALUES.append(Addon)
    
    
def getAllCustomers(CustomerUUID,Mobile):
    
    headers = {'Content-type': 'application/json', 'Accept': 'application/json','x-api-key':XVNE_API_KEY}
    
    CUSTOMER_URL = "{}{}/{}{}{}".format(BASE_URL,"v2",SPID,"/customer/",CustomerUUID)
    
    r = requests.get(CUSTOMER_URL,headers=headers)
    resp = r.json()
    FirstName = resp.get("FirstName")
    LastName = resp.get("LastName")
    Email = resp.get("Email")
    
    createdDate = Mobile.get("CreatedAtNanos")
    secs = createdDate / 1e9
    dt = datetime.fromtimestamp(secs)
    
    plan = ""
    
    if Mobile.get('Addons') is not None:
        #print(Mobile.get('Addons')[0])
        for item in PLAN_VALUES:
            if item['ProductAvailabilityUUID'] == Mobile.get('Addons')[0]['AddonAvailabilityUUID']:
                plan = item.get('Name')
                
                push2Datadog('xvnestpmreportingsvc','app.py',{"stpmPlanName":plan,"stpmPlanCount":1,"stpmPlanTimeStamp":dt.strftime('%Y-%m-%dT%H:%M:%S.%f')})
                print("{},{},{},{},{},{},{},{},{}".format(CustomerUUID,"",FirstName,LastName,"{} {}".format(FirstName,LastName),Email,Mobile.get("MSISDN"),plan,dt.strftime('%Y-%m-%dT%H:%M:%S.%f')))
        
        




getAllServices()
    