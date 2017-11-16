#!/usr/bin/env python

import rospy, numpy, math
#import pygtk
#pygtk.require('2.0')
#from mpltools import style 
import gtk

from std_msgs.msg import String, Float32
from matplotlib.backends.backend_gtkagg import FigureCanvasGTK as FigureCanvas
import matplotlib
from matplotlib.figure import Figure
from numpy import arange, sin, pi
import matplotlib.animation as animation
import matplotlib.pyplot as plt
#import pickle
#matplotlib.use('TkAgg')

rospy.init_node('node_humeur', anonymous=True)
rospy.loginfo("behavior_humeur")


class ExpressionFaciale:

    verbose = True

    # Code vient d'ici:  http://www.pygtk.org/pygtk2tutorial/sec-Images.html#idp5575312
    if verbose == True:
        rospy.loginfo("Definition de la classe.")

    volts = []
    times = []
    iTime = 0

    delais = 5000    # va rafraichir toutes les x millisecondes.

    # Plot
    temps_max = 1000
    figure = Figure(figsize=(600,125))
    figure.patch.set_facecolor('black')
    ax = figure.add_subplot(111, facecolor='black')
    line, = ax.plot(times,volts)
    ax.set_ylim(-0.2,1.0)    # mv:  -0.5 a 1
    ax.set_xlim(0,temps_max)    
    ax.set_axis_bgcolor('black')

    etatHumeur = "Neutre"
    etatStatut = "En attente..."

    #envoieSpikePret = True
    # Communication avec Behavior_chatbot
    #topic_attention_conversation = rospy.Publisher('topic_attention_conversation', String, queue_size=10)
        
    # Images et textes 
    imageHumeur = gtk.Image()
    imageFiller = gtk.Image()
    statut = gtk.TextView()
    statut.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('#000000'))
    statut.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#FFFFFF'))
    texte = statut.get_buffer()
    texte.set_text(etatStatut)

    #def update_line(data):
        #line.set_ydata(volts)
        #line.set_xdata(times)
    #    return line, 

    plotCanevas = FigureCanvas(figure) 
 
    #ani = animation.FuncAnimation(figure, update_line, interval=delais)
 
    plt.style.use('dark_background')

    pix_filler = gtk.gdk.PixbufAnimation("/home/ubuntu/catkin_ws/src/spike/src/spike/images/pensees/imageFiller.jpeg")
    imageFiller.set_from_animation(pix_filler)

    pix_humeur_neutre = gtk.gdk.PixbufAnimation("/home/ubuntu/catkin_ws/src/spike/src/spike/images/humeurs/humeurNeutre.png")
    pix_humeur_joyeux = gtk.gdk.PixbufAnimation("/home/ubuntu/catkin_ws/src/spike/src/spike/images/humeurs/humeurJoyeux.png")
    pix_humeur_fatigue = gtk.gdk.PixbufAnimation("/home/ubuntu/catkin_ws/src/spike/src/spike/images/humeurs/humeurFatigue.gif")
    pix_humeur_triste = gtk.gdk.PixbufAnimation("/home/ubuntu/catkin_ws/src/spike/src/spike/images/humeurs/humeurTriste.gif")

    def expression(self, widget, data=None):
        print "Expression faciale"

    def delete_event(self, widget, event, data=None):
        print "La fenetre ExpressionFaciale a ete detruite..."
        return False

    def destroy(self, widget, data=None):
        print "La fenetre ExpressionFaciale a ete detruite..."
        self.main_quit()

    def my_timer(self):

        #if mode == modeTest:
        #    if verbose:
        #        rospy.loginfo("Timer modeTest: Change les etats...")
        #if mode == modeRecoitSignal:
        #    if verbose:
        #        rospy.loginfo("Timer modeRecoitSignal")
        self.rafraichir()

    def rafraichir(self):

        if self.verbose == True:
            rospy.loginfo(" Humeur: " + self.etatHumeur )

        # Execute ce code UNE fois, au debut.  ChatBot - Spike est pret!
        #if self.envoieSpikePret == True:
        #    self.envoieSpikePret = False
        #    if verbose:
        #        rospy.loginfo("Envoie le message que Spike est pret au chatbot.")
        #    self.topic_attention_conversation.publish("SPIKE PRET")

        # On ajuste l'humeur selon l'etat
        #if self.etatHumeur == "Neutre":
        #    self.imageHumeur.set_from_animation(self.pix_humeur_neutre)
        #if self.etatHumeur == "Joyeux":
        #    self.imageHumeur.set_from_animation(self.pix_humeur_joyeux)
        #if self.etatHumeur == "Triste":
        #    self.imageHumeur.set_from_animation(self.pix_humeur_triste)
        #if self.etatHumeur == "Fatigue":
        #    self.imageHumeur.set_from_animation(self.pix_humeur_fatigue)
        #self.imageHumeur.show()

        # mise a jour du message a ecran
        #self.texte.set_text(self.etatStatut)
        #self.statut.set_buffer(self.texte)
        #self.statut.show()
        # On reinitialise pour le prochain rafraichissement
        #self.etatStatut = ""

        # Declaration du timer
        gtk.timeout_add(self.delais, self.my_timer)

        #self.plotCanevas.show()
        
    def __init__(self):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.set_border_width(1)
        self.window.set_title("SPIKE")
    
        self.window.resize(600, 480)
        
        #fixed = gtk.Fixed()
        #fixed.set_size_request(1280, 1024)
        self.imageHumeur.set_from_animation(self.pix_humeur_neutre)
        #self.canevas.put(self.imageReflexion, 0, 0)

        #fixed.put(self.plotCanevas,0,0)
        #fixed.put(self.imageHumeur, 0, 256)
        #fixed.put(self.statut, 100, 50)
        #self.plotCanevas.show()
        #fixed.show()
     
        #self.window.add(self.imageHumeur)
        #self.window.add(self.statut)
        
        #JSD: REACTIVER LES LIGNES COMMENTES POUR AVOIR LES AUTRES ELEMENTS.  MAIS REDUIRE LA TAILLE DU FILLER. 
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.plotCanevas)
        vbox.pack_start(self.imageHumeur, False, False)
        #vbox.pack_start(self.imageFiller, False, False)
        vbox.pack_start(self.statut)

        self.window.add(vbox)
        self.window.show_all()
        self.rafraichir()

    def main(self):

        if self.verbose == True:
            rospy.loginfo("Behavior_humeur: Main")

        if self.verbose == True:
            rospy.loginfo("Definition des callbacks.")

        def callbackHumeur(data):
            expression.etatHumeur = data.data
            if self.verbose == True:
                rospy.loginfo("Humeur: %s", expression.etatHumeur)

        def callbackStatut(data):
            expression.etatStatut = data.data
            if self.verbose == True:
                rospy.loginfo("Statut: %s", expression.etatStatut)

        def callbackNeurones(data):
            print "Callback neurones"
            if self.iTime >= 1000:
                del self.times[:]
                del self.volts[:]
                self.iTime = 0
                plt.clf()
            self.volts.append(data.data)
            self.times.append(self.iTime)
            self.iTime += 1
            
        if self.verbose == True:
            rospy.loginfo("Enregistrement des Subscribers.")

        # On s'inscrit aux topics
        rospy.Subscriber("topic_humeur", String, callbackHumeur)
        rospy.Subscriber("behavior_ecoute/output", String, callbackStatut)
        rospy.Subscriber('/topic_motor_volt_1', Float32, callbackNeurones)

        if self.verbose == True:
            rospy.loginfo("Appel de la definition de l'expression faciale.")
        gtk.main()
        

if __name__ == "__main__":

        expression = ExpressionFaciale()
        expression.main()

