#!/usr/bin/env python

'''
Filename: SNN.py
Author: Jean-Sebastien Dessureault
Date created: 01/06/2016
Python version 2.7
'''
from brian2 import *
prefs.codegen.target = "cython"

import rospy
import numpy as np
from std_msgs.msg import String, Float32, Float32MultiArray, Int16
import matplotlib.pyplot as plt
import time
from graphics import plotVoltTemps, plotSpikeTemps, plotPopulationRate, plotConnectivity

# Retriving parameters from launcher
SNNname = rospy.get_param("/SNN/SNNname")
verbose = rospy.get_param("/SNN/verbose") 
stdp = rospy.get_param("/SNN/STDP")  
mode = rospy.get_param("/SNN/mode")
nb_learn = rospy.get_param("/SNN/nb_learn")
sensory_neurons = rospy.get_param("/SNN/sensory_neurons")
motor_neurons = rospy.get_param("/SNN/motor_neurons")
inter_neurons = rospy.get_param("/SNN/inter_neurons")
inter_layers = rospy.get_param("/SNN/inter_layers")
synapse_weight = str(rospy.get_param("/SNN/synapse_weight"))
synapse_delay = str(rospy.get_param("/SNN/synapse_delay"))
synapse_condition = rospy.get_param("/SNN/synapse_condition")
input_drive_current = rospy.get_param("/SNN/input_drive_current")
tau = rospy.get_param("/SNN/tau") * ms
threshold_value = rospy.get_param("/SNN/threshold")
refractory_value = rospy.get_param("/SNN/refractory") * ms
reset_value = rospy.get_param("/SNN/reset")
simulation_lenght_ms = rospy.get_param("/SNN/simulation_lenght") * ms
simulation_lenght_int = rospy.get_param("/SNN/simulation_lenght") 
graph = rospy.get_param("/SNN/graph")
pathSNN = rospy.get_param("/SNN/path")
 
# Displaying parameters to console
rospy.loginfo("Parameters received from launcher:")
rospy.loginfo("SNNname:" + SNNname)
rospy.loginfo("verbose:" + str(verbose))
rospy.loginfo("STDP:" + str(stdp))
rospy.loginfo("mode:" + str(mode))
rospy.loginfo("nb_learn:" + str(nb_learn))
rospy.loginfo("graph:" + str(graph))
rospy.loginfo("sensory_neurons:" + str(sensory_neurons))
rospy.loginfo("motor_neurons:" + str(motor_neurons))
rospy.loginfo("inter_neurons:" + str(inter_neurons))
rospy.loginfo("inter_layers:" + str(inter_layers))
rospy.loginfo("synapse_weight" + synapse_weight)
rospy.loginfo("synapse_delay" + synapse_delay)
rospy.loginfo("synapse_condition" + synapse_delay)
rospy.loginfo("input_drive_current" + str(input_drive_current))
rospy.loginfo("tau:" + str(tau))
rospy.loginfo("threshold:" + str(threshold_value))
rospy.loginfo("refractory:" + str(refractory_value))
rospy.loginfo("simulation_lenght:" + str(simulation_lenght_int))
rospy.loginfo("path:" + pathSNN)

# Registering node to ROS
rospy.init_node('node_spiking_neural_networks_'+SNNname, anonymous=True)
rospy.loginfo("SNN - Spiking Neural Network - " + SNNname)

# Filenames and path where the trained SNN and pickle files will be saved. 
initFile = SNNname + "_initialized"
learnedFile = SNNname + "_learned"

# Mode
LEARNING = 0
RUN = 1

# output topics
topics_motor_volts = []
topics_motor_spikes = []

sensory_count = 0

# Global variable that receives the frames from the topic.
frames_in = [sensory_neurons]
for x in range(0, sensory_neurons):
    frames_in.append(0.0)

# Initialize input frames.
def init_frames_in():
    for x in range(0, sensory_neurons):
        frames_in[x] = 0.0
    global sensory_count
    sensory_count = 0 

# Callback triggered when there is a new message on the topic.
def callbackReceiveMsgFromTopic(data, sensory_nb):
    global sensory_count
    #rospy.loginfo("Received in the callback: neuron: %i  dat: %s", sensory_nb, data.data)
    valeur = float(data.data) 
    if valeur != 0:
        frames_in[sensory_nb] = valeur
    sensory_count = sensory_count + 1

