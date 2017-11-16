#!/usr/bin/env python

'''
Filename: SNN.py
Author: Jean-Sebastien Dessureault
Date created: 01/06/2016
Python version 2.7
'''

import rospy
import numpy as np
from brian2 import *
from std_msgs.msg import String
import matplotlib.pyplot as plt
import time
import pickle
from graphics import plotVoltTemps, plotSpikeTemps, plotPopulationRate, plotConnectivity

# Registering node to ROS
rospy.init_node('node_spiking_neural_networks', anonymous=True)
rospy.loginfo("Behavior SNN - Spiking Neural Network")

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
tau = rospy.get_param("/SNN/tau") * ms
threshold_value = rospy.get_param("/SNN/threshold")
refractory_value = rospy.get_param("/SNN/refractory") * ms
reset_value = rospy.get_param("/SNN/reset")
simulation_lenght = rospy.get_param("/SNN/simulation_lenght") * ms
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
rospy.loginfo("tau:" + str(tau))
rospy.loginfo("threshold:" + str(threshold_value))
rospy.loginfo("refractory:" + str(refractory_value))
rospy.loginfo("simulation_lenght:" + str(simulation_lenght))
rospy.loginfo("path:" + pathSNN)

# Filenames and path where the trained SNN and pickle files will be saved. 
initFile = SNNname + "_initialized"
learnedFile = SNNname + "_learned"

# Mode
LEARNING = 0
RUN = 1

# Global variable that receives the frames from the topic.
frames_in = []

# Callback triggered when there is a new message on the topic.
def callbackReceiveMsgFromTopic(data):
    #rospy.loginfo("Le callback a recu: %s", data.data)
    valeur = float(data.data) 
    #print "Recu: " + data.data + " Conversation: " + str(valeur) 

    #if data.data != 1.0:
    frames_in.append(valeur)

def displaySpikeMonitorInfo(spikeMonitor):
    rospy.loginfo("Total motor neuron spikes: " + str(spikeMonitor.num_spikes))

    
