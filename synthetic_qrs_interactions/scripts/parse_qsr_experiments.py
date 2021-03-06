#!/usr/bin/env python

'''
QSR parser. Reads bags produced by Laurence experiments for TAROS 2020

- We use from each bag the topics:
    /robot5/people_tracker_filtered/positions      
    /tf                                            
    /tf_static                                     

- With those, we obtain:
    - Robot Trajectory in map frame: from tf data
    - Human Trajectory in map frame: from positions topic

Note you will need to install tf_bag from https://github.com/LCAS/tf_bag
I recently included last changes from original repo, so our released package most likely won't be updated. 
'''


import rosbag
from tf_bag import BagTfTransformer
from geometry_msgs.msg import TransformStamped
from tf2_geometry_msgs import do_transform_pose
from geometry_msgs.msg import PoseStamped
import numpy as np
from tf.transformations import euler_from_quaternion
import pandas as pd
import tf2_py as tf2

import matplotlib.pyplot as plt


# FUNCTIONS ...................................................................................................

# get yaw from orientation quaternion             
def getYaw(orientation_q):
    (roll, pitch, yaw) = euler_from_quaternion([orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w])
    return yaw     

# print pose stamped with some text description before it
def printPoseSt(poseSt, text):
    print(text + " Pose ( " +
            '{0:.2f}'.format(poseSt.pose.position.x) + ", " + '{0:.2f}'.format(poseSt.pose.position.y) + ", " +
            '{0:.2f}'.format(getYaw(poseSt.pose.orientation) * 180.0 /np.pi) + " deg) " +
            " in frame (" + poseSt.header.frame_id+ ")"
            )  

# get pose stamped modulus
def getModulus(poseSt):
    x = poseSt.pose.position.x 
    y = poseSt.pose.position.y 
    z = poseSt.pose.position.z
    dist = np.sqrt(x*x + y*y + z*z)   
    return dist      

# gets the transfrom from in_frame to out_frame at given time in rosbag object
def getTransform(in_frame_id, out_frame_id, time, bag_tf):
    tfSt = None
    try:
        translation, quaternion = bag_tf.lookupTransform(out_frame_id, in_frame_id, time)
        tfSt = TransformStamped()
        tfSt.header.stamp = time
        tfSt.header.frame_id = out_frame_id
        tfSt.child_frame_id = in_frame_id
        tfSt.transform.translation.x = translation[0]
        tfSt.transform.translation.y = translation[1]
        tfSt.transform.translation.z = translation[2]

        tfSt.transform.rotation.x = quaternion[0]
        tfSt.transform.rotation.y = quaternion[1]
        tfSt.transform.rotation.z = quaternion[2]
        tfSt.transform.rotation.w = quaternion[3]
    except tf2.ExtrapolationException as e:
        print("[getTransform] no tf available yet. ")

    return tfSt

# returns the closest (to ref_frame_id) human posestamped. Sets global var tracked_uuid 
def getClosestHuman(peopleTrackerMsg,time,ref_frame_id,bag_tf):
    global tracked_uuid
    tfi = None
    poseOut = None    
    shouldTransform = (peopleTrackerMsg.header.frame_id != ref_frame_id)

    if (shouldTransform):
        tfi = getTransform(peopleTrackerMsg.header.frame_id, ref_frame_id, time, bag_tf)

    if (tfi!=None) or not shouldTransform:
        poseOut = PoseStamped()
        poseOut.header = peopleTrackerMsg.header

        min_i = -1
        min_d = np.inf

        for i,pose_i in enumerate(peopleTrackerMsg.poses):
            poseOut.pose = pose_i

            if (shouldTransform):
                relPoseSt = do_transform_pose(poseOut, tfi)
            else:
                relPoseSt = poseOut

            d = getModulus(relPoseSt)
            if (d<min_d):
                min_d = d
                min_i = i

        if (min_i!=-1):
            poseOut.pose = peopleTrackerMsg.poses[min_i]
            if tracked_uuid == None:
                tracked_uuid = peopleTrackerMsg.uuids[min_i]
        else:
            poseOut = None

    return poseOut

# At the beginning, it just gets closest human to ref_frame_id. Once got one,
# It will stick to that first detected human.
def getFirstClosestHuman(peopleTrackerMsg,time,ref_frame_id,bag_tf):
    global tracked_uuid
    poseOut = None
    if tracked_uuid == None:
        poseOut = getClosestHuman(peopleTrackerMsg,time,ref_frame_id,bag_tf)

    else:        
        for i,pose_i in enumerate(peopleTrackerMsg.poses):
            if (peopleTrackerMsg.uuids[i]==tracked_uuid):
                poseOut = PoseStamped()
                poseOut.header = peopleTrackerMsg.header
                poseOut.pose = peopleTrackerMsg.poses[i]
                break

    return poseOut    

