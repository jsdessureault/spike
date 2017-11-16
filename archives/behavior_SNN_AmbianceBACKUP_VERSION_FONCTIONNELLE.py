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
rospy.loginfo("Behavior SNN Ambiance")

LEARNING = 0
TEST = 1
mode = TEST

verbose = True
frames = []
norm = []
NBFRAMESORIGINAL = 800
ECHANTILLON = 8

NBFRAMES = NBFRAMESORIGINAL / ECHANTILLON

# Ajustement - BUG
NBFRAMES = NBFRAMES - 20
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
    plt.xlabel('Temps en ms')
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
    
    # PSEUDOCODE
    # Definition des parametres du SNN
    # Definition des couches de neurones et de synapses
    # Creation des moniteurs
    # TANT QUE VRAI
    #   Lecture des paquets (du micro ou du rosbag)
    #   Normalisation des entrees (0 a 1)
    #   Assignation des entres aux neurones d'entres.
    #   Execution de la simulation
    #   SI mode est LEARNING
    #       Store le resultats dans After_learning.dat
    #   SI mode est TEST       
    #       Recuperation des neurones de sorties        
    #       Envoie du signal sur un topic qui sera lu par l'attention. 
    # Affichage des graphiques
   
    if verbose and mode == LEARNING:
        rospy.loginfo("SNN phase entrainement")
    if verbose and mode == TEST:
        rospy.loginfo("SNN phase test")
        
    start_scope()
    
    # Definition des variables 
    if verbose:
        rospy.loginfo("Nb neurones entree: " + str(N))
        rospy.loginfo("Creation du SNN")

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


Mettre les entrees dans les synapses. w.




    # Synapses
    global ItoH1
    ItoH1 = Synapses(InputGroup, HiddenGroup1, 'w:1', on_pre='v_post += w')
    ItoH1.connect(p=0.2)
    ItoH1.w = '0.2'

    global H1toH2
    H1toH2 = Synapses(HiddenGroup1, HiddenGroup2, 'w:1', on_pre='v_post += w')
    H1toH2.connect(p=0.2)
    H1toH2.w = '0.2'

    global H2toO
    H2toO = Synapses(HiddenGroup2, OutputGroup, 'w:1', on_pre='v_post += w')
    H2toO.connect(p=0.2)
    H2toO.w = '0.2'

    # Creation des moniteurs
    if verbose:
        rospy.loginfo("Assignation des moniteurs")    
    statemon = StateMonitor(InputGroup, 'v', record=0)
    stateOutput = StateMonitor(OutputGroup, 'v', record=True)
    spikemon = SpikeMonitor(OutputGroup)
    popratemon = PopulationRateMonitor(HiddenGroup1)
    
    if verbose:
            rospy.loginfo("Stockage du SNN initialise.")
    if mode == LEARNING:
        store("Initialized", "Initialised.dat")
    if mode == TEST:
        restore("After_learning", "After_learning.dat")
    
    while True: 
    
        # Lecture des neurones d'entree
        if verbose:
            rospy.loginfo("En attente frames (live ou rosbag)...")
        rospy.set_param("no_frame_SNN", 1)
        frame = rospy.get_param("no_frame_SNN")
        while frame <= NBFRAMES:
            # Affiche a tous les x frames.     
            frame = rospy.get_param("no_frame_SNN")
            if frame%10 == 0 and verbose: 
                rospy.loginfo("Frame # " + str(frame) + "/" + str(NBFRAMES))
        # Normalisation du vecteur
        normalize2DVector()    
        
        # Assignation des neurones d'entrees
        if verbose:
            rospy.loginfo("Assignation des neurones d'entree.")
        for j in range(0,NB_LIGNES-1):
            for k in range(0,NB_COLONNES-1):
                noNeurone = (j*NB_COLONNES) + k
                InputGroup.v[noNeurone] = intensite(j,k)    
                if verbose:
                    if noNeurone%100 == 0 and verbose:
                        rospy.loginfo("neurone : " + str(noNeurone) + " voltage: " + str(InputGroup.v[noNeurone]))  
    
        # Execution de la simulation
        if verbose:
            rospy.loginfo("Execution de la simulation")   
        duree = 100*ms
        if verbose:
            run(duree, report='text', report_period=1*second)
        else:
            run(duree)
        
        if mode == LEARNING:
            if verbose:
                rospy.loginfo("Storage du SNN apres entrainement.")  
            store('After_learning', "After_learning.dat")        
        
        if mode == TEST:        
        
            # Recuperation des neurones de sorties
            # spikeMonitor.num_spikes: Total des spikes
            # spikeMonitor.count: Total des spikes / par neurones
            # spikeMonitor.count: Total des spikes / pour neurones i
            # spikeMonitor.i: Tableau des spikes enregistres
                
            silencieux = spikemon.count[0]
            calme = spikemon.count[1]
            bruyant = spikemon.count[2] 
            if verbose:
                rospy.loginfo("Recuperation des neurones de sortie.")
                rospy.loginfo("Silencieux: " + str(silencieux))
                rospy.loginfo("Calme: " + str(calme))
                rospy.loginfo("Bruyant: " + str(bruyant))                
        
            # Envoie du signal sur un topic qui sera lu par l'attention. 
            if verbose:
                rospy.loginfo("Envoie du resultat sur le topic")
    
            
        # Affichage des graphiques 
        if verbose:
            rospy.loginfo("Affichage des graphiques si actifs...")
        #plotSignalSonore()
        #echantillonFrames()
        #plotVoltTemps(statemon)
        plotSpikeTemps(spikemon)
        #plotAnimationVoltTemps(statemon)
        #plotConnectivity(S)
        #plotPopulationRate(popratemon)
        #plotOutputNeurons(stateOutput)
   


if verbose:
    print("Souscrit au callback...")
rospy.Subscriber("topic_son_ambiant", String, callbackRecoitDonnees)

SNN()

