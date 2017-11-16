# Tue les processus de SPIKE
# Par JS.Dessureault
#
# Notes: 
# Parametres de xterm
#	-e "ligne de commande avec parametres"
# 	& Execute en tache de fond
#	-hold  : ne ferme pas la fenetre apres execution

echo "Killing all previous processes..."
pkill roscore 
pkill python  
pkill roslaunch
pkill xterm
echo "Processes killed."
