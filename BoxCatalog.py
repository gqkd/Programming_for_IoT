import cherrypy
import json
import datetime
import time
import os
import requests
import threading

class Catalog():
    exposed=True
    def __init__(self):
        self.catalog = {
            "projectOwner": "Bonfanti_Pedroncelli_Quaglia_Zanchi", 
            "projectName": "IoT platform for smart organs delivery", 
            "lastUpdate": str(datetime.time()), 
            "deviceList": [],
            "servicesList": []
        }
        self.deviceList = self.catalog["deviceList"]
        self.servicesList = self.catalog["servicesList"]
        self.timestart = time.time()
        
    def PUT(self,*uri):
        timenow = time.time()
        print(f"_____________{timenow-self.timestart}__________________")
        
        body=cherrypy.request.body.read()
        jsonBody=json.loads(body)
        if uri[0] == "Device":
            cont = -1
            for box in self.deviceList:
                cont += 1
                if str(box["deviceID"]) == str(jsonBody["deviceID"]):
                    self.deviceList.pop(cont)
            self.deviceList.append(jsonBody)
            self.catalog["deviceList"] = self.deviceList
            return json.dumps(self.deviceList)

        elif uri[0] == "Service":
            cont = -1
            for service in self.servicesList:
                cont += 1
                if str(service["serviceID"]) == str(jsonBody["serviceID"]):
                    self.servicesList.pop(cont)
            self.servicesList.append(jsonBody)
            self.catalog["servicesList"] = self.servicesList
            return json.dumps(self.servicesList)
        
        elif uri[0] == "UserData":
            # dizionario degli utenti iscritti alla WebApp
            self.userData = jsonBody

        elif uri[0] == "Info":
            self.info = jsonBody

        self.catalog["lastUpdate"] = str(datetime.time())

        
    def GET(self,*uri):
        
        timenow = time.time()
        print(f"_____________{timenow - self.timestart}__________________")
        
        if len(uri)!=0:
            if uri[0] == "GetTemperature":
                d = {}
                topics = []
                for device in self.deviceList:
                    if device["Resource"] == "Temperature":
                        topics.append(device["Topic"])
                d["topics"] = topics
                return json.dumps(d)
            
            elif uri[0] == "GetAcceleration":
                topics = []
                for device in self.deviceList:
                    if device["Resource"] == "Acceleration":
                        topics.append(device["Topic"])
                return json.dumps({"topics": topics})
            
            elif uri[0] == "GetMass":
                topics = []
                for device in self.deviceList:
                    if device["Resource"] == "Mass":
                        topics.append(device["Topic"])
                return json.dumps({"topics": topics})
            
            elif uri[0] == "GetOxygenLevel":
                topics = []
                for device in self.deviceList:
                    if device["Resource"] == "Oxygen":
                        topics.append(device["Topic"])
                return json.dumps({"topics": topics})
            
            elif uri[0] == "GetGPS":
                topics = []
                for device in self.deviceList:
                    if device["Resource"] == "GPS":
                        topics.append(device["Topic"])
                return json.dumps({"topics": topics})
            
            elif uri[0] == "GetServiceTopic":
                topics = []
                for service in self.servicesList:
                    if service["Resource"] == "AccelerationControl" or service["Resource"] == "TemperatureControl" or service["Resource"] == "OxygenControl" or service["Resource"] == "WeightControl":
                        topics.append(service["Topic"])
                return json.dumps({"topics": topics})
                        
            elif uri[0] == "GetTelegram":
                for service in self.servicesList:
                    if service["Resource"] == "TelegramBot":
                        TgTopic = service["Topic"]
                        return json.dumps({"topics": TgTopic})
                    
            elif uri[0] == "GetUserData":
                return json.dumps(self.userData)

            elif uri[0] == "Get_Info":
                return json.dumps(self.info)

            elif uri[0] == "Get_TSadaptor":
                return json.dumps({"devices":self.deviceList, "services":self.servicesList})


class cherry:
    def __init__(self):
        
        conf={
        '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                'tool.session.on':True
        }
        }
        cherrypy.config.update({'server.socket_port': 8070})
        cherrypy.tree.mount(Catalog(),'/',conf)
        cherrypy.engine.start()
        

class ngrok:
    def __init__(self):
        time.sleep(5)
        os.system('ngrok http 8070')

class tunneling:
    def __init__(self):
        time.sleep(10)
        r = requests.get('http://localhost:4040/api/tunnels')
        jsonBody=json.loads(r.text)
        publicURL=jsonBody["tunnels"][0]["public_url"]
        print(publicURL)
        conf=json.load(open("settings.json"))
        apikey = conf["publicURL"]["publicURL_write"]
        r1 = requests.get(f"https://api.thingspeak.com/update?api_key={apikey}&field1="+publicURL)
        print(r1.text)

if __name__=="__main__":
    t1 = threading.Thread(target=cherry)
    t2 = threading.Thread(target=ngrok)
    t3 = threading.Thread(target=tunneling)

    t1.start()
    t2.start()
    t3.start()


    


    
    
