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

rospy.set_param("texte_recu", "")
#self.texte_recu = ""
def callbackAssigneTexteEcoute(data):
	#self.texte_recu = data.data
	# Un parametre ROS plutot qu'une simple variable est utilisee ici.
	# La portee d'un callback n'est pas la meme que le reste du programme. 
	rospy.set_param("texte_recu", data.data)
	if verbose:
		rospy.loginfo(rospy.get_caller_id() + "Recu: %s", rospy.get_param("texte_recu"))

if verbose:
	rospy.loginfo("Initialisation des topics")

# Communication avec Behavior_joue_son
topic_joue_son = rospy.Publisher('topic_joue_son', String, queue_size=10)

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
# rospy.Subscriber("topic_out_SNN_Ambiance", String, callbackAmbiance)

# JSD: LOGIQUE FLOUE EN COMMENTAIRE. - REACTIVER ETE 2017. 
# Chargement du fichier .fcl - Fuzzy Control Language qui contient la logique floue 
#if verbose:
#	rospy.loginfo("Chargement du fichier .FCL - Logique floue")

# Initialisation de la logique floue
#fuzzyLogicSystem = fuzzy.storage.fcl.Reader.Reader().load_from_file("/home/ubuntu/catkin_ws/src/spike/src/spike/fcl/selection.fcl")

# Declaration des tableaux de variables entrees et sorties 
#fuzzy_logic_input = {
#	"TempsDepuisDerniereAction": 0.0
#	}

#fuzzy_logic_output  = {
#	"Selection_Idle": 0.0,
#	}

# Variables de gestion de temps
#tempsDerniereBoucle = 0.0
#chronoDebut = datetime.datetime.now()
#chronoFin = chronoDebut

if verbose:
	rospy.loginfo("Boucle infinie de la selection...")

topic_attention_conversation.publish("SPIKE PRET")
tempsSleep = 1
while True:

	# On commence a compter le temps pour calcul du temps de derniere boucle. 
	#chronoDebut = datetime.datetime.now()
	
	time.sleep(tempsSleep)
	
	# Compte le temps depuis derniere action pour detecter un idle. 
	#tempsCumule = fuzzy_logic_input["TempsDepuisDerniereAction"]
	#fuzzy_logic_input["TempsDepuisDerniereAction"] =  tempsCumule + tempsDerniereBoucle
	#print(tempsCumule, tempsDerniereBoucle, fuzzy_logic_input["TempsDepuisDerniereAction"])

	# Selectionne le behavior qui aura l'attention avec le system de logique flou. 
	#fuzzyLogicSystem.calculate(fuzzy_logic_input, fuzzy_logic_output)

	# Assignation des variables de sortie
	#attentionIdleFuzzy = fuzzy_logic_output["Attention_Idle"]

	# Lecture et reinitialisation du parametre texte_recu
	texte_recu = rospy.get_param("texte_recu")
	rospy.set_param("texte_recu", "")
	# Faire appel a tous les behaviors prioritaires, selon instruction detectee.
	# Si aucune instruction prioritaire, on fait appel au chatbot.
	if (texte_recu == "shutdown"):
		print("Shutdown!")
		# Appel OS shutdown
		os.system("sudo shutdown now")
	# Ajoute par Patrick
	if (texte_recu == 'Learn me something'):
		print('Learning me something.')
		learnstring = 'What is hello world'
		topic_wiki.publish(learnstring)

	if (texte_recu == "spike"):
		print("Spike")
		topic_attention_conversation.publish(texte_recu)
	if (texte_recu == "tell me a joke"):
		print("Tell me a joke")
		topic_attention_conversation.publish(texte_recu)
	if (texte_recu == "hello"):
		print("hello")
		topic_attention_conversation.publish(texte_recu)
	if (texte_recu == "hi"):
		print("hi")
		topic_attention_conversation.publish(texte_recu)

	# Reactiver lors de la remise en fonction du chatbot. 
	# Ultimement, si aucune instruction reconnue, appel du chatbot
	#if (chatbot == True):  
	#    print("Chatbot")
	#    topic_attention_conversation.publish(texte_recu)

	#if attentionIdleStr == "Behavior_Idle":
	#	topic_idle.publish("null")

	# Mise a jour des valeur de fin pour calcul du temps de derniere boucle. 
	#chronoFin = datetime.datetime.now()
	#tempsTmp = chronoFin - chronoDebut    
	#tempsDerniereBoucle =  10.0 * (tempsTmp.microseconds / 1000000.0)
	
	#if verbose:
	#	rospy.loginfo("Duree derniere boucle: %s", tempsDerniereBoucle)
