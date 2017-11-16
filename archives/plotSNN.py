#!/usr/bin/env python
import rospy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from std_msgs.msg import Float32

rospy.init_node("node_plotSNN", anonymous=True)
rospy.loginfo("plotSNN")

sizePacket = 1000
#iTimes = 0
iVolts = 0

#times = [sizePacket]
volts = [sizePacket]

#def callbackTimes(data):
	#print data.data
#	global iTimes, iVolts
#	iTimes += 1
#	times.append(data.data)
#	if iTimes == sizePacket and iVolts == sizePacket:
#		displayVoltGraph()

def callbackVolts(data):
	print data.data
	global iVolts, iTimes
	iVolts += 1
	volts.append(data.data)
	if iVolts == sizePacket:
		displayVoltGraph()

def displayVoltGraph():
	global times, volts, iTimes, iVolts
	print "volt"
	print volts
	#print "time"
	#print times

#	iTimes = 0
	iVolts = 0
	plt.ylim(0.0, 2.0)
	plt.plot(volts)
	plt.show()

#print "Subscribers"
#rospy.Subscriber('/topic_motor_time_1', Float32, callbackTimes)
rospy.Subscriber('/topic_motor_volt_1', Float32, callbackVolts)

#print "spin"
rospy.spin()

