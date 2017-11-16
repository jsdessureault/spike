#!/usr/bin/env python
import rospy
from std_msgs.msg import String

rospy.init_node('parle', anonymous=True)
rospy.loginfo("parle en remote")


# On publie a behavior_parle
topic_parle = rospy.Publisher('topic_parle', String, queue_size=10)

def message (texte):
    if texte == "1":
        return "Bonjour!  Je suis Spike le robot. Bienvenue tout le monde au Cegep de Victoriaville.  Je vous souhaite un bon sejour parmis nous!"
    if texte == "2":
        return "Au revoir tout le monde!  Au plaisir de vous revoir bientot!"
    if texte == "3":
        return "Ha ha ha!  C'est drole!"
        


while True:
    entree = raw_input("Spike dit> ")
    if len(entree) >= 0:
        if entree >= "1" and entree <= "9":
            entree = message(entree)  
        rospy.loginfo("Je repete: " + entree)                      
        topic_parle.publish(entree)

rospy.spin()
