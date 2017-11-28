#!/usr/bin/env python
import roslib
import rospy, os, sys
import time
import aiml
from std_msgs.msg import String

rospy.init_node('node_chatbot', anonymous=True)
rospy.loginfo("Behavior_chatbot")

verbose = True

modeKeyboard = 1
modeVocal = 2

mode = modeVocal

last = ""

espeak = rospy.Publisher('/espeak', String, queue_size=1)

# Kernel is the public interface for AIML. 
k = aiml.Kernel()

# startup.xml load all aiml content
if verbose:
	rospy.loginfo("Loading AIML files.")

k.learn("/home/pi/ros_catkin_ws/src/spike/assets/aiml/en/startup.xml")
the_answer = k.respond("LOAD AIML")
if verbose:
	rospy.loginfo(the_answer)

if mode == modeKeyboard:

	while True:
		the_input = raw_input("You> ")
		the_answer = k.respond(the_input)
		if len(the_answer) == 0:
			the_answer = k.respond("SPIKE NE SAIT PAS")	
		print "Spike> " + the_answer
		espeak.publish(the_answer)

if mode == modeVocal:
    if verbose:
        rospy.loginfo("Callback definition.")
	
    def callbackInput(data):
	if verbose:
            rospy.loginfo(rospy.get_caller_id() + " Message received: %s", data.data)
            patternAIML = data.data
	    #if patternAIML != dernier:
	    templateAIML = k.respond(patternAIML)
	    #last = patternAIML
	    espeak.publish(templateAIML)
	    if verbose:
		rospy.loginfo("Chatbot answer: " + templateAIML)

    rospy.Subscriber("/speech_recognition", String, callbackInput)

    if verbose:
	rospy.loginfo("Waiting for topics inputs...")	

rospy.spin()
