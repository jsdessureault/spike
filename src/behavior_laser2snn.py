#!/usr/bin/env python
import roslib
import rospy, os, sys
import time
from std_msgs.msg import Float32
from sensor_msgs.msg import LaserScan

rospy.init_node('node_laser2snn', anonymous=True)
rospy.loginfo("Behavior_laser2snn")

verbose = True

pub = rospy.Publisher('/nearest_value_scan', Float32, queue_size = 10)
	
def callbackInput(data):
    ranges = data.ranges
    # Get to smallest value of the array to find the nearest object.
    # We only take the value of the 1/3 most center of the laser detection. 
    lenght = len(ranges)
    third = int(lenght / 3)
    smallest = 99.9
    i = third
    while (i < (third * 2)):
        if ranges[i] < smallest:
            smallest = ranges[i]
        i += 1

    if smallest == 99.9:
        smallest = 0.0
    nearest = smallest / data.range_max
    voltage = 1.0 - nearest
    if verbose:
        rospy.loginfo("Smallest dist.: " + str(smallest) + "range_max: " + str(data.range_max) + " Norm.: " + str(nearest) + " Volt " + str(voltage))

    pub.publish(voltage)

 
rospy.Subscriber("/scan", LaserScan, callbackInput)

if verbose:
    rospy.loginfo("Waiting for commands...")	

rospy.spin()
