####################################################################
### MOTEUR
### 25.12.2022
### Nestor Laborier
####################################################################


import numpy as np

# Module geopy pour la gestion des coordonnées en norme WGS 84
from geopy import distance

# Module de lien avec l'API OpenSky, en mode Python ou en mode REST
from link import *

# Module de construction de la base de données pour une mise à jour possible des modèles de jets et des immatriculations
from buildDB import *


### DEFINITION DE LA CLASSE POSITION

class Position : 
    """Classe des positions, en latitude/longitude, selon la norme WGS84"""
    
    def __init__(self,lat=0,long=0):
        self.lat   = lat
        self.long  = long

    def __repr__(self):
        return f"(latitude={self.lat:3} ; longitude={self.long:3})"

    def __add__(self,p):
        return Position(self.lat + p.lat, self.long + p.long)

    def __sub__(self,p):
        return Position(self.lat - p.lat, self.long - p.long)

    def __eq__(self, p):
        if self.lat == p.lat and self.long == p.long:
            return True
        return False

    def sign(self):
        return Position(np.sign(self.lat), np.sign(self.long))

    def dist(self,p):
        """ Calcule la distance entre ce point et un autre, selon la norme WGS84 """
        return round(distance.distance((self.lat,self.long),(p.lat,p.long)).km * 100)/100

### DEFINITION DE LA CLASSE DES AVIONS

class Plane :
    """Classe d'un avion, définie par son ICAO, sa position, son modèle, son immatriculation ID, et son pays d'origine"""
    
    def __init__(self, icao="unknown", model="unknown", country="unknown", ID="unknown", pos=Position(0,0)):
        self.icao   = icao
        self.pos    = pos
        self.model  = model
        self.ID     = ID
        self.country= country

    def __repr__(self) :
        return ' | '.join([self.icao,f"{self.model:<40}",f"{self.country:<20}",f"{self.ID:<8}", f"{str(self.pos.lat):<7}", str(self.pos.long)])

    def findRouteLinear(self,inter) :
        """
        LEGACY : Trouve la route suivie par l'avion décomposée par intervalle, de manière itérative
        Limitations : Les requetes OpenSkyAPI ne peuvent être effectuées que toutes les 10 secondes min
        """
        
        currentTime = time.time()
        r = Route(self.icao)

        api = OSapi()
        state = api.getOldState(self.icao,0)
        k = 1

        while state != None :
            # print(state)
            if state.states != [] :
                pos = Position(state.states[0].latitude,state.states[0].longitude)
                r.addPos(pos)
            time.sleep(11)
            state = api.getOldState(self.icao,k*(inter+11))
            k+=1

        return r

    def findRouteREST(self):
        """Récupère la route courante suivie par l'avion actif, par une requete REST, directe et plus rapide"""
        rest = RESTapi()
        raw_route = rest.getCurrentRoute(self.icao)
        route = Route(self.icao)
        for p in raw_route : 
            route.addPos(Position(p[1],p[2]))
        return route


    def findOrigin(self) : 
        """DEPRECATED : Trouve la position de départ de l'avion actif par dichotomie
        en considérant un trajet de maximum 18h, il nous faut une profondeur récursive de 16, 
        soit ~16*10 = 2min40sec pour un requete à la seconde près"""
        pass


### DEFINITION DE LA CLASSE DES ROUTES

