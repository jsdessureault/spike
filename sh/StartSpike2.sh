# Lancement de SPIKE
# Par JS.Dessureault
#
# Notes: 
# Parametres de xterm
#	-e "ligne de commande avec parametres"
# 	& Execute en tache de fond
#	-hold  : ne ferme pas la fenetre apres execution

cd ~/catkin_ws/
echo "LAUNCHING SPIKE..."
echo "roscore..."
roscore &
sleep 5

echo "Kinect..."
roslaunch freenect_launch freenect.launch &
sleep 5

echo "SPIKE LAUNCHED!"
