####################################################################
### CONSTRUCTION DE LA BASE DE DONNEES DE JETS PRIVES
### 24.12.2022
### Nestor Laborier
####################################################################

import csv

model_numbers = dict()

# On constitue la base de données des modèles de jets privés enregistrés dans le fichier doc8643AircraftTypes.csv

with open('.\\planeDB\\doc8643AircraftTypes.csv', newline='') as csvfile:
    csvfile.readline()

    lines = csv.reader(csvfile, delimiter=',', quotechar='"')
    
    for row in lines:
        if row[0] == "LandPlane" and row[4] == "Jet" and row[5] in ["BOMBARDIER","GULFSTREAM","DASSAULT","PIAGGIO"] or (row[5] == "CESSNA" and "Citation" in row[6]) :
            if "Rafale" not in row[6] and "Mirage" not in row[6] :
                
                description = row[1]
                model_nbr = row[2]
                manufacturer = row[5]
                model = row[6]

                model_numbers[model_nbr] = model

                # DEBUG AFFICHAGE DE LA LISTE DES MODELES
                # print(description + model_nbr + manufacturer + model)


# CLASSE DE LA LISTE DES JETS PRIVES IMMATRICULES 

class PrivateJets :
    """Classe de la liste des jets privés immatriculés en novembre 2022"""
    def __init__(self) :

        self.jets = dict()      # Dictionnaire des jets privés avec leur ICAO comme clef

        with open('.\\planeDB\\aircraftDatabase-2022-11.csv','r') as csvfile:
    
            csvfile.readline()

            lines = csv.reader(csvfile, delimiter=',', quotechar='"')

            for row in lines :
                if row[5] in model_numbers :
                    
                    self.jets[row[0]] = [row[2],row[4],model_numbers[row[5]]]

                    # DEBUG AFFICHAGE DE LA LISTE DES AVIONS CORRESPONDANTS AUX MODELES
                    # useful = [row[0],row[1],row[2],row[3],row[4],row[5]]
                    # print(", ".join(useful))

        # DEBUG AFFICHAGE DU NOMBRE DE JETS
        # print(len(self.jets))

    def __repr__(self) :
        output = ''
        for jet in self.jets :
            output += jet + '   ' + f"{self.jets[jet][0]:<12}" + ' ' + self.jets[jet][1] + '\n '
        return output

    # Rafraichir la liste des jets privés
    def refreshList(self) :
        """Réinitialise la liste des jets privés (en cas de mise à jour du fichier)"""
        self.__init__(self)

    def selectICAOS(self,icao_select_list) : 
        """Selectionner les codes ICAO parmi self selon une liste de codes ICAO (intersection)"""
        selected_planes = []
        for icao in self.jets.keys() :
            if icao in icao_select_list :    
                selected_planes.append(icao)
            
        return selected_planes
 
    def extractICAOS(self,icao_select_list) :
        """Filtrer les avions selon une liste de codes ICAO"""
        temp = dict()
        for icao in icao_select_list :
            if icao in self.jets.keys() : 
                temp[icao] = self.jets[icao]
        self.jets = temp

# PROCEDURES DE TESTS 

def mainTest(): 
    print("\n Liste des modèles d'avions retenus comme jets privés :")
    print(', '.join(model_numbers))

    print("\n Liste des avions immatriculés retenus comme jets privés : \n")
    private = PrivateJets()

    plane = private.jets['4b1804']
    print(plane)


if __name__ == "__main__" : 
    mainTest()