class Route():
    """Classe des routes, liée à un ICAO particulier, contient une liste de positions à la norme WGS-84, et la longueur totale du trajet mise à jour à chaque ajout de position"""
    
    def __init__ (self, icao="", pos_list=[]) :
        self.length = 0
        self.pos_list = pos_list
        self.icao = icao
    
    def __repr__(self) :
        header = "Route de l'avion ICAO : " + self.icao + "\n"
        history =  "\n"
        for p in self.pos_list :
            history += p.__repr__() +"\n"
        footer = "\n Longueur totale du trajet : " + str(self.length)
        return header+history+footer

    def addPos(self,pos):
        """Ajoute une position à la route active, et met à jour la distance parcourue"""
        if self.pos_list != [] :
            k = -1
            # On contrôle que la dernière position est ok, sinon on recule jusqu'a en trouver une bonne
            while (self.pos_list[k].lat == None) or (self.pos_list[k].long == None) :
                k -= 1
            self.length += self.pos_list[k].dist(pos)
        self.pos_list.append(pos)

    def findRouteREST(self,plane):
        """Met à jour la route actuelle avec celle de l'avion choisi, en un appel à l'API REST"""
        rest = RESTapi()
        raw_route = rest.getCurrentRoute(plane.icao)
        self.icao = plane.icao
        self.pos_list = []
        for p in raw_route : 
            self.addPos(Position(p[1],p[2]))

    def unpack_coord(self):
        """Renvoie les listes des latitudes et longitudes de la route active (pour l'affichage)"""
        rlt,rlg = [],[]
        for p in self.pos_list :
            rlt.append(p.lat)
            rlg.append(p.long)
        return rlt,rlg
        

    
### CLASSE DE LA LISTE DES JETS PRIVES EN VOLS ACTUELLEMENT

class FlyingPlanes :
    """Classe des avions en vols, regroupe la liste de tous les avions actuellement en vol répertoriés par l'API OpenSky"""
    
    def __init__ (self) :
        api = OSapi()
        states_list = api.getCurrentStates()
        states_list = states_list.states
        jets_list = PrivateJets()

        self.flying = []
        self.positions = dict()
    
        for state in states_list :
            if state.icao24 in jets_list.jets :
                model = jets_list.jets[state.icao24][0] + ' ' + jets_list.jets[state.icao24][2]
                ID = state.callsign
                country = state.origin_country
                self.flying.append(Plane(state.icao24,model,country,ID,Position(state.latitude,state.longitude)))
                self.positions[state.icao24] = Position(state.latitude,state.longitude)

    def __repr__(self):
        output = ''
        for plane in self.flying :
            output += str(plane) + '\n'
        return output

    def coordinates(self):
        """Renvoie les coordonnées des avions en vols répertoriés"""
        coord = []
        for plane in self.flying :
            coord.append(plane.pos)
        return coord
    
    def select_plane(self,icao) :
        """Renvoie l'avion sélectionné à l'aide d'un code icao, avec ses informations actuelles si elles sont présentes"""
        for plane in self.flying :
            # print(plane)
            if plane.icao == icao :
                return plane
        return Plane(icao)
          

def convert_CO2(km):
    return 4.9 * km


### PROTOCOLE DE TEST

def TestListesAvions() :
    """Teste la récupération de la base de données des modèles de jets privés, et la connexion avec l'OpenSkyAPI pour la récupération des vecteur d'états"""

    print("Liste des jets privés recensés :")
    planes = PrivateJets()
    print(planes)

    jets = FlyingPlanes()
    print("\n Liste des jets privés en vols actuellement : \n")
    print(" ICAO  | Marque et modèle                         | Pays d'origine       | Immat    | Position actuelle")
    print("-------------------------------------------------------------------------------------------------------")
    print(jets)
    print("-------------------------------------------------------------------------------------------------------")
    print(" ICAO  | Marque et modèle                         | Pays d'origine       | Immat    | Position actuelle")
    print("\n Nombre de jets privés en vol actuellement : " +   str(len(jets.flying)))

    print(jets.select_plane("4b1804"))


def TestRoutePositions():
    """Teste l'implantation des classe Route() et Position() et leur méthodes"""
    p1 = Position(1,0)
    p2 = Position(2,0)
    p3 = Position(3,0)
    r = Route("XXX")
    r.addPos(p1)
    r.addPos(p2)
    r.addPos(p3)
    print(r)

def testFindRoute():
    """Teste la récupération automatique des routes par l'API REST en sélectionnant aléatoirement un avion"""
    states = FlyingPlanes()
    n = np.random.randint(0,100)
    plane = states.flying[n]
    print(plane)
    
    p = Position(1.5,2.5)
    print(p)
    
    r = plane.findRouteREST()
    print(r)

if __name__ == '__main__' :
    TestListesAvions()
    testFindRoute()