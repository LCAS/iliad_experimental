cmake_minimum_required(VERSION 2.8.3)
project(synthetic_qrs_interactions)

find_package(catkin REQUIRED)

catkin_package(
)

#############
## Install ##
#############

install(DIRECTORY
   launch
   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

#install(DIRECTORY
#   config
#   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
#)
