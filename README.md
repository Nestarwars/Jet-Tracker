# JetTracker

## Nestor Laborier

### Dec 2022

Jet Tracker est une application Python pour le suivi des jets privés dans le monde, et le calcul d'équivalent CO2 de leur route.
Les données utilisées sont celles du réseau OpenSky Network.

## Dépendances :

	- Python3 en distribution AnaConda

	- PyQt5

	- CartoPy

	- GeoPy

	- Matplotlib.pyplot

	- Numpy

	- Module CSV

	- Module Requests

	- Module JSON

	- OpenSky Python API
	
### Avertissement

Pour fonctionner correctement, vous devez disposer d'un compte OpenSkyAPI, et entrer les credentials dans le fichier `link.py` aux lignes 18 et 47.

En raison des limites de taille de GitHub, il manque également une DB des avions dans le dossier `planeDB`. Vous devez télécharger la base `aircraftDatabase-2022-11.csv` sur l'OpenSkyNetwork ([Téléchargez ici](https://opensky-network.org/datasets/metadata/aircraftDatabase-2022-11.csv)) et la mettre dans dans le dossier `planeDB`.

## Mentions :

Développé sur Visual Studio Code, en utilisant les APIs Python et REST de OpenSkyNetwork.
Les bases de données utilisées sont fournies par le réseau OpenSkyNetwork et sont utilisées dans le cadre d'un travail étudiant. Elles ne doivent en aucun cas être extraites de ce repo ou réutilisées sans demande à OpenSkyNetwork. 
La licence attachée ici ne concerne que le code produit par Nestor Laborier (les fichiers `.py`).
