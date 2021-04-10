import threading
import requests
import time
from MyMQTT import *


class Speaker(threading.Thread):
    def __init__(self, speakerID, boxID, broker, port, publicURL):
        threading.Thread.__init__(self)
        self.speakerID = f"{boxID}{speakerID}"  # ID deve essere numerico
        self.boxID = boxID
        self.broker = broker
        self.port = port
        self.payload = {
            "deviceID": self.speakerID,
            "Resource": "Speaker",
            "Timestamp": None
        }
        self.client = MyMQTT(self.speakerID, self.broker, self.port, self)
        self.client.start()
        self.d = {'Temperature': [0,"ON"], 'Acceleration': [0,"ON"], 'Oxygen': [0,"ON"], 'Mass': 1} # la seconda chiave è per le notifhce 
        # Dati utili per timing
        conf2 = json.load(open("settingsboxcatalog.json"))
        self.timerequestTopic = conf2["timerequestTopic"]
        self.timerequest = conf2["timerequest"]
        self.count = 6
        self.url = publicURL

    def request(self):
        # Sottoscrizione al boxcatalog
        self.payload["Timestamp"] = time.time()
        requests.put(self.url+"/Device", json=self.payload)  # Sottoscrizione al Catalog

    def topicRequest(self):
        # Richiesta GET per topic del servizio
        try:
            r = requests.get(self.url+"/GetServiceTopic")
            jsonBody = json.loads(r.content)
        except:
            print("...............attivato except...............")
            time.sleep(5)
            r = requests.get(self.url + "/GetServiceTopic")
            jsonBody = json.loads(r.content)
        
        listatopicService = jsonBody["topics"]
        # Una volta ottenuto il topic, subscriber si sottoscrive a questo topic per ricevere dati
        #self.client = MyMQTT(self.speakerID, self.broker, self.port, self)
        #self.client.stop()
        #self.client.start()
        for topic in listatopicService:
            self.client.mySubscribe(topic)  # TOPIC RICHIESTO A CATALOG
        try:
            r = requests.get(self.url+"/GetTelegram")
            jsonBody = json.loads(r.content)
        except :
            print("...............attivato except...............")
        
        self.telegramTopic = jsonBody["topics"]
        self.client.mySubscribe(self.telegramTopic)
        
    def run(self):
        while True:
            self.topicRequest()
            if self.count % (self.timerequest/self.timerequestTopic) == 0:
                self.request()
                self.count=0
            self.count += 1
            time.sleep(self.timerequestTopic)

    def notify(self, topic, msg):
        print(f"&&&&&&&&&&&&&&&&&&&&&&&&&ATTUATORE{topic}")
        if topic == self.telegramTopic:
            messaggio = json.loads(msg)
            if messaggio['DeviceID'] == self.boxID:
                listaKeys = list(messaggio.keys())
                toSilence = listaKeys[0] # Parametro da disattivare o attivare
                toSilence_state = messaggio[toSilence] # se attivare le notifche o disattivarle
                self.d[toSilence][1] = toSilence_state

        else:
            messaggio = json.loads(msg)
            listachiavi = list(messaggio.keys())
            deviceID = messaggio['DeviceID']
            if self.boxID == deviceID[0:3]:
                print(f"""MESSAGGIO RICEVUTO DA ATTUATOREEEEEEEEE:\n {messaggio}""")
                if 'Mass' in listachiavi:
                    self.d['Mass'] = messaggio['Mass']
                elif 'Temperature' in listachiavi:
                    self.d['Temperature'][0] = messaggio['Temperature']
                elif 'Acceleration' in listachiavi:
                    self.d['Acceleration'][0] = messaggio['Acceleration']
                elif 'Oxygen' in listachiavi:
                    self.d['Oxygen'][0] = messaggio['Oxygen']
            print(f"Allarmi: {self.d}")
            if self.d["Mass"]==0 and ((self.d['Temperature'][0]==1 and self.d['Temperature'][1]=="ON")  or (self.d['Acceleration'][0]==1 and self.d['Acceleration'][1]=="ON") or (self.d['Oxygen'][0]==1 and self.d['Oxygen'][1]=="ON")): # abbiamo aggiunto self.d["Mass"] == 0 in modo che quando la massa non è presente (1) non continua a dare allarme 
                print('A T T E N Z I O N E: \n ALLARME ATTIVO')


    def stop_MyMQTT(self):
        self.client.stop()