# Display time.  Must be called in the main SNN loop. 
def display_chrono(start, label):        
    elapsed = time.time() - start
    txt = "time: %.2f" % (elapsed)
    rospy.loginfo(label + " " +txt)


# Main SNN function.    
def SNN():

    if verbose and mode == LEARNING:
        rospy.loginfo("SNN LEARNING (train) mode")
    if verbose and mode == RUN:
        rospy.loginfo("SNN RUN mode")
        
    start_scope()
    
    if verbose:
        rospy.loginfo("Creating SNN...")
    
    # SNN Creation    
    neurons = []                # Array of neuronGroup
    synapses = []               # Array of synapses
    SENSORY_LAYER = 0             # input layer index
    MOTOR_LAYER = inter_layers + 2 - 1    # Motor layer index:  inter layer +  1 sensory layer + 1 motor layer (- 1 because the index starts at 0).
           
    # Creation of the equation
    # LI&F equation p.110 Brian2.pdf
    #equation = '''
    #dv/dt = (v0 - v)/tau : 1 (unless refractory)
    #v0 : 1'''

    #equation = "dv/dt = (I - v)/tau : 1 (unless refractory) I = " + input_drive_current + " : 1"
    equation = "dv/dt = (I - v)/tau : 1 (unless refractory) I : 1"

    if verbose: 
        rospy.loginfo("Equation: " + equation)
    
    # Creation of the neurons and synapses structures
    for layer in range(SENSORY_LAYER,MOTOR_LAYER+1): 
        # Neurons
        if layer == SENSORY_LAYER:
            neurons.append(NeuronGroup(sensory_neurons, equation, threshold=threshold_value, reset=reset_value, refractory=refractory_value, method='linear'))
            if verbose: 
                rospy.loginfo("Assigning SENSORY layer: " + str(layer))
        if layer == MOTOR_LAYER: 
            neurons.append(NeuronGroup(motor_neurons, equation, threshold=threshold_value, reset=reset_value, refractory=refractory_value, method='linear'))
            if verbose: 
                rospy.loginfo("Assigning MOTOR layer: " + str(layer))
        if layer < MOTOR_LAYER and layer > SENSORY_LAYER:
            neurons.append(NeuronGroup(inter_neurons, equation, threshold=threshold_value, reset=reset_value, refractory=refractory_value, method='linear'))
            if verbose: 
                rospy.loginfo("Assigning INTER layer: " + str(layer))
        # Synapses
        if layer > SENSORY_LAYER:
            if stdp == True:
                # Synapse WITH plasticity:  synaptic weight changes over the time  
                Apre = float(synapse_weight)
                Apost = -Apre*tau/tau*1.05    # could be a_post = -a_pre*tau_pre/tau_post*1.05   but here, tau_pre = tau_post
                wmax = Apre
                synapses.append(Synapses(neurons[layer-1], neurons[layer],
                    '''
                    w : 1
                    dapre/dt = -apre/tau : 1 (event-driven)
                    dapost/dt = -apost/tau : 1 (event-driven)  
                    ''',
                    on_pre= '''
                    v_post += w
                    apre += Apre
                    w = clip(w+apost, 0, wmax)
                    ''',
                    on_post='''
                    apost += Apost
                    w = clip(w+apre, 0, wmax)
                    ''' , multisynaptic_index = 'synapse_number'))   # method='linear'
            else:
                # Synapse WITHOUT plasticity: constant synaptic weight
                postsynaptic = "v_post += " + synapse_weight    # Synapse weight 
                synapses.append(Synapses(neurons[layer-1], neurons[layer],  on_pre=postsynaptic, multisynaptic_index = 'synapse_number'))  # Fix synaptic weight to the parameter value. 
                #synapses.append(Synapses(neurons[layer-1], neurons[layer], ""))  # Synaptic weight has been change in the training mode

            # A delay is defined to better visualize graphics (no line overlapping).      
            #synapses[layer-1].delay = 'synapse_number*'+synapse_delay+'*ms'
            # Connextion type between layers.
            if synapse_condition != "":
                synapses[layer-1].connect(condition=synapse_condition) 
            else:
                synapses[layer-1].connect() 
            if verbose: 
                rospy.loginfo("Assigning SYNAPSES between layer: " + str(layer-1) + " and layer " + str(layer))

    # Declaring the monitors        
    stateMotor = StateMonitor(neurons[MOTOR_LAYER], 'v', record=True)
    spikeMonitor = SpikeMonitor(neurons[MOTOR_LAYER])
            
    # Integrtion of each component in the network. 
    if verbose: 
        rospy.loginfo("Integration of each component in the network.")
    net = Network(collect())
    net.add(neurons)
    net.add(synapses)
    
    # Save the state if LEARNING mode. 
    if mode == LEARNING:
        if verbose:
            rospy.loginfo("Saving initialized SNN...")
        net.store(initFile, pathSNN+initFile+".dat")

    # If RUN mode, restore the learned SNN. 
    if mode == RUN:
        if verbose:
            rospy.loginfo("Restoring previously learned SNN...")
        net.restore(learnedFile, pathSNN+learnedFile+".dat")
        # Keep this initial state in memory.  Restore() after each simulation. 
        net.store("current")

    init_frames_in()
    
    # Main loop.  Inifite if RUN mode.   Quit after X iteration if LEARNING mode. 
    theExit = False
    while not theExit: 
        # Start the cycle and the timer.
        start = time.time()
        time.clock()
        if verbose:
            display_chrono(start, "BEGIN CYCLE")

        # Restore initial SNN and monitors
        if mode==RUN:
            net.restore("current")
        
        # When the callback function has received all the input neurons, assign those neurons to the input layer. 
        frames_assignation = frames_in
        #rospy.loginfo("Assigned sensories: " + str(frames_assignation))
        global sensory_count
        rospy.loginfo("Sensory count: " + str(sensory_count))

        # Assing sensory neurons from frames              
        for k in range(0,sensory_neurons): 
            neurons[SENSORY_LAYER].v[k] = frames_assignation[k]   # Only v of the sensory neurons
            neurons[SENSORY_LAYER].I[k] = input_drive_current 
            rospy.loginfo("neuron " + str(k) + " v. " + str(neurons[SENSORY_LAYER].v[k])) 
        init_frames_in()

        # Simulation execution
        net.run(simulation_lenght_ms)
                      
        # If LEARNING mode, store the learned SNN in a file.  
        if mode == LEARNING:
            # If it was the last train data, then exit. 
            global nb_learn
            nb_learn = nb_learn - 1
            if nb_learn == 0:
                theExit = True       

        # If RUN mode, send the results to the topics
        if mode == RUN:
            # Publish on the output topic
            for y in range(0, motor_neurons):
                rospy.loginfo("Values to publish for neuron " + str(y) + " : " + str(len(stateMotor.v[y])))
                rospy.loginfo("Number of spikes: " + str(spikeMonitor.num_spikes))
                # publish volts
                voltsToPublish = Float32MultiArray()
                voltsToPublish.data = stateMotor.v[y]
                topics_motor_volts[y].publish(voltsToPublish) 
                # publish spikes    
                nb_spikes = sum(spikeNo == y for spikeNo in spikeMonitor.i)
                topics_motor_spikes[y].publish(nb_spikes)
            topic_simulation_lenght.publish(simulation_lenght_int)
            rospy.loginfo("Transmitted voltage values: "  + str(len(stateMotor.v[0])))

        # If we asked for a graph, then exit after this iteration. 
        if graph == True:
            theExit = True

        # End of the cycle
        display_chrono(start, "END OF CYCLE")    
        rospy.loginfo("-----------")

    # If LEARNING mode, store the learned SNN in a file.  
    if mode == LEARNING:
        if verbose:
            rospy.loginfo("Saving SNN after training...")  
        net.store(learnedFile, pathSNN+learnedFile+".dat") 
        if verbose:
            rospy.loginfo("SNN saved! Exiting application...")  

if verbose:
    rospy.loginfo("Subscribe to the callbacks (input neurons)...")
for k in range(0, sensory_neurons):
    rospy.Subscriber("topic_in_SNN_"+SNNname+"_"+str(k+1), String, callbackReceiveMsgFromTopic, k)
for k in range(0, motor_neurons):
    topics_motor_volts.append(rospy.Publisher('topic_motor_volts_'+SNNname+str(k+1), Float32MultiArray, queue_size=1))
    topics_motor_spikes.append(rospy.Publisher('topic_motor_spikes_'+SNNname+str(k+1), Float32, queue_size=1))
topic_simulation_lenght = rospy.Publisher('topic_simulation_lenght_'+SNNname, Int16, queue_size=1)
# Call the SNN system
SNN()