def SNN():

    if verbose and mode == LEARNING:
        rospy.loginfo("SNN LEARNING (train) mode")
    if verbose and mode == RUN:
        rospy.loginfo("SNN RUN mode")
        
    start_scope()
    
    # Definition des variables 
    if verbose:
        rospy.loginfo("Creating SNN...")
    
    # SNN Creation    
    neurons = []                # Array of neuronGroup
    synapses = []               # Array of synapses
    SENSORY_LAYER = 0             # input layer index
    MOTOR_LAYER = inter_layers + 2 - 1    # Output layer index:  Hidden layer +  1 input layer + 1 output layer (- 1 because the index starts at 0).
           
    # Creation of the equation
    # LI&F equation p.110 Brian2.pdf
    #equation = '''
    #dv/dt = (v0 - v)/tau : 1 (unless refractory)
    #v0 : 1'''

    equation = '''
    dv/dt = (1 - v)/tau : 1 (unless refractory)
    '''


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
            if stdp == False:
                # Synapse WITHOUT plasticity: constant synaptic weight
                postsynaptic = "v_post += " + synapse_weight    # Synapse weight 
                synapses.append(Synapses(neurons[layer-1], neurons[layer],  on_pre=postsynaptic))  # Fix synaptic weight to the parameter value. 
                #synapses.append(Synapses(neurons[layer-1], neurons[layer], ""))  # Synaptic weight has been change in the training mode
            else:
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
                    ''' , method='linear'))          
            synapses[layer-1].connect() 
            if verbose: 
                rospy.loginfo("Assigning SYNAPSES between layer: " + str(layer-1) + " and layer " + str(layer))
    
    # Creation of the monitors
    stateSensory = StateMonitor(neurons[SENSORY_LAYER], 'v', record=True)
    if inter_neurons > 0:
        stateInter = StateMonitor(neurons[SENSORY_LAYER + 1], 'v', record=True)
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

    # Main loop.  Inifite if RUN mode.   Quit after X iteration if LEARNING mode. 
    theExit = False
    while not theExit: 
        # Start the cycle and the timer.
        rospy.loginfo("BEGINNING OF CYCLE")
        start = time.time()
        time.clock()
        
        # If RUN mode, restore the learned SNN. 
        if mode == RUN:
            if verbose:
                rospy.loginfo("Restoring previously learned SNN...")
            net.restore(learnedFile, pathSNN+learnedFile+".dat")
        
        # When the callback function has received all the input neurons, assign those neurons to the input layer. 
        frames_assignation = frames_in

        if len(frames_assignation) >= sensory_neurons:    
            if verbose:
                rospy.loginfo("Assigning sensory neurons...")
            
            for i in range(0,sensory_neurons): 
                neurons[SENSORY_LAYER].v[i] = frames_assignation[i]  # Only v of the first simulation
                if verbose:
                    rospy.loginfo("neuron : " + str(i) + " voltage: " + str(neurons[SENSORY_LAYER].v[i]))  

            # Simulation execution
            if verbose:
                rospy.loginfo("Simulation execution...")   
            if verbose:
                net.run(simulation_lenght, report='text', report_period=0.2*second)
            else:
                net.run(simulation_lenght)
                
            del frames_in[:] 
            # If LEARNING mode, store the learned SNN in a file.  
            if mode == LEARNING:
                # If it was the last train data, then exit. 
                global nb_learn
                nb_learn = nb_learn - 1
                if nb_learn == 0:
                    theExit = True       

            # If RUN mode, send the data to some pickle files
            if mode == RUN:
                # Send output_neurons on topics
                if verbose:
                    rospy.loginfo("Send the result to the topic...")              
                pickleOutput_v = open(pathSNN+learnedFile+"_v.pk1", 'wb')
                pickleOutput_t = open(pathSNN+learnedFile+"_t.pk1", 'wb')
                # Send the voltage and time of the output state monitor. (contains spikes)
                pickle.dump(stateMotor.v, pickleOutput_v)
                pickle.dump(stateMotor.t/ms, pickleOutput_t)
                pickleOutput_v.close()
                pickleOutput_t.close()
                
                # Publish on the output topic
                topic_output_spike.publish(str(spikeMonitor.num_spikes))
                
            # Display some basic information to the console. 
            displaySpikeMonitorInfo(spikeMonitor)

        # If we asked for a graph, then exit afterward. 
        if graph == True:
            theExit = True

        # End of the cycle
        rospy.loginfo("END OF CYCLE")
        elapsed = time.time() - start
        txt = "Cycle time: %.2f" % (elapsed)
        rospy.loginfo(txt)
 
        # Show the graphics
        if graph == True:
            if verbose:
                rospy.loginfo("Display graphics...")
            plotVoltTemps(stateSensory, "Sensory neurons potential difference", 0, sensory_neurons)
            if inter_neurons > 0:
                plotVoltTemps(stateInter, "Inter neurons potential difference",0, inter_neurons)
            plotVoltTemps(stateMotor, "Motor neurons potential difference",0, motor_neurons)
            plotSpikeTemps(spikeMonitor, "Motor neurons spikes")
            #Uncomment for connectivity
            #for k in range (0, len(synapses)):
            #    plotConnectivity(synapses[k])
          

    # If LEARNING mode, store the learned SNN in a file.  
    if mode == LEARNING:
        if verbose:
            rospy.loginfo("Saving SNN after training...")  
        net.store(learnedFile, pathSNN+learnedFile+".dat") 

if verbose:
    rospy.loginfo("Subscribe to the callbacks (input neurons)...")
rospy.Subscriber("topic_in_SNN_"+SNNname, String, callbackReceiveMsgFromTopic)
topic_output_spike = rospy.Publisher('topic_out_SNN_'+SNNname, String, queue_size=10)

# Call the SNN system
SNN()

