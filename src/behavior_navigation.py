#!/usr/bin/env python
import sys
import rospy
import time
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import String, Float32
from sensor_msgs.msg import Joy


rospy.init_node('behavior_navigate', anonymous=True)
rospy.loginfo("Behavior_navigate")


SNNname = "spike"

pub = rospy.Publisher('/Rosaria/cmd_vel', Twist, queue_size = 10)
#goal = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size = 10)

#rate = rospy.Rate(5) # hz
msg = Twist()
msg.linear.x = 0.0
msg.linear.y = 0.0
msg.linear.z = 0.0
msg.angular.x = 0.0
msg.angular.y = 0.0
msg.angular.z = 0.0

#global a, b
#a = PoseStamped()
#b = PoseStamped()

linear = 0.0
angular = 0.0
linear_speed = 0.0
linear_speed_limit = 1.0
angular_speed = 0.15

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def callbackForward(data):
    global linear, angular 
    if data.data != 0.0:
        print("Forward: " + str(data.data))
        linear = 1.0
        angular = 0.0
    

def callbackStop(data):
    global linear, angular 
    if data.data != 0.0:
        print("Stop: "  + str(data.data))
        linear = 0.0
        angular = 0.0

def callbackLeft(data):
    global linear, angular 
    if data.data != 0.0:
        print("Left: "  + str(data.data))
        #linear = 0.0
        angular = 1.0

def callbackRight(data):
    global linear, angular     
    if data.data != 0.0:
        print("Right: " + str(data.data))
        #linear = 0.0
        angular = -1.0

def callbackLaser(data):
    global linear, angular     
    if data.data != 0.0:
        print("Laser: " + str(data.data))
        linear = 0.0
        angular = 0.0
        
def callbackNearestValueScan(data):
    global linear_speed     
    if data.data != 0.0:
        #print("NearestValueScan: " + str(data.data))
        linear_speed = 1.0 - data.data

def speed_graph(speed):
    speed2 = speed
    while speed >= 0.0:
        sys.stdout.write("*")
        speed -= 0.01
    print " " + str(speed2)
    
rospy.Subscriber("/motor_spikes_"+SNNname+"1", Float32, callbackForward)
rospy.Subscriber("/motor_spikes_"+SNNname+"2", Float32, callbackStop)
rospy.Subscriber("/motor_spikes_"+SNNname+"3", Float32, callbackLeft)
rospy.Subscriber("/motor_spikes_"+SNNname+"4", Float32, callbackRight)
rospy.Subscriber("/motor_spikes_"+SNNname+"5", Float32, callbackLaser)
rospy.Subscriber("/nearest_value_scan", Float32, callbackNearestValueScan)

r = rospy.Rate(5)
while not rospy.is_shutdown():
#    if linear_speed >= 1.0:
#        linear_speed = 0
    speed = clamp(linear_speed * linear , 0, linear_speed_limit)
    speed_graph(speed)
    msg.linear.x = speed
    msg.angular.z = angular * angular_speed
    pub.publish(msg)
    r.sleep()
    
    
