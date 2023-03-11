####################################################################
### CONTROLEUR
### 25.12.2022
### Nestor Laborier
####################################################################

### Module moteur
from engine import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

### CLASSES

class ControlerBase:
    def __init__(self):
        self.clients = list()
        self.message = ""

    def addClient(self, client):
        self.clients.append(client)

    def refreshAll(self, message):
        self.message = message
        for client in self.clients:
            client.refresh()


class Controler(ControlerBase):
    def __init__(self):
        super().__init__()

        self.flying_planes = FlyingPlanes()
        self.coord_list = self.flying_planes.coordinates()
        self.plane_list = self.flying_planes.flying
        self.positions = self.flying_planes.positions
        self.route_coord = ([],[])
        self.refresh_planes_flag = False
        self.route_length = 0 
        self.co2 = 0

    def prep_plot_planes(self) :
        """Récupère les coordonnées de tous les avions à afficher en lat,long norme WGS 84"""
        x = []
        y = []
        for pos in self.coord_list :
            y.append(pos.lat)
            x.append(pos.long)
        self.plane_coord_list = (x,y)

    def select_plane(self,icao):
        """Récupère les coordonnées d'un avion icao à afficher en lat,long norme WGS 84"""
        self.plane_coord_list = (self.positions[icao].long,self.positions[icao].lat)

        ### DEPRECATED 
        # selected = Plane("000000","ERROR","ID",Position(0,0))
        # for plane in self.flying_planes.flying :
        #     print(plane)
        #     if plane.icao == icao :
        #         selected = plane
        # self.plane_coord_list = (selected.pos.lat,selected.pos.long)

    def compute_route(self,icao): 
        """Calcule la route correspondant à l'avion icao, et stocke les positions succesives et la longueur de la route"""   
        plane = self.flying_planes.select_plane(icao)
        route = Route()
        route.findRouteREST(plane)
        self.route_coord = route.unpack_coord()
        self.route_length = route.length

    def refresh_planes(self):
        """Rappelle l'OpenSkyAPI pour mettre à jour la liste des avions en vols actuellement"""
        self.flying_planes = FlyingPlanes()
        self.coord_list = self.flying_planes.coordinates()
        self.plane_list = self.flying_planes.flying
        self.positions = self.flying_planes.positions
        self.route_coord = ([],[])
        self.refresh_planes_flag = False

    def clear_route(self):
        """Réinitialise la route courante"""
        self.route_coord = [],[]
        self.route_length = 0

    def compute_co2(self):
        """Calcule le bilan carbone de la route courante, en partant sur la base de 4,9 kg CO2 / km pour un Bombardier Global Express"""
        if self.route_length :
            self.co2 = convert_CO2(self.route_length)
        else :
            self.co2 = 0

    def clear_co2(self):
        """Reinitialise le compteur CO2 courant"""
        self.co2 = 0
        


def mainTest():
    # On crée un controler vide
    controler = Controler()

    # On essaie de récupérer la route d'un avion -> icao code à changer pour le test
    controler.compute_route('adf446')

    # On récupère les points de la route et on les affiche
    poslist = controler.route_coord
    print(poslist)

    # On change d'avion pour tester le changement de route
    controler.compute_route('a950ff')
    poslist = controler.route_coord
    print(poslist)

if __name__ == '__main__':
    mainTest()

