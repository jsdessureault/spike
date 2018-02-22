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
    smallest = 99.9
    i = 0
    while (i < len(ranges)):
        if ranges[i] < smallest:
            smallest = ranges[i]
        i += 1

    nearest = smallest / data.range_max
    if verbose:
        rospy.loginfo(rospy.get_caller_id() + " Smallest distance: " + str(smallest) + " Normalized: " + str(nearest))
    pub.publish(nearest)

 
rospy.Subscriber("/scan", LaserScan, callbackInput)

if verbose:
    rospy.loginfo("Waiting for commands...")	

rospy.spin()