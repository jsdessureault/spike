#!/usr/bin/env python
import roslib
import rospy, os, sys
import time
from std_msgs.msg import String
from espeak import espeak

rospy.init_node('node_speak', anonymous=True)
rospy.loginfo("Behavior_speak")

verbose = True

modeTest = 1
modeTopic = 2

mode = modeTopic

def wait():
    while espeak.is_playing:
        pass

def callback(data):
        if verbose:
                rospy.loginfo(rospy.get_caller_id() + " text to say: %s", data.data)

        text_to_say = data.data
        espeak.synth(text_to_say)
        #wait()


# On s'inscrit au topic
rospy.Subscriber("/espeak", String, callback)

if mode == modeTest:

    while True:
        text_to_say = raw_input("Spike will repeat>")
        espeak.synth(text_to_say)
	#wait()

# Puisqu'on attend un signal, il ne faut pas quitter
# L'instruction suivante permet de rester dans le programme
rospy.spin()
