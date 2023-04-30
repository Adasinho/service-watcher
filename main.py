from enum import Enum
import argparse
import time
import os
import subprocess
import logging

LOG_FILE_NAME = "service_watcher.log"

class Service(Enum):
    MYSQL = "mysql.service"
    APACHE = "apache2.service"
    
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--service", help="choose service to action")

# Read arguments from the command line
args = parser.parse_args()

serviceParam = args.service

# logging configuration
logging.basicConfig(filename=LOG_FILE_NAME,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

def serviceIsOnline(serviceName):
    # return os.system(f'systemctl is-active --quiet {service}')
    status = subprocess.call(["systemctl", "is-active", "--quiet", serviceName])
    return True if not status else False

def restartService(serviceName):
    RESTART_ATTEMPTS = 3
    
    for _ in range(RESTART_ATTEMPTS):
        subprocess.call(["systemctl", "start", serviceName])
        
        if serviceIsOnline(serviceName):
            return True
    
    return False

def verifyService(serviceName):
    if(serviceName == Service.MYSQL.name):
        return True
    elif(serviceName == Service.APACHE.name):
        return True
    else:
        return False

def getServiceEnum(serviceName):
    return next((service for service in Service if service.name == serviceName), None)

if(verifyService(serviceParam)):
    service: Service = getServiceEnum(serviceParam)
    logging.info(f'Start application, watching service: {service.name}')
    
    while True:
        status: bool = serviceIsOnline(service.value)
        print(f'{service.name} status: {"online" if status else "offline"}')
    
        if not status:
            logging.error(f'{service.name} is offline')
        time.sleep(5.0)
else:
    logging.error(f'Service with name: {serviceParam} unsupported')