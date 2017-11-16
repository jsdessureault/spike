#!/usr/bin/env python
import roslib
import rospy, os, sys
import time
import fuzzy.storage.fcl.Reader
import datetime
from array import array
from datetime import timedelta
from std_msgs.msg import String

rospy.init_node('node_selection', anonymous=True)
rospy.loginfo("Behavior_selection")

verbose = True


def BACKUPattentionFuzzy2Str(fuzzyValue):
	# Declaration des valeurs attention dans le .fcl
	# TODO: Trouver une facon d'aller chercher ces valeurs dans le fichier .fcl directement
	attentionArray = array('d', [0.0, 3.33, 6.66, 10.0])
	# Calcul la valeur la plus pres
	plusPetitEcart = 99
	attentionPlusProche = 0
	for x in range(0,4):
		ecart = abs(attentionArray[x] - fuzzyValue)
		if ecart < plusPetitEcart:
			plusPetitEcart = ecart
			attentionPlusProche = x
	if attentionPlusProche == 0:
		return "Behavior_PileVide"
	if attentionPlusProche == 1:
		return "Behavior_Deplacement"
	if attentionPlusProche == 2:
		return "Behavior_Conversation"
	if attentionPlusProche == 3:
		return "Behavior_Idle"
	return "NoOp"

def attentionFuzzy2Str(fuzzyValue, behavior):
	# Declaration des valeurs attention dans le .fcl
	# TODO: Trouver une facon d'aller chercher ces valeurs dans le fichier .fcl directement
	attentionArray = array('d', [0.0, 10.0])
	# Calcul la valeur la plus pres
	plusPetitEcart = 99
	attentionPlusProche = 0
	for x in range(0,2):
		ecart = abs(attentionArray[x] - fuzzyValue)
		if ecart < plusPetitEcart:
			plusPetitEcart = ecart
			attentionPlusProche = x
	if attentionPlusProche == 0:
		return "NoOp"
	if attentionPlusProche == 1:
		return behavior
	return "NoOp"

def humeurFuzzy2Str(fuzzyValue):
	# Declaration des valeurs attention dans le .fcl
	# TODO: Trouver une facon d'aller chercher ces valeurs dans le fichier .fcl directement
	humeurArray = array('d', [0.0, 5.0, 10.0])
	# Calcul la valeur la plus pres
	plusPetitEcart = 99
	humeurPlusProche = 0
	for x in range(0,3):
		ecart = abs(humeurArray[x] - fuzzyValue)
		if ecart < plusPetitEcart:
			plusPetitEcart = ecart
			humeurPlusProche = x
	if humeurPlusProche == 0:
		return "Joyeux"
	if humeurPlusProche == 1:
		return "Neutre"
	if humeurPlusProche == 2:
		return "Triste"
	return "Neutre"

		
def energieFuzzy2Str(fuzzyValue):
	# Declaration des valeurs attention dans le .fcl
	# TODO: Trouver une facon d'aller chercher ces valeurs dans le fichier .fcl directement
	energieArray = array('d', [0.0, 10.0])
	# Calcul la valeur la plus pres
	plusPetitEcart = 99
	energiePlusProche = 0
	for x in range(0,2):
		ecart = abs(energieArray[x] - fuzzyValue)
		#rospy.loginfo("ecart: " + str(ecart))
		if ecart < plusPetitEcart:
			plusPetitEcart = ecart
			energiePlusProche = x
			#rospy.loginfo("plusProche: " + str(energiePlusProche))
	if energiePlusProche == 0:
		return "Basse"
	if energiePlusProche == 1:
		return "Neutre"
	return "Neutre"

rospy.set_param("texte_recu", "")
#self.texte_recu = ""
def callbackAssigneTexteEcoute(data):
	#self.texte_recu = data.data
	# Un parametre ROS plutot qu'une simple variable est utilisee ici.
	# La portee d'un callback n'est pas la meme que le reste du programme. 
	rospy.set_param("texte_recu", data.data)
	if verbose:
		rospy.loginfo(rospy.get_caller_id() + "Recu: %s", rospy.get_param("texte_recu"))
	
def callbackAmbiance(data):
    #  ATTENTION!  Il faudra refaire cette partie pour la faire gerer par l'attention.  
    if verbose:
        rospy.loginfo(rospy.get_caller_id() + "Recu du SNN: %s", data.data)
    nbSpikes = int(data.data)
    if nbSpikes > 0:
        humeurStr = "Triste"
        topic_humeur.publish(humeurStr)
        topic_attention_conversation.publish("DEMANDE_SILENCE") 


if verbose:
	rospy.loginfo("Initialisation des topics")

# Communication avec Behavior_joue_son
topic_joue_son = rospy.Publisher('topic_joue_son', String, queue_size=10)
# Communication avec Behavior_humeur (visage)
topic_humeur = rospy.Publisher('topic_humeur', String, queue_size=10)
topic_pensee = rospy.Publisher('topic_pensee', String, queue_size=10)

# Ajoute par Patrick
topic_wiki = rospy.Publisher('topic_wiki', String, queue_size=10)
# Fin de l'ajout

