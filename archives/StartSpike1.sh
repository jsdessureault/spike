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
sleep 3
echo "behavior_speak"
rosrun spike behavior_speak.py &
sleep 3
echo "behavior_chatbot"
rosrun spike behavior_chatbot.py &
sleep 3
echo "behavior_speech_recog"
rosrun spike behavior_speech_recog.py &

#export DISPLAY=':0'
#echo "behavior_humeur"
#rosrun spike behavior_mood.py &

echo "SPIKE LAUNCHED!"
