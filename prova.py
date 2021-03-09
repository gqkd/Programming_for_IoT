from MyMQTT import *
import json
import time
import requests
#CIAO AMICIIIIIII
class HR_Control():
    def __init__(self,ServiceID):
        self.ServiceID = ServiceID
        self.L=[]
        
    def startMQTT(self,broker,port):
        r=requests.get(f"http://localhost:8080/GetDevice?deviceID=HR")
        jsonBody=json.loads(r.content)
        self.topic=jsonBody["topic"]  
        self.client=MyMQTT(self.ServiceID,broker,port,self)
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop(self):
        self.client.stop()

    def notify(self,topic,msg):
        payload=json.loads(msg)
        hr=payload['e'][0]['HR']
        print(f"The HR is {hr}")
        if hr>190:
            print('!!!WARNING HIGH HR!!!')
        

if __name__=="__main__":
    conf=json.load(open("settings.json"))
    broker=conf["broker"]
    port=conf["port"]
    service=HR_Control("MicroService1234")
    service.GET()
    service.startMQTT(broker,port)
    choice = ''
    while choice!='q':
        choice=input("'q' to quit\n")

    service.stop_MyMQTT()