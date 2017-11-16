#!/usr/bin/env python
import rospy
import numpy as np
#import time
#import random
from brian2 import *
from std_msgs.msg import String
import matplotlib.pyplot as plt
import matplotlib.animation as animation

rospy.init_node('node_spiking_neural_networks', anonymous=True)
rospy.loginfo("Gestion des reseaux de neurones a decharge.")

verbose = True
frames = []
norm = []
NBFRAMESORIGINAL = 800
ECHANTILLON = 8

NBFRAMES = NBFRAMESORIGINAL / ECHANTILLON

# Ajustement - BUG
NBFRAMES = NBFRAMES - 15
print "NBFRAMES: " + str(NBFRAMES) 
CHUNK = 16

NB_LIGNES = NBFRAMES - 1
NB_COLONNES = CHUNK
N = NB_LIGNES * NB_COLONNES

rospy.set_param("no_frame_SNN", 1)

def plotSignalSonore():
    # Tuto: matplotlib.org/users/beginner.html
    #plt.plot([1,2,3,4])
    plt.plot(frames)
    plt.ylabel('Spectre sonore')
    plt.show()
  
def animate(i):
    line.set_ydata(statemon.v[neurone])
    return line
    
def init():
    line.set_ydata(statemon.v[neurone])
    return line  
  
def plotAnimationVoltTemps(statemon):
    neurone = 0
    fig = plt.plot(statemon.t/ms, statemon.v[neurone])
    
    ani = animation.FuncAnimation(fig, animate, 20, init_func=init, interval=25, blit=False)
    plt.show()
  
def plotVoltTemps(statemon):
    debut = 0
    fin = 1
    title("Voltage en fonction du temps (Neurones de " + str(debut) + " a " + str(fin) + ")")
    for j in range(debut,fin):
        plt.plot(statemon.t/ms, statemon.v[j])
    plt.ylabel('voltage')
    plt.xlabel('Temps m/s')
    plt.show()
    
def plotOutputNeurons(stateOutput):
    debut = 0
    fin = 2
    title("Voltage final des neurones de sortie")
    for j in range(debut,fin):
        plt.plot(stateOutput.t/ms, stateOutput.v[j])
    plt.ylabel('voltage')
    plt.xlabel('Neurones de sortie')
    plt.show()
    

def plotSpikeTemps(spikemon):
    plt.plot(spikemon.t/ms, spikemon.i, '.k')
    plt.ylabel('Spikes')
    plt.xlabel('Temps m/s')
    plt.show()
    
def plotPopulationRate(popratemon):
    plt.plot(popratemon.t/ms, popratemon.rate/Hz)
    plt.xlabel('Temps m/s')
    plt.ylabel('Rate/Hz')
    plt.show()

def plotConnectivity(S):
    Ns = len(S.source)
    Nt = len(S.target)
    figure(figsize=(10,4))
    subplot(121)
    plot(np.zeros(Ns), arange(Ns), 'ok', ms=10)
    plot(np.ones(Nt), arange(Nt), 'ok', ms=10)
    for i,j in zip(S.i, S.j):
        plot([0,1], [i,j], '-k')
    xticks([0,1], ['Source', 'Target'])
    ylabel("Neuron index")
    xlim(-0.1, 1.1)
    ylim(-1, max(Ns, Nt))
    subplot(122)   
    plot(S.i, S.j, 'ok')
    xlim(-1, Ns)
    ylim(-1, Nt)
    xlabel('Source neuron index')
    ylabel('Target neuron index')
    plt.show()

def echantillonFrames():
    print "Echantillons FRAMES"
    print type(norm[5][5])
    print norm[5][5]
    #print type(frames[5])
    #print frames[5]
    print norm


def callbackRecoitDonnees(data):
    no_frame = rospy.get_param("no_frame_SNN")
    decoded = numpy.fromstring(data.data, 'Int16');
    #if verbose:
    #    rospy.loginfo(rospy.get_caller_id() + "Le callback a recu: %s", decoded)
    frames.append(decoded)
    #norm.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    liste=[]
    for i in range(CHUNK):
        liste.append(0)
    norm.append(liste)
    rospy.set_param("no_frame_SNN", no_frame + 1)