# ...................................................................................................
# Main function.
if __name__ == '__main__':
    ## params

    # this was a nice clean rosbag
    #bagFolder = '/home/manolofc/ILIAD_DATASETS/HRSI_situation_QTC_rosbags/ot/hotl/'
    #bagFile = '10.bag'

    # this has a couple of missing points due to incomplete tfs
    
    bagFolder = '/home/manolofc/ILIAD_DATASETS/HRSI_situation_QTC_rosbags/ot/rotl/'    
    bagFile = '7.bag'
    resultsFile = bagFile[:-4]+'.csv'
    resultsURI =  bagFolder + resultsFile

    # topic names in bag file
    human_poses_topic = '/robot5/people_tracker_filtered/positions'
    # map frame
    map_frame_id = 'map_laser2d'
    robot_frame_id = 'robot5/base_link'
    saveOutput = False

    viewOutput = False

    # Process bag  ........................................................

    print("..................................")
    print("Processing bag: "+bagFile)
    bag = rosbag.Bag(bagFolder+bagFile)
    bag_transformer = BagTfTransformer(bag)
    global tracked_uuid
    # this is the first, closest human detected
    tracked_uuid = None

    robot_pose_x = []
    robot_pose_y = []
    robot_pose_h = []

    human_pose_x = []
    human_pose_y = []
    human_pose_h = []
    # actually, it's the same for both ...
    human_pose_t = []

    # Process bag ..........................................................
    for topic, msg, t in bag.read_messages():
        if topic == human_poses_topic:
            #print('.')
            # we got a human pose array: cast to map frame if needed.
            human_frame_id = msg.header.frame_id
            shouldTransform = (human_frame_id != map_frame_id)
            transform = None
            if (shouldTransform):
                transform = getTransform(human_frame_id, map_frame_id, t, bag_transformer)

            if (transform!=None) or not shouldTransform:
                # uncomment this if you just want to stick to closest.
                #humanPoseRob = getClosestHuman(msg,t,robot_frame_id,bag_transformer) 
                humanPoseRob = getFirstClosestHuman(msg,t,robot_frame_id,bag_transformer) 
                # if human pose array was empty, we hava a null here
                isValid = (humanPoseRob!=None)

                # this is either wrong or troubleful...
                if isValid:
                    isValid = not ( (humanPoseRob.pose.position.x==0) and (humanPoseRob.pose.position.y==0) and (humanPoseRob.pose.position.z==0))

                if (isValid):                
                    #printPoseSt(humanPoseRob,"Human pose in: ")
                    if (shouldTransform):
                        humanPoseMap = do_transform_pose(humanPoseRob, transform)
                    else:
                        humanPoseMap = humanPoseRob
                    #printPoseSt(humanPoseMap,"Human pose out: ")

                    # Now, we get robot pose in map frame too for comparison.
                    shouldTransform = (robot_frame_id != map_frame_id)

                    if (shouldTransform):
                        transform = getTransform(robot_frame_id, map_frame_id, t, bag_transformer)

                    robotPose = PoseStamped()
                    robotPose.header.frame_id = robot_frame_id
                    robotPose.header.stamp = t
                    
                    if (shouldTransform):
                        robotPoseMap = do_transform_pose(robotPose, transform)
                    else:
                        robotPoseMap = robotPose

                    # Finally, save data
                    robot_pose_x.append(robotPoseMap.pose.position.x)
                    robot_pose_y.append(robotPoseMap.pose.position.y)
                    robot_pose_h.append(getYaw(robotPoseMap.pose.orientation))
                    human_pose_x.append(humanPoseMap.pose.position.x)
                    human_pose_y.append(humanPoseMap.pose.position.y)
                    human_pose_h.append(getYaw(humanPoseMap.pose.orientation))            
                    human_pose_t.append(t.to_sec())
            else:
                print("Skipping point at time "+str(t.to_sec())+" due to incomplete tf tree at that time")
    # close bag
    bag.close()

    # set timestamps to relative
    human_pose_t = np.array(human_pose_t)
    human_pose_t = human_pose_t-human_pose_t[0]

    # I'm using dataframes to generate nice csv's. But much more can be done ...
    df = pd.DataFrame({'robot_pose_x': robot_pose_x,
                       'robot_pose_y': robot_pose_y,
                       'robot_pose_h': robot_pose_h,
                       'human_pose_x': human_pose_x,
                       'human_pose_y': human_pose_y,
                       'human_pose_h': human_pose_h,
                       'human_pose_t': human_pose_t})


    df.to_csv(resultsURI, index=True, columns=['robot_pose_x', 'robot_pose_y', 'robot_pose_h', 'human_pose_x', 'human_pose_y', 'human_pose_h', 'human_pose_t'])

    # Just a quick check
    if viewOutput:
        plt.plot(human_pose_x,human_pose_y,'r',label='human')
        plt.plot(robot_pose_x,robot_pose_y,'g',label='robot')
        plt.show()