#!/usr/bin/env python
import roslib
import rospy
import time
import speech_recognition as sr
from std_msgs.msg import String


rospy.init_node('node_Speech_recog', anonymous=True)
rospy.loginfo("Behavior_speech")

verbose = True

modeTest = 1
modeTopic = 2

mode = modeTopic

pub_sp = rospy.Publisher('/speech_recognition', String, queue_size = 10)

while (True):
    
    # Obtain audio from microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        rospy.loginfo("Waiting for a voice...")
        audio = r.listen(source)
    
    # Recognize speech using Google Speech Recognition
    try:
        text = r.recognize_google(audio)
        rospy.loginfo("I've heard: " + text)
        if mode == modeTopic:
            pub_sp.publish(text)
    except sr.UnknownValueError:
        rospy.loginfo("Did not understand...")
    except sr.RequestError as e:
        rospy.loginfo("Could not request results: {0}".format(e))

