# Lancement de SPIKE
# Par JS.Dessureault
#
# Notes: 
# Parametres de xterm
#	-e "ligne de commande avec parametres"
# 	& Execute en tache de fond
#	-hold  : ne ferme pas la fenetre apres execution

echo "LAUNCHING SPIKE..."

echo "Kinect..."
roslaunch freenect_launch freenect.launch &
sleep 5

echo "SPIKE LAUNCHED!"
