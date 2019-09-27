# Packages and description:
This is iliad-related experiments package. Things here are either still experimental or doubtfully useful ouside LCAS. 

Note: Those packages are still in early development ("hic sunt dracones")

## constraints maps
Provides a visualization of the mpc spatial constraints. Looks like oru nav is not using them...

## hri_simulation
Depends on `iliad_base_simulation` and `nav_simulation` packages. It simulates human aware navigation.

## iliad_global_planner
Luigi Palmieri already did this. This is a proof of concept of a ROS-compatible global ILIAD planner. Here just for testing ...

## iliad_human_local_navigation
Experiments for the human aware local navigation.

## nav_simulation (previously in package named demo)
Shows simulated forklift using ROS navigation stacks. Currently testing TEB planner and ROS DWA.

## taros19_experiments
Launchers to create simulation experiments with same conditions but different navigation stacks. To be used in TAROS'19 paper.

## Other relevant packages:

* strands_hri
https://github.com/strands-project/strands_hri

* strands_perception_people
https://github.com/strands-project/strands_perception_people

* strands_navigation
https://github.com/strands-project/navigation/tree/han_dwa_only_kinetic

* strands_qsr_lib
https://github.com/strands-project/strands_qsr_lib

* ghmm (required by qsr_lib)
http://ghmm.sourceforge.net/installation.html

* velodyne_simulator
https://github.com/LCAS/velodyne_simulator

* kinect2_simulation
https://gitsvn-nt.oru.se/iliad/software/kinect2_simulation

* iai_kinect2
https://github.com/code-iai/iai_kinect2

* navigation_oru
https://github.com/OrebroUniversity/navigation_oru-release

* Spencer people tracking (iliad branch)
https://github.com/LCAS/spencer_people_tracking/tree/ilidad-dev

* TF utilities for BAG files
https://github.com/LCAS/tf_bag
