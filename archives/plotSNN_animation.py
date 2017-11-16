#!/usr/bin/env python
import rospy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from std_msgs.msg import Float32

rospy.init_node("node_plotSNN_animation", anonymous=True)
rospy.loginfo("plotSNN_animation")


volts = []
times = []
iTime = 0

fig1 = plt.figure()
l, = plt.plot(volts, 'r')
plt.ylim(-0.2, 1.2)
plt.xlim(0,1000)

def callbackVolts(data):
	global iTime
	#if len(volts) % 100 == 0:
	#	rospy.loginfo("Callback: " + str(iTime) + " " + str(len(volts)))
	#print data.data
	rospy.loginfo("iTimes, lenght of times and volts : " + str(iTime) + " " + str(len(times)) + " " + str(len(volts)))
	if iTime >= 1000:	
		del times[:]
		del volts[:]
		iTime = 0
		plt.clf()
	volts.append(data.data)
	times.append(iTime)
	iTime += 1

topic_motor_1 = rospy.Subscriber('/topic_motor_volt_1', Float32, callbackVolts)

def update_line(num, data, line):
	#rospy.loginfo("Upadate frame: " + str(len(times)) + " " + str(len(volts)))
	line.set_xdata(times)
	line.set_ydata(volts)
	return line,

# Defining animation
# Animation parameters
# - figure to plot
# - update function
# - number of frames to cache
# - interval. Delay between frames in ms. (def: 200)
# - repeat: loop animation
# - blit: quality of the animation
line_ani = animation.FuncAnimation(fig1, update_line, 25, fargs=(volts,l), interval=200, repeat=True, blit=True)
plt.show()

rospy.spin()