def normalize2DVector():
    print "Normalize"
    pluspetit = 99999
    plusgrand = -99999
    for l in range(0, NB_LIGNES-1):
        for c in range(0, NB_COLONNES-1):
            nombre = frames[l][c]
            if nombre < pluspetit:
                pluspetit = nombre
            if nombre > plusgrand:
                plusgrand = nombre
    ecart = plusgrand - pluspetit
    print "plusgrand: %i" % plusgrand
    print "pluspetit: %i" % pluspetit
    print "ecart: %i" % ecart
    for l in range(0, NB_LIGNES-1):
        for c in range(0, NB_COLONNES-1):
            ancien = frames[l][c]
            norm[l][c] = float(float(ancien - pluspetit)) / float(ecart)
            #print "Donnee: %i Donnee normalisee: %.5f" % (ancien, norm[l][c]) 

#def normalize1DVector():
#    norm = [float(i)/max(frames) for i in frames]    
    
@check_units(l=1, c=1, result=0)
def intensite(l, c):
    i = norm[l][c]
    return i

def SNN():
    print "SNN"  

    start_scope()
    
    # Definition des variables 
    print "Nombre de neurones entrees: " + str(N)
    tau = 10*ms
    eqs = '''
    dv/dt = (1 - v) /tau : 1 (unless refractory)
    '''
    
    # Creation du SNN
    # Neurones d'entree
    InputGroup = NeuronGroup(N, eqs, threshold='v> 0.8', reset='v = 0', refractory=5*ms)
    HiddenGroup1 = NeuronGroup(50, eqs, threshold='v> 0.8', reset='v = 0', refractory=5*ms)
    HiddenGroup2 = NeuronGroup(50, eqs, threshold='v> 0.8', reset='v = 0', refractory=5*ms)
    OutputGroup =  NeuronGroup(3, eqs, threshold='v> 0.8', reset='v = 0', refractory=5*ms)

    # Synapses
    global ItoH1
    ItoH1 = Synapses(InputGroup, HiddenGroup1, 'w:1', on_pre='v_post += w')
    ItoH1.connect()
    ItoH1.w = 'j*0.2'

    global H1toH2
    H1toH2 = Synapses(HiddenGroup1, HiddenGroup2, 'w:1', on_pre='v_post += w')
    H1toH2.connect()
    H1toH2.w = 'j*0.2'

    global H2toO
    H2toO = Synapses(HiddenGroup2, OutputGroup, 'w:1', on_pre='v_post += w')
    H2toO.connect()
    H2toO.w = 'j*0.2'

    # Assignation des neurones d'entrees
    for j in range(0,NB_LIGNES-1):
        for k in range(0,NB_COLONNES-1):
            noNeurone = (j*NB_COLONNES) + k
            InputGroup.v[noNeurone] = intensite(j,k)    
            if verbose:
                if noNeurone%100 == 0:
                    print "neurone : " + str(noNeurone) + " voltage: " + str(InputGroup.v[noNeurone])    
    
    # Creation des moniteurs
    #global statemon
    statemon = StateMonitor(InputGroup, 'v', record=0)
    #global stateOutput
    stateOutput = StateMonitor(OutputGroup, 'v', record=True)
    #global spikemon 
    spikemon = SpikeMonitor(HiddenGroup1)
    #global popratemon
    popratemon = PopulationRateMonitor(HiddenGroup1)

    # Execution de la simulation
    run(500*ms, report='text', report_period=1*second)

    # Recuperation des neurones de sorties


    # Envoie du signal sur un topic qui sera lu par l'attention. 


    # Affichage des graphiques 
    if verbose:
        print "Affichage des graphiques..."
    #plotSignalSonore()
    #echantillonFrames()
    #plotVoltTemps(statemon)
    #plotSpikeTemps(spikemon)
    #plotAnimationVoltTemps(statemon)
    #plotConnectivity(S)
    #plotPopulationRate(popratemon)
    plotOutputNeurons(stateOutput)
   


if verbose:
    print("Souscrit au callback...")
rospy.Subscriber("topic_son_ambiant", String, callbackRecoitDonnees)

if verbose:
    print("Boucle sur les frames...")

frame = rospy.get_param("no_frame_SNN")
while frame <= NBFRAMES:
    # Affiche a tous les x frames.     
    frame = rospy.get_param("no_frame_SNN")
    if frame%10 == 0: 
        print "Frame # " + str(frame) + "/" + str(NBFRAMES)

normalize2DVector()
SNN()

