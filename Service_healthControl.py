import time
import threading
import requests
import json
from math import sqrt
from MyMQTT import *

class HealthControl(threading.Thread):
    def __init__(self, serviceID, topic, broker, port, publicURL):
        threading.Thread.__init__(self)
        self.serviceID = serviceID
        self.topic = topic
        self.broker = broker
        self.port = port
        self.client = MyMQTT(self.serviceID, self.broker, self.port, self)
        self.client.start()
        self.payload = {
            "serviceID": self.serviceID,
            "Topic": f"{self.topic}/{self.serviceID}/healthControl",
            "Resource": "HealthControl",
            "Timestamp": None
        }
        self.dizionario_misure = {}
        conf2 = json.load(open("settingsboxcatalog.json"))
        self.timerequestTopic = conf2["timerequestTopic"]
        self.timerequest = conf2["timerequest"]
        self.count = 6
        self.url = publicURL

    def request(self):
        # Sottoscrizione al boxcatalog
        self.payload["Timestamp"] = time.time()
        requests.put(self.url+"/Service", json=self.payload)

    def topicRequest(self):
        # Richiesta GET per topic del servizio
        for i in range(5):
            try:
                r = requests.get(self.url+"/GetServiceTopic")
            except:
                print("!!! except -> GetServiceTopic !!!")
                time.sleep(5)
        jsonBody = json.loads(r.content)
        listatopicService = jsonBody["topics"]
        for topic in listatopicService:
            self.client.mySubscribe(topic)

    def run(self):
        while True:
            self.topicRequest()
            if self.count % (self.timerequest/self.timerequestTopic) == 0:
                self.request()
                if self.dizionario_misure != {}:
                    self.calcolo_healthstatus()
                    self.client.myPublish(f"{self.topic}/{self.serviceID}/healthControl", self.dizionario_misure)
                self.count=0
            self.count += 1
            time.sleep(self.timerequestTopic)

    def notify(self, topic, msg):
        
        messaggio= json.loads(msg)
        listachiavi = list(messaggio.keys())
        self.deviceID = messaggio['DeviceID'][:3:]
        if self.deviceID in list(self.dizionario_misure.keys()):
            if 'Temperature' in listachiavi:
                self.dizionario_misure[f'{self.deviceID}']['Temperature']=messaggio['Temperature']
            elif 'Acceleration' in listachiavi:
                self.dizionario_misure[f'{self.deviceID}']['Acceleration'] = messaggio['Acceleration']
            elif 'Oxygen' in listachiavi:
                self.dizionario_misure[f'{self.deviceID}']['Oxygen'] = messaggio['Oxygen']
        else:
            self.dizionario_misure[f'{self.deviceID}']={}
        print(f"\nHealth Control Service received a message from {list(messaggio.keys())[0]} Service")


    def calcolo_healthstatus(self):
        lista_device = list(self.dizionario_misure.keys())
        for device in lista_device:
            lista_valori = list(self.dizionario_misure[f'{self.deviceID}'].values())
            cont=-1
            for i in lista_valori:
                cont+=1
                if i>1:
                    lista_valori.pop(cont)

            self.dizionario_misure[f'{self.deviceID}']['Health Status'] = (sum(lista_valori*100))/3
            

    def stop_MyMQTT(self):
        self.client.stop()
        print('{} has stopped'.format(self.serviceID))

