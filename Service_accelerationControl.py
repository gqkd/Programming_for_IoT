import time
import threading
import requests
import json
from math import sqrt
from MyMQTT import *

class AccelerationControl(threading.Thread):
    def __init__(self, serviceID, topic, broker, port, publicURL):
        threading.Thread.__init__(self)
        self.serviceID = serviceID
        self.topic = topic
        self.broker = broker
        self.port = port
        self.payload = {
            "serviceID": self.serviceID,
            "Topic": f"{self.topic}/{self.serviceID}/accelerationControl",
            "Resource": "AccelerationControl",
            "Timestamp": None
        }
        self.client = MyMQTT(self.serviceID, self.broker, self.port, self)
        self.client.start()
        conf2 = json.load(open("settingsboxcatalog.json"))
        self.timerequestTopic = conf2["timerequestTopic"]
        self.timerequest = conf2["timerequest"]
        self.count = 2
        self.url=publicURL

    def request(self):
        self.payload["Timestamp"] = time.time()
        requests.put(self.url+"/Service", json=self.payload)

    def topicRequest(self):
        # Richiesta GET per topic
        for i in range(5):
            try:
                r = requests.get(self.url+"/GetAcceleration")
            except:
                print("!!! except -> GetAcceleration !!!")
                time.sleep(5)
        jsonBody = json.loads(r.content)
        listatopicSensor = jsonBody["topics"]
        for topic in listatopicSensor:
            self.client.mySubscribe(topic)

    def run(self):
        while True:
            self.topicRequest()
            if self.count % 2 == 0:
                self.request()
                self.count=0
            self.count += 1
            time.sleep(self.timerequestTopic)
                   
    def notify(self, topic, msg):
        payload = json.loads(msg)
        print(f"\nAcceleration Control Service received a message")
        # Estrazione dei valori di accelerazione su ogni asse
        ax = payload['e'][0]["v_xaxis"]
        ay = payload['e'][0]["v_yaxis"]
        az = payload['e'][0]["v_zaxis"]
        # Calcolo dell'accelerazione complessiva
        a_tot = sqrt(ax**2+ay**2+az**2)
        if a_tot> 0.01:
            messaggio = {'Acceleration':1, "DeviceID": payload['bn']}       # CODICE PER DIRE CHE ACCELERAZIONE NON VA BENE
        else:
            messaggio = {'Acceleration': 0, "DeviceID":payload['bn']}      # CODICE PER DIRE CHE ACCELERAZIONE VA BENE
        self.client.myPublish(f"{self.topic}/{self.serviceID}/accelerationControl", messaggio)

    def stop_MyMQTT(self):
        self.client.stop()
        print('{} has stopped'.format(self.serviceID))

