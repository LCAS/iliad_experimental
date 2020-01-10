#!/bin/bash

# This launches three attempts of four different Interaction Scenarios (see description.txt).
# Each scenario has a delay time for the human to start walking to account for delays in start.

declare -a ScenarioNavigationTime=(
                      # Scenario 1 Robot crosses human left to right (of human). 
                      # x collision! 
                      "1 25 48"
                      # x Human crosses first
                      "1 25 35"
                      # x Robot crosses first
                      "1 25 59"
                      # Scenario 2 Robot crosses human right to left
                      # x collision!
                      "2 25 48"
                      # x Human crosses first
                      "2 25 35"
                      # x Robot crosses first
                      "2 25 59"
                      # Scenario 3 Robot is overtaken by human (robot left of human)
                      # x almost same speed              
                      "3 33 40"                      
                      # x no collision!                      
                      "3 36 15"                                    
                      # Scenario 4 Robot is overtaken by human (robot right of human)                                 
                      # x almost same speed              
                      "4 33 40"                      
                      # x no collision!                      
                      "4 36 15"                                    
                      # Scenario 5 Robot is overtaken by human with collision
                      # x collision in the end
                      "5 25 59"
                      # x collision in the middle
                      "5 25 45"
                      # Scenario 6 Robot is headed to human, in parallel (robot left of human)               
                      # x almost same speed              
                      "6 33 40"
                      # x no collision!                      
                      "6 36 15"
                      # Scenario 7 Robot is headed to human, in parallel (robot right of human)                
                      # x almost same speed              
                      "7 33 40"                      
                      # x no collision!                      
                      "7 36 15"       
                      # Scenario 8 Robot is headed to human with collision
                      # always collision!                                         
                      "8 25 45"    
                                     
          )

ROS_WORKSPACE=$HOME"/workspace/iliad_ws/"
SAVE_FOLDER=$ROS_WORKSPACE"/src/iliad_experimental/bags/"

source $ROS_WORKSPACE"devel/setup.bash"

for ((ATTEMPT = 1; ATTEMPT < 4; ATTEMPT++)); do
      ## now loop through the above array
      for i in "${ScenarioNavigationTime[@]}"
      do
         conf=( $i )
         s=${conf[0]}
         startt=${conf[1]}
         endt=${conf[2]}
         a=$ATTEMPT
         echo -e "......................"
         echo "Running simulation: Scenario: "$s", Human delay: "$startt", Human walk time: "$endt", Attempt: "$a
         rosrun synthetic_qrs_interactions experiment.bash $i $ROS_WORKSPACE
         sleep 150
         echo -e "done."
         echo -e "......................"
         echo -e "Moving bag file to ["$SAVE_FOLDER"]"
         mv $HOME/.ros/*.bag $SAVE_FOLDER
         sleep 1
         echo -e "done."
         echo -e "......................"
         echo -e "Wait 5 secs so you can try read this."
         sleep 5
         echo -e "done."
         echo -e "......................\n\n\n"
      done
done
