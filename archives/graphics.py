#!/usr/bin/env python
import rospy
import numpy as np
from brian2 import *
import matplotlib.pyplot as plt
      

def plotVoltTemps(statemon, titre, debut, fin):
    title(titre + " (Neurons from " + str(debut) + " to " + str(fin) + ")")
    for j in range(debut,fin):
        plt.plot(statemon.t/ms, statemon.v[j])
    plt.ylabel('Voltage mV')
    plt.xlabel('Temps m/s')
    plt.show()
    
def plotSpikeTemps(spikemon, titre):
    title(titre)
    plt.plot(spikemon.t/ms, spikemon.i, '.k')
    plt.ylabel('Spikes')
    plt.xlabel('Time m/s')
    plt.show()
    
def plotPopulationRate(popratemon):
    title("Spikes Population Rate")
    plt.plot(popratemon.t/ms, popratemon.rate/Hz)
    plt.xlabel('Time m/s')
    plt.ylabel('Rate/Hz')
    plt.show()

def plotConnectivity(S):
    Ns = len(S.source)
    Nt = len(S.target)
    figure(figsize=(10,4))
    #subplot(111)
    plot(np.zeros(Ns), arange(Ns), 'ok', ms=10)
    plot(np.ones(Nt), arange(Nt), 'ok', ms=10)
    for i,j in zip(S.i, S.j):
        plot([0,1], [i,j], '-k')
    xticks([0,1], ['Source', 'Target'])
    ylabel("Neuron index")
    xlim(-0.1, 1.1)
    ylim(-1, max(Ns, Nt))
    title("SNN Architecture Connectivity")
    plt.show()

