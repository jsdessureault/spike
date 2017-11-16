#!/usr/bin/env python
import roslib
import rospy, os, sys
import time
import aiml
from std_msgs.msg import String

rospy.init_node('node_chatbot', anonymous=True)
rospy.loginfo("Behavior_chatbot")

verbose = True

french = 1
english = 2

modeKeyboard = 1
modeVocal = 2

language = english
mode = modeKeyboard

last = ""


# Kernel is the public interface for AIML. 
k = aiml.Kernel()

# startup.xml load all aiml content
if verbose:
	rospy.loginfo("Loading AIML files.")

if language == english:
	k.learn("/home/pi/ros_catkin_ws/src/spike/assets/aiml/en/startup.xml")
	k.respond("LOAD AIML ENGLISH")
	
if verbose:
	rospy.loginfo("End of loading.")


if mode == modeKeyboard:
	presentation = False
	while True:
		the_input = raw_input("You> ")
		the_answer = k.respond(the_input)
		if len(the_answer) == 0:
			the_answer = k.respond("SPIKE NE SAIT PAS")	
		print "Spike> " + the_answer

if mode == modeVocal:
	if verbose:
		rospy.loginfo("Callback definition.")
	
	def callbackInput(data):
		global last
		if verbose:
			rospy.loginfo(rospy.get_caller_id() + " Message received: %s", data.data)
		patternAIML = data.data
		if patternAIML != dernier:
			templateAIML = k.respond(patternAIML)
			last = patternAIML
			topic_speak.publish(templateAIML)
			if verbose:
				rospy.loginfo("Chatbot answer: " + templateAIML)

	rospy.Subscriber("chatbot_input", String, callbackInput)
	topic_speak = rospy.Publisher('chatbot_speak', String, queue_size=10)

	if verbose:
		rospy.loginfo("Waiting for topics inputs...")	

	rospy.spin()
