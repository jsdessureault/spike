#!/usr/bin/env python

import rospy
from std_msgs.msg import String, Float32
import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

rospy.init_node('node_mood', anonymous=True)
rospy.loginfo("behavior_mood")

verbose = True

volts = []
times = []
iTime = 0

# Plot
# Small scree Spike: 1600 X 800
temps_max = 600
img_neutre = mpimg.imread("/home/pi/ros_catkin_ws/src/spike/assets/images/humeurs/humeurNeutre.png")
mpl.rcParams['toolbar'] = 'None'
figsize = mpl.rcParams['figure.figsize']
figsize[0] = 18 #8
figsize[1] = 12 #4.5
mpl.rcParams['figure.figsize'] = figsize

figure, ax = plt.subplots(2, sharex=True)
plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0, hspace=0.0)

line, = ax[0].plot(times,volts)
ax[0].set_ylim(-0.2,1.0)    # mv:  -0.5 a 1
ax[0].set_xlim(0,temps_max)    
ax[0].set_facecolor('black')
ax[1].set_facecolor('black')
ax[1].axis('off')
ax[1].imshow(img_neutre)

def update_line(data):
    #print "update: " + str(len(volts)) + " " + str(len(times))
    line.set_ydata(volts)
    line.set_xdata(times) 
    return line, 

delais=100
ani = animation.FuncAnimation(figure, update_line, interval=delais)
plt.style.use('dark_background')
        
# Publish ready to the chatbot
#topic_attention_conversation.publish("SPIKE_READY")
        
if verbose == True:
    rospy.loginfo("Callback definition")

def callbackMood(data):
    mood_state = data.data
    if verbose == True:
        rospy.loginfo("Mood: %s", mood_state)

def callbackNeurons(data):
    global iTime
    #print "Callback neurons " + str(iTime)
    if iTime >= temps_max:
        del times[:]
        del volts[:]
        iTime = 0
    volts.append(data.data)
    times.append(iTime)
    iTime += 1
    
if verbose == True:
    rospy.loginfo("Subscribers.")

rospy.Subscriber("mood", String, callbackMood)
rospy.Subscriber('/snn_motor_volt_1', Float32, callbackNeurons)

if verbose == True:
    rospy.loginfo("Spin...")

plt.show()

rospy.spin()
