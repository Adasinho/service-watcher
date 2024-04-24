from enum import Enum
import argparse
import time
import os
import subprocess
import logging
import discord

LOG_FILE_NAME = "service_watcher.log"
ATTEMPTS_TO_RESTART = 3
TOKEN = "https://discord.com/api/webhooks/1103788473426649109/OaKdqmp1vVPP-_HKJ5M7f2EIArHg5HMei5k5h703V7C6U-DnOtFD2HHoQZ9sSowkoz5V"
BOT_NAME = "Service Watcher"

class ServiceStatus(Enum):
    ONLINE = 0
    OFFLINE = 1
    UNKNOWN = 999

class LogLevel(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2

class ServiceType(Enum):
    MYSQL = "mysql.service"
    APACHE = "apache2.service"
    NGINX = "nginx.service"
    
class Service:
    def __init__(self, serviceName):
        self.serviceName = serviceName
        self.serviceType = self.getServiceEnum()
        self.restartCounter = 0
        self.lastMessage = None
        self.prevStatus = ServiceStatus.UNKNOWN
        self.status = ServiceStatus.UNKNOWN
        self.discord = discord.Discord(TOKEN, BOT_NAME)
        
    def setStatus(self, newStatus):
        #if self.status != newStatus:
        self.prevStatus = self.status
        self.status = newStatus
    
    def getServiceEnum(self):
        return next((service for service in ServiceType if service.name == self.serviceName), None)
    
    def serviceIsOnline(self):
        # return os.system(f'systemctl is-active --quiet {service}')
        status = subprocess.call(["systemctl", "is-active", "--quiet", self.serviceType.value])
        ret = True if not status else False
        newStatus = ServiceStatus.ONLINE if ret else ServiceStatus.OFFLINE
        self.setStatus(newStatus)
        
        return ret
    
    def restartService(self):
        if(self.restartCounter == 0):
            logging.info(f'Trying restart process: {self.serviceType.value}')

        if(self.restartCounter < ATTEMPTS_TO_RESTART):
            subprocess.call(["systemctl", "start", self.serviceType.value])
            
            if self.serviceIsOnline():
                self.restartCounter = 0
                logging.info(f'Restart process: {self.serviceType.value} success')
                return True
        elif(self.restartCounter == ATTEMPTS_TO_RESTART):
            logging.error(f'Can\'t restart process: {self.serviceType.value}')
            
            # send info about dead process
            title = f'{self.serviceType.name} status'
            description = "Offline"
            self.discord.sendMessage(title, description)
        
        self.restartCounter += 1
        return False
    
    def logStatus(self):
        if self.status == ServiceStatus.OFFLINE and self.prevStatus == ServiceStatus.ONLINE:
            logging.error(f'{self.serviceType.name} is offline')
        elif self.status == ServiceStatus.ONLINE and self.prevStatus == ServiceStatus.OFFLINE:
            logging.info(f'{self.serviceType.name} is online')
            
    
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--service", help="choose service to action")

# Read arguments from the command line
args = parser.parse_args()

serviceParam = args.service

# logging configuration
logging.basicConfig(filename=LOG_FILE_NAME,
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

restartCounter = 0

def verifyService(serviceName: str):
    if(serviceName == ServiceType.MYSQL.name):
        return True
    elif(serviceName == ServiceType.APACHE.name):
        return True
    elif(serviceName == ServiceType.NGINX.name):
        return True
    else:
        return False

if(verifyService(serviceParam)):
    service: Service = Service(serviceParam)
    logging.info(f'Start application, watching service: {service.serviceType.name}')
    
    while True:
        status: bool = service.serviceIsOnline()
        print(f'{service.serviceType.name} status: {"online" if status else "offline"}')
    
        service.logStatus()
        
        if not status:
            service.restartService()
        time.sleep(5.0)
else:
    logging.error(f'Service with name: {serviceParam} unsupported')