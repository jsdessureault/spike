#!/usr/bin/env python
import roslib
import rospy, os, sys
import time
from std_msgs.msg import Float64, String

rospy.init_node('node_battery', anonymous=True)
rospy.loginfo("Behavior_verifie_batterie")

verbose = True

if verbose:
	rospy.loginfo("Initialisation des topics")

topic_parle = rospy.Publisher('/topic_parle', String, queue_size=10)


def callbackBatterie(data):
	global start_time
	global check_time
	global elapsed_time
	elapsed_time = time.time() - start_time
	#print elapsed_time
	if elapsed_time >= check_time:
		start_time = time.time()
		if verbose:
			rospy.loginfo(rospy.get_caller_id() + " Message recu: %s", str(data.data))
		voltage = data.data
		if voltage <= battery_low_threshold:
			message = "Warning! Battery low! Voltage is " + str(voltage) + " Please charge me!" 
			rospy.loginfo(message)
			topic_parle.publish(message)


start_time = time.time()
check_time = 60.0		# Check battery state every 120 seconds. 
elapsed_time = check_time

battery_low_threshold = 10.5

rospy.Subscriber("/Rosaria/battery_voltage", Float64, callbackBatterie)
rospy.spin()



