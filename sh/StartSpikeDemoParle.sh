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
xterm roscore &
sleep 5
echo "sound_play..."
xterm -e "roslaunch sound_play soundplay_node.launch" &
sleep 5
echo "behavior_parle"
xterm -e "rosrun spike behavior_parle.py" &
sleep 5
echo "parle"
xterm -e "rosrun spike parle.py" &
export DISPLAY=':0'
echo "behavior_humeur"
xterm -e "rosrun spike behavior_humeur.py" &

echo "SPIKE LAUNCHED!"
