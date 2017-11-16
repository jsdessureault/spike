#!/usr/bin/env python
import roslib
import rospy, os, sys
import time
from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient

rospy.init_node('node_joue_son', anonymous=True)
rospy.loginfo("Behavior_joue_son")

verbose = True

modeTest = 1
modeRecoitSignal = 2

SAY = -3
WAV = -2

mode = modeTest

if verbose:
	rospy.loginfo("Initialisation du son")

soundhandle = SoundClient()
rospy.sleep(1)
soundhandle.stopAll()
if verbose: 
	rospy.loginfo("Son initialise!")

soundAssets = '/home/pi/ros_catkin_ws/src/spike/src/spike/sons/'
nomWav = 'robot.wav'


def callback(data):
        global soundhandle
        if verbose:
                rospy.loginfo(rospy.get_caller_id() + " Message recu: %i", data.command)
        if data.command == WAV:
            nomWav = data.arg
            rospy.loginfo(rospy.get_caller_id() + "Va produire un son..." + soundAssets + nomWav)
            sh = soundhandle.playWave(soundAssets + nomWav)
            #sh.play()
            rospy.loginfo(rospy.get_caller_id() + "A produit un son...")
        if data.command == SAY:
            entree = data.arg
            rospy.loginfo(rospy.get_caller_id() + "Va parler..." + entree)
            sh = soundhandle.say(entree)
            #sh.play()
            rospy.loginfo(rospy.get_caller_id() + "A parle...")
        rospy.sleep(2)

# On s'inscrit au topic
rospy.Subscriber("/robotsound", SoundRequest, callback)

if mode == modeTest:
        sh = soundhandle.say("Ready!")
        messageSon = SoundRequest()
        topicSon = rospy.Publisher("/robotsound", SoundRequest, queue_size=10)
	while True:
            print "Spike va dire (s pour son) "
            entree = raw_input(">")
            if entree != "s": 
                rospy.loginfo("Spike dit: " + entree)
                messageSon.command = SAY
                messageSon.arg = entree
                topicSon.publish(messageSon)
                print messageSon.command 
                
                #soundhandle.say(entree)
            else:
	    	rospy.loginfo("Joue un son.")
	    	messageSon.command = WAV
                messageSon.arg = nomWav
                topicSon.publish(messageSon)
                print messageSon.command 
		#soundhandle.playWave(soundAssets + nomWav)

# Puisqu'on attend un signal, il ne faut pas quitter
# L'instruction suivante permet de rester dans le programme
rospy.spin()
