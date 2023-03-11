####################################################################
### INTERFACE GRAPHIQUE
### 25.12.2022
### Nestor Laborier
####################################################################

### Module d'interface
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import random

### Module pour la cartographie
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.img_tiles as cimgt

### Module pour le tracé des données
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

### Module controleur
from controler import *



class Planisphere(QGroupBox):
    """Bloc carte, pour l'affichage des avions"""
    def __init__(self, parent, controler):
        super().__init__(parent)
        self.controler = controler
        self.controler.addClient(self)

        self.setTitle("CARTE")
        layout = QVBoxLayout()

        self.controler.prep_plot_planes()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.draw()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.drawgraph()    

    def drawgraph(self):
        """Dessine la carte et trace les positions du ou des avion(s) sélectionnés"""
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS)
        ax.add_feature(cfeature.OCEAN)
        (x,y) = self.controler.plane_coord_list
        (ry,rx) = self.controler.route_coord
        ax.set_global()
        ax.plot(x, y, 'or')
        ax.plot(rx,ry,'-g')
        self.figure.tight_layout()
        self.canvas.draw()

    def refresh(self):
        self.drawgraph()


class LogWidget(QTextEdit):
    """Bloc log, désactivé par défaut, pour le debogage"""
    def __init__(self, parent, controler):
        super().__init__(parent)
        self.controler = controler
        self.controler.addClient(self)
        self.setMinimumHeight(200)
        self.setReadOnly(True)
        self.append("BIENVENUE DANS JET TRACKER \n")
        font = QFont("Courier New", 12)
        self.setFont(font)

    def refresh(self):
        message = self.controler.message
        if message:
            self.append(message)


class PlaneListWidget(QGroupBox):
    """Bloc liste des avions, pour la sélection d'un avion"""
    def __init__(self, parent, controler):
        super().__init__(parent)
        self.controler = controler
        self.controler.addClient(self)
        self.setTitle("Liste des jets en vol")
        self.setMinimumWidth(600)

        layout = QGridLayout()
        self.setLayout(layout)
        self.listwidget = QListWidget()
        self.set_list()

        self.listwidget.clicked.connect(self.plane_selec)
        layout.addWidget(self.listwidget)

        self.reset_button = QPushButton("Reset de la sélection")
        layout.addWidget(self.reset_button)
        self.reset_button.clicked.connect(self.reset_selec)

    def set_list(self): 
        """Crée la liste des avions en vols pour la sélection"""
        self.listwidget.insertItem(0," ICAO  | Marque et modèle                           | Pays d'origine       | Immat    ")
        self.listwidget.insertItem(1,"--------------------------------------------------------------------------------------")
        font = QFont("Courier New", 10)
        self.listwidget.setFont(font)
        i = 2
        for plane in self.controler.plane_list :
            self.listwidget.insertItem(i," | ".join([plane.icao,f"{plane.model:<42}",f"{plane.country:<20}",f"{plane.ID:<8}"]))
            i+=1

    def plane_selec(self, qmodelindex):
        item = self.listwidget.currentItem()
        message = item.text()

        if message[0] == " " or message[0] =="-" :
            return None
        else :
            self.controler.select_plane(message[:6])
            self.controler.clear_route()
            self.controler.clear_co2()
            self.controler.compute_route(message[:6])

        self.controler.refreshAll("Sélectionné : " + message)

    def reset_selec(self):
        self.controler.prep_plot_planes()
        self.controler.clear_route()
        self.controler.clear_co2()
        self.controler.refreshAll("Sélection réinitialisée")

    def refresh(self):
        if self.controler.refresh_planes_flag == True :
            self.controler.refresh_planes()
            self.listwidget.clear()
            self.set_list()
        else :
            pass

class OneLineInfo(QTextEdit):
    """Bloc de log mini, une ligne pour afficher l'état actuel"""
    def __init__(self,parent,controler):
        super().__init__(parent)
        self.controler = controler
        self.controler.addClient(self)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        font = QFont("Courrier New", 12)
        self.setFont(font)
        self.setFixedHeight(self.fontMetrics().height() + 11)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                       
        self.append("Bienvenue dans Jet Tracker")

    def refresh(self):
        message = self.controler.message
        if message :
            self.clear()
            self.append(message)             

