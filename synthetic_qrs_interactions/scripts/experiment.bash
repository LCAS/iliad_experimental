#!/bin/bash

SCENARIO=${1:-1}
startTime=${2:-8}
endTime=${3:-16}
#TODO
ROS_WORKSPACE=${4:-$HOME"/workspace/iliad_ws/"}

HERE=`pwd`

BASE_SCENARIO_NAME="ncfm-qsr-sim"
COORDINATOR_TMULE_SCRIPT="iliad-coordinator.yaml"
ROBOT_TMULE_SCRIPT="iliad-robot.yaml"

robot_id="4"
prefix="robot"$robot_id

# derived args:
source $ROS_WORKSPACE"devel/setup.bash"
BASE_SCENARIO_SH_FILE=`rospack find iliad_launch_system`"/tmule/"$BASE_SCENARIO_NAME".sh"
worldFileName=`rospack find iliad_base_simulation`"/worlds/ncfm_model_1_actor_scenario-"$SCENARIO".world"

bag_file_code="S"$SCENARIO"-i"$startTime"-e"$endTime

case $SCENARIO in
1)
  session_name="Robot crossess left of human."
  ;;
2)
  session_name="Robot crossess right of human."
  ;;
3)
  session_name="Robot is overtaken by human. (robot left of human)"
  ;;
4)
  session_name="Robot is overtaken by human. (robot right of human)"
  ;;
5)
  session_name="Robot is overtaken by human with collision"
  ;;
6)
  session_name="Robot is headed to human, in parallel (robot left of human)"
  ;; 
7)
  session_name="Robot is headed to human, in parallel (robot right of human)"
  ;;                           
8)
  session_name="Robot is headed to human with collision"
  ;;  
*)
  echo "Don't know Scenario "$SCENARIO"\n"
  exit
  ;;
esac

# provide some context
echo "------------------- SYSTEM CONFIGURATION -----------------------------"
echo "Using base scenario name: ["$BASE_SCENARIO_NAME"]"
echo "Current scenario: ["$session_name"]"

# get to right folder
cd `rospack find iliad_launch_system`/tmule/

# set .iliadrc, just in case
echo "----------------- SETTING SCENARIO NAME IN ~/.iliadrc ----------------"
sed -i "s/SCENARIO_NAME=.*/\SCENARIO_NAME=\"$BASE_SCENARIO_NAME\"/g" ~/.iliadrc

# set in scenario sh file the world file we are about to use.
sed -i "s:WORLD_NAME=.*:WORLD_NAME=\"$worldFileName\":g" $BASE_SCENARIO_SH_FILE

# Change human walking script duration or delay
echo "----------------------------------------------------------------------"
echo "|    *  SETTING HUMAN start time ("$startTime") delay in world file         "
sed -i "s/.*sed marker 1.*/        \<delay_start\>"$startTime"\<\/delay_start\>  \<\!-- sed marker 1 --\>/" $worldFileName

echo "----------------------------------------------------------------------"
echo "|    *  SETTING HUMAN total walk time ("$endTime") in world file             "
sed -i "s/.*sed marker 2.*/            \<time\>"$endTime"\<\/time\>   \<\!-- sed marker 2 --\>/" $worldFileName

# start tmule for iliad-coordinator
echo "--------------    LAUNCHING COORDINATOR TMULE SCRIPT    --------------"
tmule --config $COORDINATOR_TMULE_SCRIPT launch

# start tmule for iliad-robot
echo "--------------    LAUNCHING ROBOT TMULE SCRIPT    --------------------"
tmule --config $ROBOT_TMULE_SCRIPT launch

# Coordinator needs to receive some robot data before accepting goals ... so we wait >5
echo "----------------------   STUPID 10\" SLEEP HERE  ----------------------"
sleep 10
echo "----------------------     DONE SLEEPING HERE   ----------------------"

# Provide target, start recording
roslaunch synthetic_qrs_interactions additional_nodes.launch robot_id:=$robot_id  descriptor:=$bag_file_code max_scenario_time:=150

# stop tmule for iliad-robot
echo "--------------    STOPPING ROBOT TMULE SCRIPT     --------------------"
tmule --config $ROBOT_TMULE_SCRIPT terminate

# stop tmule for iliad-coordinator
echo "--------------    STOPPING COORDINATOR TMULE SCRIPT     --------------"
tmule --config $COORDINATOR_TMULE_SCRIPT terminate



echo "----------------------------------------------------------------------"
cd $HERE