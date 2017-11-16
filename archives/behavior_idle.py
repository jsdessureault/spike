#!/usr/bin/env python
import roslib
import rospy, os, sys
import time
import random
from std_msgs.msg import String

rospy.init_node('node_idle', anonymous=True)
rospy.loginfo("Behavior_idle")

verbose = True


if verbose:
	rospy.loginfo("Initialisation des topics")

topic_idle_parle = rospy.Publisher('topic_idle_parle', String, queue_size=10)
topic_idle_son = rospy.Publisher('topic_idle_son', String, queue_size=10)
topic_idle_aiml_pattern = rospy.Publisher('topic_idle_aiml_pattern', String, queue_size=10)


def callbackAIML(data):
	if verbose:
		rospy.loginfo(rospy.get_caller_id() + " Message recu: %s", data.data)
	templateAIML = data.data
	topic_idle_parle.publish(templateAIML)

def callbackIDLE(data):
	if verbose:
		rospy.loginfo(rospy.get_caller_id() + " Message recu: %s", data.data)
	templateIDLE = data.data
	# Quand il ne se passe rien:
	# Il peut appeler chat bot pour se trouver une replique d'ennui. 	
	# Ou il joue un son.

	# Tire un nombre aleatoire (bornes incluses)
	nb = random.randint(0, 9)

	if nb <= 5:	
		# Ici, il dit qu'il s'ennuie
		if verbose:
			rospy.loginfo("demande ce qu'il faut dire au chatbot quand on s'ennuie")
		topic_idle_aiml_pattern.publish("SPIKE ENNUI")
	else:
		# Ici, il va produire un son. 
		if verbose:
			rospy.loginfo("Envoie message au behavior_joue_son")
		topic_idle_son.publish("EtatEveil")


rospy.Subscriber("topic_idle", String, callbackIDLE)
rospy.Subscriber("topic_idle_aiml_template", String, callbackAIML)

rospy.spin()