class ButtonsWidget(QMenuBar):
    """Bloc de boutons et de cadres, pour l'affichage des différentes valeurs importantes"""
    def __init__(self,parent,controler):
        super().__init__(parent)
        self.controler = controler
        self.controler.addClient(self)
        buttongrid = QVBoxLayout()

        self.reset_button = QPushButton('Rafraichir la liste des avions')
        self.reset_button.clicked.connect(self.refresh_planes)
        
        self.label_dist = QLabel("Distance parcourue par l'avion sélectionné : ")
        self.label_dist.setFixedHeight(self.label_dist.fontMetrics().height() + 11)

        self.route_length = QTextEdit()
        self.route_length.setReadOnly(True)
        self.route_length.setLineWrapMode(QTextEdit.NoWrap)
        self.route_length.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        font = QFont("Courrier New", 20)
        self.route_length.setFont(font)
        self.route_length.setFixedHeight(self.route_length.fontMetrics().height() + 11)
        self.route_length.append("")

        self.co2_button = QPushButton('Bilan CO2 partiel')
        self.co2_button.clicked.connect(self.compute_co2)

        self.sublabel1_co2 = QLabel("Estimation du CO2,\nbasée sur un Bombardier Global Express \n(soit 4,9 kg CO2e/km) ")
        # Donnée : https://www.sciencesetavenir.fr/nature-environnement/climat/l-impact-ecologique-demesure-des-jets-prives_164673

        self.bilan_co2 = QTextEdit()
        self.bilan_co2.setReadOnly(True)
        self.bilan_co2.setLineWrapMode(QTextEdit.NoWrap)
        self.bilan_co2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        font = QFont("Courrier New", 20)
        self.bilan_co2.setFont(font)
        self.bilan_co2.setFixedHeight(self.bilan_co2.fontMetrics().height() + 11)

        self.sublabel2_co2 = QLabel("Equivalent en trajet Lyon-Paris en TGV\n(soit 0,743 kg CO2e/pers)")
        # Donnée : https://ressources.data.sncf.com/explore/dataset/emission-co2-tgv/table/

        self.bilan_co2_tgv = QTextEdit()
        self.bilan_co2_tgv.setReadOnly(True)
        self.bilan_co2_tgv.setLineWrapMode(QTextEdit.NoWrap)
        self.bilan_co2_tgv.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        font = QFont("Courrier New", 20)
        self.bilan_co2_tgv.setFont(font)
        self.bilan_co2_tgv.setFixedHeight(self.bilan_co2.fontMetrics().height() + 11)

        self.sublabel3_co2 = QLabel("Equivalent en steaks de boeuf\n(soit 1,31 kg CO2e/steak de 100gr)")
        # Donnée : https://bilans-ges.ademe.fr/docutheque/docs/%5BBase%20Carbone%5D%20Documentation%20g%C3%A9n%C3%A9rale%20v11.pdf

        self.bilan_co2_steak = QTextEdit()
        self.bilan_co2_steak.setReadOnly(True)
        self.bilan_co2_steak.setLineWrapMode(QTextEdit.NoWrap)
        self.bilan_co2_steak.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        font = QFont("Courrier New", 20)
        self.bilan_co2_steak.setFont(font)
        self.bilan_co2_steak.setFixedHeight(self.bilan_co2.fontMetrics().height() + 11)


        
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        
        buttongrid.addWidget(self.label_dist,0)
        buttongrid.addWidget(self.route_length,0)
        buttongrid.addWidget(self.line,0)

        self.spacer = QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        buttongrid.addItem(self.spacer)
        
        buttongrid.addWidget(self.sublabel1_co2,0)
        buttongrid.addWidget(self.bilan_co2,0)

        buttongrid.addWidget(self.sublabel2_co2,0)
        buttongrid.addWidget(self.bilan_co2_tgv,0)

        buttongrid.addWidget(self.sublabel3_co2,0)
        buttongrid.addWidget(self.bilan_co2_steak,0)
        
        self.spacer = QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        buttongrid.addItem(self.spacer)

        buttongrid.addWidget(self.co2_button,0)
        buttongrid.addWidget(self.line,0)
        buttongrid.addWidget(self.reset_button,0)

        self.setLayout(buttongrid)

    def refresh(self):
        length = self.controler.route_length
        self.route_length.clear()
        if length != 0 :
            self.route_length.append("{:.2f}".format(length)+' km') 

        co2 = self.controler.co2
        self.bilan_co2.clear()
        self.bilan_co2_tgv.clear()
        self.bilan_co2_steak.clear()
        if co2 != 0 : 
            self.bilan_co2.append("{:.0f}".format(co2)+' kg CO2e')
            self.bilan_co2_tgv.append("{:.0f}".format(co2/0.743)+' trajets')
            self.bilan_co2_steak.append("{:.0f}".format(co2/1.31)+' steaks')
    
    def compute_co2(self):
        self.controler.compute_co2()
        self.controler.refreshAll('')

    def refresh_planes(self):
        self.controler.refresh_planes_flag = True
        self.controler.refreshAll("Listes des avions rafraichie")

class MainWidget(QGroupBox):
    def __init__(self, parent, controler):
        super().__init__(parent)
        self.setMinimumSize(1920, 1080)
        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        menu = QHBoxLayout()
        self.paramswidget = PlaneListWidget(self, controler)
        self.chartswidget = Planisphere(self, controler)
        # self.logwidget = LogWidget(self, controler)
        self.buttonswidget = ButtonsWidget(self,controler)
        self.oneline = OneLineInfo(self,controler)
        hlayout.addWidget(self.buttonswidget, 1)
        hlayout.addWidget(self.chartswidget, 4)
        vlayout.addLayout(hlayout,3)
        vlayout.addWidget(self.paramswidget,1)
        #vlayout.addWidget(self.logwidget, 0)
        vlayout.addWidget(self.oneline,0)
        self.setLayout(vlayout)


class MainWindow(QMainWindow):
    def __init__(self, controler):
        super().__init__()
        self.setWindowTitle("JET TRACKER")
        self.setWindowIcon(QIcon("icon.png"))
        self.mainwidget = MainWidget(self, controler)
        self.setCentralWidget(self.mainwidget)

    def _createMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

def main():
    app = QApplication([])
    controler = Controler()
    win = MainWindow(controler)
    win.show()
    app.exec()


if __name__ == '__main__':
    main()