# Communication avec Behavior_idle 
topic_idle = rospy.Publisher('topic_idle', String, queue_size=10)
# Communication avec Behavior_chatbot
topic_attention_conversation = rospy.Publisher('topic_attention_conversation', String, queue_size=10)
# Enregistrement du callback de behavior_ecoute (pocketsphinx)
rospy.Subscriber("behavior_ecoute/output", String, callbackAssigneTexteEcoute)

# Enregistrement du callback d'ecoute du son ambient (par SNN)
rospy.Subscriber("topic_out_SNN_Ambiance", String, callbackAmbiance)

# Chargement du fichier .fcl - Fuzzy Control Language qui contient la logique floue 
if verbose:
	rospy.loginfo("Chargement du fichier .FCL - Logique floue")

# Initialisation de la logique floue
fuzzyLogicSystem = fuzzy.storage.fcl.Reader.Reader().load_from_file("/home/ubuntu/catkin_ws/src/spike/src/spike/fcl/selection.fcl")

# Declaration des tableaux de variables entrees et sorties 
fuzzy_logic_input = {
	"Senseur_Deplacement": 0.0,
	"Senseur_Vision": 0.0,
	"Senseur_Ecoute": 0.0,
	"Senseur_LRF": 0.0,
	"Senseur_Batterie": 0.0,
	"TempsDepuisDerniereAction": 0.0
	}

fuzzy_logic_output  = {
	"Attention_PileVide": 0.0,
	"Attention_Conversation": 0.0,
	"Attention_Idle": 0.0,
	"Attention_Deplacement": 0.0,
	"Humeur": 0.0,
	"Energie": 0.0
	}

# Variable retournee par logique flou (en string) 
attentionStr = ""
humeurStr = ""
energieStr = ""

# Variables pour la gestion de l'humeur
oldHumeur = 0
oldHumeurStr = ""
humeurStr = ""

# Variables pour la gestion de la reflexion
tempsReflexion = 0   # secondes
tempsReflexionMax = 3.0   # secondes
etatPensee = "Neutre"
oldAttention = ""

# Variables de gestion de temps
tempsDerniereBoucle = 0.0
chronoDebut = datetime.datetime.now()
chronoFin = chronoDebut

if verbose:
	rospy.loginfo("Boucle infinie de l'attention...")

tempsSleep = 1
while True:

	# On commence a compter le temps pour calcul du temps de derniere boucle. 
	chronoDebut = datetime.datetime.now()
	
	time.sleep(tempsSleep)
	
	# Variables d'entree
	fuzzy_logic_input["Senseur_Deplacement"] = 0.0
	fuzzy_logic_input["Senseur_Vision"] = 0.0
	
	#print("texte: *"+rospy.get_param("texte_recu")+"*")
	if (rospy.get_param("texte_recu") == ""):
		fuzzy_logic_input["Senseur_Ecoute"] = 0.0
		#print("Senseur_ecoute: 0")
	else:
		fuzzy_logic_input["Senseur_Ecoute"] = 10.0
		#print("Senseur_ecoute: 10")
	fuzzy_logic_input["Senseur_LRF"] = 10.0
	fuzzy_logic_input["Senseur_Batterie"] = 10.0

	# Calcul des variables entree de logique floue

	# Compte le temps depuis derniere action pour detecter un idle. 
	tempsCumule = fuzzy_logic_input["TempsDepuisDerniereAction"]
	fuzzy_logic_input["TempsDepuisDerniereAction"] =  tempsCumule + tempsDerniereBoucle
	print(tempsCumule, tempsDerniereBoucle, fuzzy_logic_input["TempsDepuisDerniereAction"])

	# Selectionne le behavior qui aura l'attention avec le system de logique flou. 
	# Selectionne egalement l'humeur
	fuzzyLogicSystem.calculate(fuzzy_logic_input, fuzzy_logic_output)

	# Assignation des variables de sortie
	attentionPileVideFuzzy = fuzzy_logic_output["Attention_PileVide"]
	attentionConversationFuzzy = fuzzy_logic_output["Attention_Conversation"]
	attentionDeplacementFuzzy = fuzzy_logic_output["Attention_Deplacement"]
	attentionIdleFuzzy = fuzzy_logic_output["Attention_Idle"]
	humeurFuzzy = fuzzy_logic_output["Humeur"]
	energieFuzzy = fuzzy_logic_output["Energie"]

	# Conversion en string
	oldAttention = attentionStr
	attentionIdleStr = attentionFuzzy2Str(attentionIdleFuzzy, "Behavior_Idle")
	attentionDeplacementStr = attentionFuzzy2Str(attentionDeplacementFuzzy, "Behavior_Deplacement")
	attentionConversationStr = attentionFuzzy2Str(attentionConversationFuzzy, "Behavior_Conversation")
	attentionPileVideStr = attentionFuzzy2Str(attentionPileVideFuzzy, "Behavior_PileVide")

	oldHumeur = humeurStr
	humeurStr = humeurFuzzy2Str(humeurFuzzy)
	energieStr = energieFuzzy2Str(energieFuzzy)

	# affichage des valeurs a des fins de debugage
	#if verbose:
	rospy.loginfo("AttentionIdle: " + str(attentionIdleFuzzy) + " - " + attentionIdleStr)
		#rospy.loginfo("AttentionDeplacement: " + str(attentionDeplacementFuzzy) + " - " + attentionDeplacementStr)
		#rospy.loginfo("AttentionPileVide: " + str(attentionPileVideFuzzy) + " - " + attentionPileVideStr)
		#rospy.loginfo("AttentionConversation: " + str(attentionConversationFuzzy) + " - " + attentionConversationStr)
		#rospy.loginfo("Humeur: " + str(humeurFuzzy)  + " - " + humeurStr)
		#rospy.loginfo("Energie: " + str(energieFuzzy)  + " - " + energieStr)	

	# On reinitialise la pensee a neutre si ca fait un moment. 
	#if (etatPensee == "Reflexion"):
	#	tempsReflexion = tempsReflexion + tempsDerniereBoucle
	#if (etatPensee == "Reflexion") and (tempsReflexion >= tempsReflexionMax): 
	#	etatPensee = "Neutre"
	#	topic_pensee.publish(etatPensee)
	#	tempsReflexion = 0
	
	# On met a jour l'humeur dans l'interface
	#if (humeurStr != oldHumeur):
	#	topic_humeur.publish(humeurStr)

	if attentionConversationStr == "Behavior_Conversation":
		# Lecture et reinitialisation du parametre texte_recu
		texte_recu = rospy.get_param("texte_recu")
		rospy.set_param("texte_recu", "")
		attentionStr = attentionConversationStr
		topic_pensee.publish("Reflexion")
		chatbot = True
		# Faire appel a tous les behaviors prioritaires, selon instruction detectee.
		# Si aucune instruction prioritaire, on fait appel au chatbot.
