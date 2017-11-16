#!/usr/bin/env python
import rospy
import pyaudio
import numpy
import matplotlib.pyplot as plt
import time
import rospy
from std_msgs.msg import String
    

# Plusieurs exemples d'utilisation du son et pyaudio ici:
# www.programcreek.com/python/example/52624/pyaudio.PyAudio

# Initialisation des constantes
ROSBAG = 0
ROS = 1
TEST = 2

verbose = rospy.get_param("/Listen/verbose") 
graph = rospy.get_param("/Listen/graph")
mode = rospy.get_param("/Listen/mode")
pformat = rospy.get_param("/Listen/format")
pchannels = rospy.get_param("/Listen/channels")
prate = rospy.get_param("/Listen/rate")
pchunk = rospy.get_param("/Listen/chunk")
pframes = rospy.get_param("/Listen/frames")
sampling = rospy.get_param("/Listen/sampling") 
rospy_rate = rospy.get_param("/Listen/rospy_rate") 

# Displaying parameters to console
rospy.loginfo("Parameters received from launcher:")
rospy.loginfo("verbose:" + str(verbose))
rospy.loginfo("graph:" + str(graph))
rospy.loginfo("mode:" + str(mode))
rospy.loginfo("format:" + str(pformat))
rospy.loginfo("channels:" + str(pchannels))
rospy.loginfo("rate:" + str(prate))
rospy.loginfo("chunk:" + str(pchunk))
rospy.loginfo("frames:" + str(pframes))
rospy.loginfo("sampling:" + str(sampling))
rospy.loginfo("rospy_rate:" + str(rospy_rate))

# Anciennes valeurs - conserver un bout de temps...
# Constanstes enregistrement 
# Format Entier 16 bits
# FORMAT = pyaudio.paInt16
# 1 seul canal pour mono, 2 pour stereo
# CHANNELS = 1
# Frequence de 44100 ou 16000
# RATE = 44100
# Nombre de frames lus par buffer (1024)
# CHUNK = 1000   # 50
# RECORD_SECONDS = 3
# Nombre de frames a lire (800)
# NOFFRAMES = 5000   
# Pour ne prendre qu'une partie des donnees.  Permet d'alleger les donnees.
# ECHANTILLON = 1   # On capture une valeur tous les x frames. (8)
 
rospy.init_node('node_listen', anonymous=True)
rospy.loginfo("Behavior_listen")

if mode == ROS or mode == ROSBAG:
    topic_listen = rospy.Publisher('listen', String, queue_size=100)

frames = []

def cycleRecording():
      
    rospy.loginfo("BEGINNING OF CYCLE")
    start = time.time()
    time.clock()
        
    audio = pyaudio.PyAudio()
        
    # start Recording
    stream = audio.open(format=pformat, channels=pchannels,
                    rate=prate, input=True,
                    frames_per_buffer=pchunk)
    if verbose:
        rospy.loginfo("Recording...")
      
    #print "Type of frames is " + str(type(frames))

    r = rospy.Rate(rospy_rate) #  hz
    for i in range(0, pframes):
        data = stream.read(pchunk)
        # Si on est en mode ROS, on publie!    
        decoded = numpy.fromstring(data, 'Int16')
        # Trouve la moyenne des sons lus. 
        somme = 0.0
        for j in range(0, pchunk):
            somme = somme + decoded[j]
        moyenne = somme / pchunk
        #for j in range(0, len(decoded)):
        	#print str(moyenne)
        if mode == ROS or mode == ROSBAG:
            tmp = float(moyenne) # + float(100)  #float(32768.0)  
            normalized = abs(tmp /  float (200))  #float(65535.0)
            if normalized > 1.0:
                normalized = 1.0
            if normalized < 0.0:
                normalized = 0.0
            #normalized = 1 - normlalized
            #normalized = normalized * 1.5
            #print str(i) + " decoded: " + str(float(moyenne)) + " normalized: " + str(float(normalized))
            if normalized != 0.0:
                topic_listen.publish(str(float(normalized)))  
            if verbose:    
                printIntensite(normalized)
        if mode == ROSBAG or mode == TEST:            
            frames.append(decoded)
        r.sleep()
   
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    rospy.loginfo("END OF CYCLE")
    elapsed = time.time() - start
    print "cycle: %.2f" % (elapsed)

def printIntensite(intensite):
    strToDisplay = ""
    while intensite > 0:
        strToDisplay = strToDisplay + "#"
        intensite = intensite - 0.02   
    print strToDisplay


def printAfterRecord():
    if printAfterRecord:
        if mode == 1:     
            print "Affichage des frames lus."
            for i in range(len(frames)):
                print frames
        if mode == 2:
            print "Sommaire"
            print "Nombre de frames: " + str(len(frames))
            print "Dernier frame:"
            print frames[len(frames)-1]

def plotAfterRecord():
    # Convertir ce bout de code pour matplotlib (pour executer en ROS.)
    if plotAfterRecord:
        plt.plot(frames)
        plt.ylabel('Signal sonore')
        plt.xlabel('Frame #')
        plt.show()

if mode == ROS:
    print "MODE ROS"
    while True:
        cycleRecording()

if mode == TEST:
    print "MODE TEST"    
    while True:
        cycleRecording()
        printAfterRecord()       
        plotAfterRecord()
    
if mode == ROSBAG:
    print "MODE ROSBAG"
    cycleRecording()
    printAfterRecord()
    plotAfterRecord()    
  
