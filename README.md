# UAV-PIREN
Calibration des températures mesurées par drone sur une parcelle test située dans le parc naturel de La Bassée (Bassin de la Seine)
V16 - 21/06
- Ajout de modèle de correlogram à plusieurs couches 
- Méthode d'interpolation Intrinsic Collocated Cokriging - MM2

V15 - 15/06 :
- Ajout d'une méthode d'interpolation : Co Kriging ( Intrinsic Collocated Cokriging - MM1 / Simple Cokriging / FullCokriging (pas au point)




V14 - 27/04 :
- Méthode de calcule de variogram fonctionnel avec directionalité prise en considération
- Pré-calcul d'un fichier CSV (506 Mo) contenant les coordonnées x,y et values d'une thermo-mosaïque

V13 - 20/04 :
- Méthode d'optimisation des modèle de covariogramme à une et deux "couches" pour le workflow test : collocatedcokriging

V12 -14/04 :
-Méthode d'interpolation : Co-Kriging ( non fonctionelle)
Importation d'un jeu de donnée/ Variogrammes depuis Surfer

V11 - 08/04 :
Méthode d'interpolation : Co-Kriging ( non fonctionelle)

V10 - 24/03 : 
- Courbe des différences entre les valeurs de T° et PT° ( Pseudo-Température)
- Estimation des valeurs de Pseudo-Température pour chaque 
- Mask des labels de clustering sur les données IR (les résolutions thermo/ortho mosaïques sont différentes)
- Boxplot affichant l'évolution du signal IR des différents labels de clustering 
- Interpolation des valeurs de Pseudo-Température toutes les 15 mins.

V9 - 26/02 :
- Utilisation de la librairie GeostatsPy pour le traitement + visualisation des variograms
- Transformation en normal score de toutes les bandes pour un target/patch
-Plot d'une map 2d des valeurs issues de la transformation
-Variogram Maps/Number of Pairs pour un patch donné 
-Variogram expérimental : pas fonctionnel 
V8 - 24/02 :
-Suppression de l'effet de la rivière sur l'orthomosaique du visible ( : "cropped" )
-Transformation de la valeur 255 en mask nodata (pas d'effet en dehors de GDAL et Rasterio)
-Réorganisation du clustering dans un noteboot indépendant 
Clustering Kmeans avec groupe choisi manuellement par l'utilisateur sur les bandes RGB/HSV, la bande normalisée n'est pas au goût du jour 
Sauvegarde possible en fichier .tif des résultats des Kmeans mentionnant le nombre de groupe K et le type de bande
Figure regroupant la proportion de chaque groupe pour chaque cible sous forme d'histogramme + patch permettant de visualiser la bande RGB, et le résultat du Kmeans pour chaque cible
- Correction d'un problème de localisation survenant sur les patchs de chaque cible

V7 - 19/02 :
-Clustering avec nombre de classe déterminée par l'utilisateur sur les bandes RGB, HSV, RGB normalisée
-Ajout des histogram permettant de connaitre la proportion de surface de chaque classe.
-Plot d'une figure avec toutes les bandes (R,G,B,RGB,Greensess,H,S,V) ainsi que des patchs de la target en RGB normalisée et HSV.

V6 - 18/02 : 
- Ajout des variogrammes fonctionnels 
- Création d'un fichier .tif constitué de la bande Greeness

V5 - 17/02:
-Données visibles :
Patch (fenêtrage) de largeur variable convertible en DataFrame (et en .csv si voulu)
Ajout d'une bande réunissant RGB
Ajout d'une bande : Greeness
Variogramme (non fonctionnel pour l'instant) pour les targets (sondes) au choix ( RGB et HSV )


V4 - 11/02:
Lecture donnée visible : 
- Normalisation des bandes R G B
- Transformation en bandes H S V
- Plot des Area Of Interest (sondes)


V3 - 10/02:
-Lecture des données d'orthomosaique (IR) : 
Plot d'une sonde/IR en particulier 
Comparaison des valeurs avec la sonde la plus shallow à un interval de temps spécifié


V2 - 09/02 :

-Lecture des données d'orthomosaique (IR) : 
Lecture de toutes les images IR
Plot de toutes les zones d’intérêt autour des sondes 
Plot de toutes les zones d’intérêt autour d'un échantillon de sondes 
Comparaison des valeurs avec la sonde la plus shallow à un interval de temps défini 

V1. 08/02
- Lecture des thermos : 
Plot d'une/plusieurs sondes sur intervalle de temps défini par l'utilisateur 

-Lecture des données d'orthomosaique (IR) : 
Positions de chaque sondes acquises par un fichier .txt
Création d'un mask circulaire d'un rayon r défini par l'utilisateur autour de chaque sonde -> fonctionne seulement pour une ortho au choix
