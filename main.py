from enum import Enum
import argparse
import time
import os
import subprocess
import logging

LOG_FILE_NAME = "service_watcher.log"
ATTEMPTS_TO_RESTART = 3

class LogLevel(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2

class ServiceType(Enum):
    MYSQL = "mysql.service"
    APACHE = "apache2.service"
    
class Service:
    def __init__(self, serviceName):
        self.serviceName = serviceName
        self.serviceType = self.getServiceEnum()
        self.restartCounter = 0
        self.lastMessage = None
        
    def getServiceEnum(self):
        return next((service for service in ServiceType if service.name == self.serviceName), None)
    
    def serviceIsOnline(self):
        # return os.system(f'systemctl is-active --quiet {service}')
        status = subprocess.call(["systemctl", "is-active", "--quiet", self.serviceType.value])
        return True if not status else False
    
    def restartService(self):
        if(self.restartCounter == 0):
            logging.info(f'Trying restart process: {self.serviceType.value}')

        if(self.restartCounter < ATTEMPTS_TO_RESTART):
            subprocess.call(["systemctl", "start", self.serviceType.value])
            
            if self.serviceIsOnline():
                self.restartCounter = 0
                return True
        elif(self.restartCounter == ATTEMPTS_TO_RESTART):
            logging.warning(f'Can\'t restart process: {self.serviceType.value}')
        
        self.restartCounter += 1
        return False
    
    def logStatus(self, logLevel: LogLevel, message: str):
        if self.lastMessage != message:
            self.lastMessage = message
            if logLevel == LogLevel.INFO:
                logging.info(message)
            elif logLevel == LogLevel.WARNING:
                logging.warning(message)
            elif logLevel == LogLevel.ERROR:
                logging.error(message)
    
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

restartCounter = 0

def verifyService(serviceName: str):
    if(serviceName == ServiceType.MYSQL.name):
        return True
    elif(serviceName == ServiceType.APACHE.name):
        return True
    else:
        return False

if(verifyService(serviceParam)):
    service: Service = Service(serviceParam)
    logging.info(f'Start application, watching service: {service.serviceType.name}')
    
    while True:
        status: bool = service.serviceIsOnline()
        print(f'{service.serviceType.name} status: {"online" if status else "offline"}')
    
        if not status:
            service.logStatus(LogLevel.ERROR, f'{service.serviceType.name} is offline')
            service.restartService()
        time.sleep(5.0)
else:
    logging.error(f'Service with name: {serviceParam} unsupported')