#		if (texte_recu == "terminator"):
#			# Appel du behavior terminator
#			print("Terminator!")
#			humeurStr = "Terminator"
#			topic_humeur.publish(humeurStr)
#			topic_joue_son.publish(humeurStr)
#			chatbot = False
		if (texte_recu == "troll"):
			# Appel du behavior terminator
			print("Troll!")
			humeurStr = "Troll"
			topic_humeur.publish(humeurStr)
			chatbot = False
		if (texte_recu == "sad"):
			# Appel du behavior terminator
			print("triste!")
			humeurStr = "Triste"
			topic_humeur.publish(humeurStr)
			chatbot = False
		if (texte_recu == "tired"):
			# Appel du behavior terminator
			print("Tired!")
			humeurStr = "Fatigue"
			topic_humeur.publish(humeurStr)
			chatbot = False
		if (texte_recu == "happy"):
			# Appel du behavior terminator
			print("Happy!")
			humeurStr = "Joyeux"
			topic_humeur.publish(humeurStr)
			chatbot = False
		if (texte_recu == "spike shutdown"):
			print("Shutdown!")
			# Appel OS shutdown
			os.system("sudo shutdown now")
			chatbot = False
		if (texte_recu == "spike reboot"): 
			print("reboot!")
			# Appel OS reboot
			os.system("sudo reboot")
			chatbot = False

		# Ajoute par Patrick
		if (texte_recu == 'terminator'):
			print('Learning something from wiki')
			learnstring = 'What is hello world'
			topic_wiki.publish(learnstring)
			chatbot = False
		# Fin de l'ajout

		# Ultimement, si aucune instruction reconnue, appel du chatbot
		if (chatbot == True):  
			print("Chatbot")
			humeurStr = "Joyeux"
			topic_humeur.publish(humeurStr)
			topic_attention_conversation.publish(texte_recu)
		fuzzy_logic_input["TempsDepuisDerniereAction"] = 0.0
		#if verbose:
			#print "Node Attention: Behavior prioritaire: " + attentionStr

	if attentionIdleStr == "Behavior_Idle":
		attentionStr = attentionIdleStr
		topic_idle.publish("null")
		fuzzy_logic_input["TempsDepuisDerniereAction"] = 0.0
		
	if verbose:
		print "Node Attention: Behavior prioritaire: " + attentionStr


	# Si changement behavior ou changement humeur et pas deja en reflexion
	#if ((attentionStr != oldAttention) or (humeurStr != oldHumeur)) and (etatPensee != "Reflexion"):
	#	etatPensee = "Reflexion"
	#	topic_pensee.publish(etatPensee)
	#	tempsReflexion = 0.0
	#	fuzzy_logic_input["TempsDepuisDerniereAction"] = 0.0

	# Mise a jour des valeur de fin pour calcul du temps de derniere boucle. 
	chronoFin = datetime.datetime.now()
	tempsTmp = chronoFin - chronoDebut    
	tempsDerniereBoucle =  10.0 * (tempsTmp.microseconds / 1000000.0)
	
	#if verbose:
	#	rospy.loginfo("Duree derniere boucle: %s", tempsDerniereBoucle)
