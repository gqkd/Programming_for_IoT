import numpy as np
import json
import time
import random
import threading
import requests
from MyMQTT import *

#TODO: i sensori devono essere a se stanti e registrarsi alla scatola 

class SensorTemperature(threading.Thread):
    def __init__(self, deviceID, boxID, topic):
        threading.Thread.__init__(self)
        self.deviceID = boxID+deviceID # ID deve essere numerico 
        self.boxID = boxID
        self.topic = topic # self.topic= "Ipfsod"
        self.payload = {
            "deviceID": self.deviceID,
            "Topic": self.topic+"/"+ self.boxID +"/"+self.deviceID+"/temperature",
            "Resource": 'Temperature',
            "Timestamp": None
        }
        conf2=json.load(open("settingsboxcatalog.json"))
        self.timerequest=conf2["timerequest"]
        self.count = 6
            # "actuator": [
            #     {
            #     "Topic": self.topic+"/"+self.boxID+"/speaker",
            #     "Resource": 'Speaker',
            #     "Timestamp": None
            #     }

        
    def request(self):
        self.payload["Timestamp"] = time.time()
        r = requests.put(f"https://boxcatalog.loca.lt/Device", json=self.payload)
        print(r)
    
    def run(self):
        print("1:publishing data")
        
        self.sendData()
        if self.count % self.timerequest == 0: 
            self.request()
            self.count=0
        self.count += 1
        print("2:run finished")

    def sendData(self):
        
        t = 100 #TODO simulazione output sensore 
        message = self.__message
        message['e'][0]['t'] = float(time.time())
        message['e'][0]['v'] = t
        self.client.myPublish(self.topic,message)   
        

           
    def start_MyMQTT(self, broker, port):
        self.client = MyMQTT(self.deviceID, broker, port, None)
        self.__message={
            "bn": self.deviceID,
            "e": [
                    {
                        "n": "temperature",
                        "u": "Cel",
                        "t": None,
                        "v": ""
                    }
                ]
            }
        self.client.start()
    
     
    def stop_MyMQTT(self):
        self.client.stop()
        