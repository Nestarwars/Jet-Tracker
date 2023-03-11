####################################################################
### LIEN AVEC LES APIs
### 24.12.2022
### Nestor Laborier
####################################################################

from opensky_api import OpenSkyApi
import requests
from requests.auth import HTTPBasicAuth
import json

import time    

class OSapi(OpenSkyApi) :
    def __init__(self):
        
        ### ADD CREDENTIALS BELOW
        super().__init__('','')
        ### ADD CREDENTIALS ABOVE

    def getCurrentPlaneState(self,icao_code) :
        """Récupère le vecteur d'états de l'avion icao_code, et tout les vecteurs en ligne si icao_code = [], au temps présent"""
        state = self.get_states(0,icao_code)
        return state

    def getTimePlaneState(self,time,icao_code) :
        """Récupère le vecteur d'états de l'avion icao_code, et tout les vecteurs en ligne si icao_code = [], au temps time"""
        state = self.get_states(time,icao_code)
        return state

    def getCurrentStates(self):
        """Récupère tous les vecteurs d'états des avions actuellement en vol"""
        states = self.get_states(0)
        return states

    def getOldState(self,icao_code,seconds):
        """Récupère le vecteur d'états de l'avion icao_code, et tout les vecteurs en ligne si icao_code = [], a seconds secondes dans le passé"""
        epoch_time = int(time.time())
        selected = epoch_time - seconds
        state = self.get_states(selected,icao_code)
        return state

class RESTapi():
    def __init__(self) :

        ### ADD CREDENTIALS BELOW
        self.user = ""
        self.code = ""
        ### ADD CREDENTIALS ABOVE

    def getCurrentRoute(self,icao):
        """Renvoie la liste des positions de l'avion en ligne, un erreur si il n'est pas en cours d'émission \n Format : [time,latitude,longitude,altitude,true_track,on_ground_flag]"""
        url = "https://opensky-network.org/api/tracks/all?icao24="+icao+"&time=0"
        auth = HTTPBasicAuth(self.user,self.code)
        answer = requests.get(url,auth)
        try :
            return answer.json()['path']
        except json.decoder.JSONDecodeError as e :
            print("Erreur d'acquisition de la route")
            return []



def initiateOpenSkyAPI() :
    """Initie l'OpenSkyAPI, avec les identifiants locaux"""
    api = OpenSkyApi('Nestarwars','170598')
    return api


# PROCEDURES DE TEST

def testLiaison():
    try :
        api = OSapi()
        states = api.getCurrentStates()
        if states != [] :
            print("\n LIAISON AVEC OPENSKY API : OK \n VECTEURS DE POSITION RECUS \n")
        else :
            print("\n LIAISON AVEC OPENSKY API : OK \n WARNING : VECTEUR DE POSITION VIDE \n")

        print("Exemple de vecteur OpenSky, premier avion recensé :\n")
        print(states.states[0])
        print("\nSes coordonées à t = 0 : \n")
        print('  '.join([str(states.states[0].latitude), str(states.states[0].longitude) ]))

    except ValueError:
        print("\n LIAISON AVEC OPENSKY API : NON CONNECTE ")

def testPasse():
        api = OSapi()
        time.sleep(11)
        print("Autre avion de test")
        print("\nSes coordonées à t = 0 : \n")
        old_state  = api.getOldState("c822af",0)
        print('  '.join([str(old_state.states[0].latitude), str(old_state.states[0].longitude) ]))

        time.sleep(11)
        print("\nSes coordonées à t = -10 in : \n")
        old_state  = api.getOldState("c822af",600000)
        print('  '.join([str(old_state.states[0].latitude), str(old_state.states[0].longitude) ]))

def testREST():
    rest = RESTapi()
    print(rest.getCurrentRoute('a77a32'))


if __name__ == "__main__" :
    testLiaison()
    print("\n \n \n")
    testREST()
