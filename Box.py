from Sensor_Temperature import *
from Sensor_Acceleration import *
from Sensor_Mass import *
from Sensor_OxygenLevel import *
from Sensor_GPS import *
from Actuator_speaker import *
from Service_temperatureControl import *
from Service_oxygenControl import *
from Service_accelerationControl import *
from Service_weightControl import *
from Service_healthControl import *
import requests
import time
import json

if __name__ == '__main__':
    conf2=json.load(open("settingsboxcatalog.json"))
    timesenddata = conf2["timesenddata"]

    conf=json.load(open("settings.json"))
    topic = conf["baseTopic"]
    broker = conf["broker"]
    port = conf["port"]

    apikey = conf["publicURL"]["publicURL_read"]
    cid = conf["publicURL"]["publicURL_channelID"]
    r = requests.get(f"https://api.thingspeak.com/channels/{cid}/fields/1.json?api_key={apikey}&results=1")

    #richiesta per il public URL del boxcatalog
    jsonBody=json.loads(r.text)
    publicURL=jsonBody['feeds'][0]['field1']
    # publicURL = 'http://127.0.0.1:8070'
    # print(publicURL, r.text, r.status_code)
    # Temperatura:
    temp1 = SensorTemperature("100", "001", topic, publicURL)
    # Accelerazione:
    acc1 = SensorAcceleration("200","001",topic, publicURL)
    # Massa:
    mass1 = SensorMass("300","001",topic, publicURL)
    # Livello di ossigenazione:
    oxy1 = SensorOxygen("400",'001',topic, publicURL)
    # Speaker
    speak1 = Speaker('500','001',broker,port, publicURL)
    # GPS
    GPS1 = SensorGPS('600','001',topic, publicURL)
    # Controllo accelerazione
    contAcc1 = AccelerationControl('01_Acc_controlService',topic,broker,port, publicURL)
    # Controllo temperatura
    contTemp1 = TemperatureControl('02_Temp_controlService', topic, broker, port, publicURL)
    # Controllo ossigeno
    contOx1 = OxygenControl('03_OX_controlService',topic,broker,port, publicURL)
    # Controllo massa
    contMas1 = WeightControl('04_We_controlService',topic,broker,port, publicURL)
    #Controllo stato di salute
    contHealth1 = HealthControl('05_Health_controlService',topic,broker,port, publicURL)


    #Connessione al broker
    temp1.start_MyMQTT(broker, port)
    acc1.start_MyMQTT(broker, port)
    mass1.start_MyMQTT(broker, port)
    oxy1.start_MyMQTT(broker, port)
    GPS1.start_MyMQTT(broker, port)

    #Sottoscrizione dei sesori al catalog e invio dei dati campionati:
    temp1.start()
    time.sleep(20)
    acc1.start()
    time.sleep(20)
    mass1.start()
    time.sleep(20)
    oxy1.start()
    time.sleep(20)
    GPS1.start()
    time.sleep(20)
    speak1.start()
    contOx1.start()
    contTemp1.start()
    contAcc1.start()
    contMas1.start()
    contHealth1.start()


   


