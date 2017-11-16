#!/usr/bin/env python
import rospy
import numpy as np
from brian2 import *
from std_msgs.msg import String
import matplotlib.pyplot as plt
import time
from graphics import plotVoltTemps, plotOutputNeurons, plotSpikeTemps, plotPopulationRate, plotConnectivity, displaySpikeMonitorInfo

rospy.init_node('node_spiking_neural_networks', anonymous=True)
rospy.loginfo("Behavior SNN - Spiking Neural Network")

# Retriving parameters from launcher
SNNname = rospy.get_param("/SNN/SNNname")
verbose = rospy.get_param("/SNN/verbose")  
mode = rospy.get_param("/SNN/mode")
input_neurons = rospy.get_param("/SNN/input_neurons")
output_neurons = rospy.get_param("/SNN/output_neurons")
hidden_neurons = rospy.get_param("/SNN/hidden_neurons")
hidden_layers = rospy.get_param("/SNN/hidden_layers")
synapse_weight = str(rospy.get_param("/SNN/synapse_weight"))
tau = rospy.get_param("/SNN/tau") * ms
threshold_value = rospy.get_param("/SNN/threshold")
refractory_value = rospy.get_param("/SNN/refractory") * ms
reset_value = rospy.get_param("/SNN/reset")
simulation_lenght = rospy.get_param("/SNN/simulation_lenght") * ms
equation = rospy.get_param("/SNN/equation")
graph = rospy.get_param("/SNN/graph")
pathSNN = rospy.get_param("/SNN/path")
 
# Displaying parameters
rospy.loginfo("Reception des parametres:")
rospy.loginfo("SNNname:" + SNNname)
rospy.loginfo("verbose:" + str(verbose))
rospy.loginfo("mode:" + str(mode))
rospy.loginfo("graph:" + str(graph))
rospy.loginfo("input_neurons:" + str(input_neurons))
rospy.loginfo("output_neurons:" + str(output_neurons))
rospy.loginfo("hidden_neurons:" + str(hidden_neurons))
rospy.loginfo("hidden_layers:" + str(hidden_layers))
rospy.loginfo("synapse_weight" + synapse_weight)
rospy.loginfo("tau:" + str(tau))
rospy.loginfo("threshold:" + str(threshold_value))
rospy.loginfo("refractory:" + str(refractory_value))
rospy.loginfo("simulation_lenght:" + str(simulation_lenght))
rospy.loginfo("equation:" + equation)
rospy.loginfo("path:" + pathSNN)

# Filenames and path where the trained SNN will be saved. 
initFile = SNNname + "_initialized"
learnedFile = SNNname + "_learned"

# Mode
LEARNING = 0
RUN = 1

frames_in = []

topic_out_SNN = rospy.Publisher('topic_out_SNN_'+SNNname, String, queue_size=100)

def callbackRecoitDonnees(data):
    #rospy.loginfo("Le callback a recu: %s", data.data)
    frames_in.append(float(data.data))
    #decoded = numpy.fromstring(data.data, 'Int16');
    #if verbose:
    #    rospy.loginfo("Le callback a recu: %s", decoded)
    #del frames_in[:] 
    #for i in range(0,input_neurons): 
        #print "i et decoded de i: " + str(i) + " " + str(decoded[i])
        #frames_in.append(decoded[i])
    #    frames_in.append(data.data[i])

