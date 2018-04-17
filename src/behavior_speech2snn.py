#!/usr/bin/env python
import roslib
import rospy, os, sys
import time
import aiml
from std_msgs.msg import String, Float32MultiArray

rospy.init_node('node_speech2snn', anonymous=True)
rospy.loginfo("Behavior_speech2snn")

verbose = True

pub = rospy.Publisher('/command_snn', Float32MultiArray, queue_size = 10)
	
def callbackInput(data):
    command = data.data
    if verbose:
        rospy.loginfo(rospy.get_caller_id() + " Message received: %s", command)

    forward = 0.0
    left = 0.0
    right = 0.0
    stop = 0.0
    valid_command = False
    
    if command == "forward":
        forward = 1.0
        valid_command = True
    if command == "backward":
        backward = 1.0
        valid_command = True
    if command == "left":
        left = 1.0
        valid_command = True
    if command == "right":
        right = 1.0
        valid_command = True
    if command == "stop":
        stop = 1.0
        valid_command = True
    if valid_command:
        rospy.loginfo("Valid command detected!")
        cmd = []
        cmd.append(forward)
        cmd.append(stop)
        cmd.append(left)
        cmd.append(right)
        f32ma = Float32MultiArray()
        f32ma.data = cmd
        pub.publish(f32ma)

 
rospy.Subscriber("/speech_recognition", String, callbackInput)

if verbose:
    rospy.loginfo("Waiting for commands...")	

rospy.spin()