def SNN():

    if verbose and mode == LEARNING:
        rospy.loginfo("SNN Training mode")
    if verbose and mode == RUN:
        rospy.loginfo("SNN execution mode")
        
    start_scope()
    
    # Definition des variables 
    if verbose:
        rospy.loginfo("Creating SNN...")
    
    # SNN Creation
    InputGroup = NeuronGroup(input_neurons, equation, threshold=threshold_value, reset=reset_value, refractory=refractory_value)
    # Va rester a boucler sur le number_layers    
    HiddenGroup1 = NeuronGroup(hidden_neurons, equation, threshold=threshold_value, reset=reset_value, refractory=refractory_value)
    OutputGroup =  NeuronGroup(output_neurons, equation, threshold=threshold_value, reset=reset_value, refractory=refractory_value)

    # Synapses
    postsynaptic = "v_post += " + synapse_weight
    global ItoH1
    ItoH1 = Synapses(InputGroup, HiddenGroup1, on_pre=postsynaptic)
    ItoH1.connect()
    
    global H1toO
    H1toO = Synapses(InputGroup, HiddenGroup1, on_pre=postsynaptic)
    H1toO.connect()
        
    if mode == LEARNING:
        if verbose:
            rospy.loginfo("Saving learned SNN...")
        store(initFile, pathSNN+initFile+".dat")
    if mode == RUN:
        if verbose:
            rospy.loginfo("Restoring previously learned SNN...")
        restore(learnedFile, pathSNN+learnedFile+".dat")
    
    if graph == True:
        stateInput = StateMonitor(InputGroup, 'v', record=True)
        stateOutput = StateMonitor(OutputGroup, 'v', record=True)
        spikeMonitor = SpikeMonitor(OutputGroup)
        popRateMonitor = PopulationRateMonitor(HiddenGroup1)

    theExit = False
    while not theExit: 
        rospy.loginfo("BEGINNING OF CYCLE")
        start = time.time()
        time.clock()
        
        # Utile ave ROSBAG
        #if mode == LEARNING:
        #    rospy.loginfo("YOU HAVE 10 SECONDS TO PLAY THE ROSBAG FILE...") 
        #    rospy.sleep(10)
        #    rospy.loginfo("LEARNING...")
        
        frames_assignation = frames_in
        if len(frames_assignation) >= input_neurons:  
            del frames_in[:]   
            # Assignation des neurones d'entrees
            if verbose:
                rospy.loginfo("Assigning input neurons...")
            
            for i in range(0,input_neurons-1): 
                #print "Neuron no: " + str(i)
                #print "len de inputGroup " + str(len(InputGroup))
                #print "len de assignation " + str(len(frames_assignation))
                if i < len(frames_assignation):
                    if mode == LEARNING:
                        InputGroup.v[i] = frames_assignation[i]
                    if mode == RUN:
                        InputGroup.v[i] = frames_assignation[i] 
                if verbose:
                    rospy.loginfo("neurone : " + str(i) + " voltage: " + str(InputGroup.v[i]))  
                
            # Execution de la simulation
            if verbose:
                rospy.loginfo("Simulation execution...")   
        
            if verbose:
                run(simulation_lenght, report='text', report_period=1*second)
            else:
                run(simulation_lenght)
        
            if mode == LEARNING:
                if verbose:
                    rospy.loginfo("Saving SNN after training...")  
                store(learnedFile, pathSNN+learnedFile+".dat")        
 
            if mode == RUN:        
                
                # Send output_neurons on topics
                if verbose:
                    rospy.loginfo("Send the result to the topic...")
            
                #del frames_out[:] 
                frames_out = ""
                
                for i in range(0,output_neurons):
                    #frames_out.append(numpy.arange(OutputGroup.v[i], dtype=float32))
                    frames_out = frames_out + " " + str(OutputGroup.v[i])
                if verbose:
                    rospy.loginfo("Output neuron before publish: " + frames_out)
                # Send on topic
                topic_out_SNN.publish(frames_out)


        if graph == True:
            # Affichage des graphiques 
            if verbose:
                rospy.loginfo("Affichage des graphiques...")
            plotVoltTemps(stateInput, 0, input_neurons)
            plotSpikeTemps(spikeMonitor)
            #plotConnectivity(ItoH1)
            plotPopulationRate(popRateMonitor)
            plotOutputNeurons(stateOutput, 0, output_neurons)
            displaySpikeMonitorInfo(spikeMonitor)
            profiling_summary(show=5)
            theExit = True

        rospy.loginfo("END OF CYCLE")
        elapsed = time.time() - start
        print "cycle: %.2f" % (elapsed)

if verbose:
    print("Subscribe and registre to the callbacks...")
    
rospy.Subscriber("topic_in_SNN_"+SNNname, String, callbackRecoitDonnees)


SNN()

