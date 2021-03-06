#!/usr/bin/env python
import roslib;
import sys
sys.path[0]="/home/tony/ros/indigo/baxter_ws/src/birl_baxter/birl_baxter_dmp/dmp"
roslib.load_manifest('dmp')
import rospy
import numpy as np
import matplotlib.pyplot as plt
from dmp.srv import *
from dmp.msg import *
from baxter_core_msgs.msg import JointCommand




class Dmp(object):
    def __init__(self):
         self.q_s0 = None
         self.q_s1 = None
         self.q_e0 = None
         self.q_e1 = None
         self.q_w0 = None
         self.q_w1 = None
         self.q_w2 = None
  
    def callback(self,data):    
        self.q_s0 = data.command[0]
        self.q_s1 = data.command[1]
        self.q_e0 = data.command[2]
        self.q_e1= data.command[3]
        self.q_w0= data.command[4]
        self.q_w1= data.command[5]
        self.q_w2= data.command[6]
        rospy.loginfo("q_s0 %s", data.command[0])
        rospy.loginfo("q_s1 %s", data.command[1])
        rospy.loginfo("q_e0 %s", data.command[2])
        rospy.loginfo("q_e1 %s", data.command[3])
        rospy.loginfo("q_w0 %s", data.command[4])
        rospy.loginfo("q_w1 %s", data.command[5])
        rospy.loginfo("q_w2 %s", data.command[6])

#    
#    def ik_solve(self,w_x,w_y,w_z,w_qx,w_qy,w_qz,w_qw):
#        rospy.wait_for_service('baxter_tracik/ik_solver')
#        solve = rospy.ServiceProxy('baxter_tracik/ik_solver', ik_solver)
#        resp2 = solve(w_x,w_y,w_z,w_qx,w_qy,w_qz,w_qw)
#        return resp2
#          
#Learn a DMP from demonstration data
    def makeLFDRequest(self,dims, traj, dt, K_gain,
                       D_gain, num_bases):
        demotraj = DMPTraj()
    
        for i in range(len(traj)):
            pt = DMPPoint();
            pt.positions = traj[i]
            demotraj.points.append(pt)
            demotraj.times.append(dt*i)
    
        k_gains = [K_gain]*dims
        d_gains = [D_gain]*dims
    
        print "Starting LfD..."
        rospy.wait_for_service('learn_dmp_from_demo')
        try:
            lfd = rospy.ServiceProxy('learn_dmp_from_demo', LearnDMPFromDemo)
            resp = lfd(demotraj, k_gains, d_gains, num_bases)
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e
        print "LfD done"
    
        return resp;


#Set a DMP as active for planning
    def makeSetActiveRequest(self,dmp_list):
        try:
            sad = rospy.ServiceProxy('set_active_dmp', SetActiveDMP)
            sad(dmp_list)
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e


#Generate a plan from a DMP
    def makePlanRequest(self,x_0, x_dot_0, t_0, goal, goal_thresh,
                        seg_length, tau, dt, integrate_iter):
        print "Starting DMP planning..."
        rospy.wait_for_service('get_dmp_plan')
        try:
            gdp = rospy.ServiceProxy('get_dmp_plan', GetDMPPlan)
            resp = gdp(x_0, x_dot_0, t_0, goal, goal_thresh,
                       seg_length, tau, dt, integrate_iter)
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e
        print "DMP planning done"
    
        return resp;


if __name__ == '__main__':
    rospy.init_node('dmp_baxter_r_arm_node')
    dmp = Dmp()
#    rospy.Subscriber("end_effector_command_solution",JointCommand, dmp.callback)
#    rospy.wait_for_message("end_effector_command_solution",JointCommand)
    
#    rospy.loginfo("q_s0 %s", dmp.q_s0)
    
#    rospy.Subscriber("aruco_tracker/pose",PoseStamped, dmp.callback)
#    rospy.loginfo("I heard %s", dmp.w_qx)
# 
#    print('successfully get rot matrix')

    plt.close('all')
    # read file
    train_set = np.loadtxt('/home/tony/ros/indigo/baxter_ws/src/birl_baxter/birl_baxter_dmp/dmp/datasets/grasp_demo2.txt')
    


    train_len = len(train_set)
    resample_t = np.linspace(train_set[0,0],train_set[-1,0],train_len)
    joint0_data = np.interp(resample_t, train_set[:,0], train_set[:,9])
    joint1_data = np.interp(resample_t, train_set[:,0], train_set[:,10])
    joint2_data = np.interp(resample_t, train_set[:,0], train_set[:,11])
    joint3_data = np.interp(resample_t, train_set[:,0], train_set[:,12])
    joint4_data = np.interp(resample_t, train_set[:,0], train_set[:,13])
    joint5_data = np.interp(resample_t, train_set[:,0], train_set[:,14])
    joint6_data = np.interp(resample_t, train_set[:,0], train_set[:,15])
    
    traj = [[0.0,0.0,0.0,0.0,0.0,0.0,0.0]]* train_len
    for i in range(train_len):
        traj[i] = [joint0_data[i],joint1_data[i],joint2_data[i],joint3_data[i],joint4_data[i],joint5_data[i],joint6_data[i]]

    
    f1, axarr1 = plt.subplots(7, sharex=True)
    axarr1[0].plot(resample_t, joint0_data)
    axarr1[0].set_title('right_arm_joint_space0')
    axarr1[1].plot(resample_t, joint1_data)
    axarr1[2].plot(resample_t, joint2_data)
    axarr1[3].plot(resample_t, joint3_data)
    axarr1[4].plot(resample_t, joint4_data)
    axarr1[5].plot(resample_t, joint5_data)
    axarr1[6].plot(resample_t, joint6_data)

    #plt.show()


    #Create a DMP from a 7-D trajectory
    dims = 7
    dt = 0.01
    K = 100
    D = 2.0 * np.sqrt(K)
    num_bases = 200

    resp = dmp.makeLFDRequest(dims, traj, dt, K, D, num_bases)

    #Set it as the active DMP
    dmp.makeSetActiveRequest(resp.dmp_list)

    #Now, generate a plan
    x_0 = [joint0_data[0],joint1_data[0],joint2_data[0],
           joint3_data[0], joint4_data[0],joint5_data[0], joint6_data[0]]          #Plan starting at a different point than demo
    x_dot_0 = [0.4, 0.4, 0.4, 0.4, 0.4, 0.0, 0.4]
    t_0 = 1.3
#    goal = [ joint_angles['right_s0'], joint_angles['right_s1'],         
#             joint_angles['right_e0'], joint_angles['right_e1'],
#             joint_angles['right_w0'], joint_angles['right_w1'],
#             joint_angles['right_w2']]         #Plan to a different goal than demo
#    goal = [dmp.q_s0, 
#            dmp.q_s1, 
#            dmp.q_e0,
#            dmp.q_e1, 
#            dmp.q_w0, 
#            dmp.q_w1, 
#            dmp.q_w2 ]
    goal =[ joint0_data[-1],joint1_data[-1],
    joint2_data[-1], joint3_data[-1],joint4_data[-1],joint5_data[-1], joint6_data[-1]         ]
    goal_thresh = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
    seg_length = -1          #Plan until convergence to goal
    tau = 2 * resp.tau       #Desired plan should take twice as long as demo
#    dt = 1.0
    integrate_iter = 5       #dt is rather large, so this is > 1
    plan = dmp.makePlanRequest(x_0, x_dot_0, t_0, goal, goal_thresh,
                           seg_length, tau, dt, integrate_iter)
    
    
    
    
    
    
    Column0_plan = [0.0]*len(plan.plan.times)
    Column1_plan = [0.0]*len(plan.plan.times)
    Column2_plan = [0.0]*len(plan.plan.times)
    Column3_plan = [0.0]*len(plan.plan.times)
    Column4_plan = [0.0]*len(plan.plan.times)
    Column5_plan = [0.0]*len(plan.plan.times)
    Column6_plan = [0.0]*len(plan.plan.times)
    for i in range(len(plan.plan.times)):    
        Column0_plan[i] = plan.plan.points[i].positions[0]
        Column1_plan[i] = plan.plan.points[i].positions[1]
        Column2_plan[i] = plan.plan.points[i].positions[2]
        Column3_plan[i] = plan.plan.points[i].positions[3]
        Column4_plan[i] = plan.plan.points[i].positions[4]
        Column5_plan[i] = plan.plan.points[i].positions[5]
        Column6_plan[i] = plan.plan.points[i].positions[6]
        
    resample_t0 = np.linspace(0.01,plan.plan.times[-1], train_len)
    joint0_data_plan = np.interp(resample_t0, plan.plan.times, Column0_plan)
    joint1_data_plan = np.interp(resample_t0, plan.plan.times, Column1_plan)
    joint2_data_plan = np.interp(resample_t0, plan.plan.times, Column2_plan)
    joint3_data_plan = np.interp(resample_t0, plan.plan.times, Column3_plan)
    joint4_data_plan = np.interp(resample_t0, plan.plan.times, Column4_plan)
    joint5_data_plan = np.interp(resample_t0, plan.plan.times, Column5_plan)
    joint6_data_plan = np.interp(resample_t0, plan.plan.times, Column6_plan)
##########  record the plan trajectory 
    WriteFileDir ="/home/tony/ros/indigo/baxter_ws/src/birl_baxter/birl_baxter_dmp/dmp/datasets/baxter_joint_output_data1.txt"    
    plan_len = len(plan.plan.times)
    f = open(WriteFileDir,'w')
    f.write('time,')
    f.write('right_s0,')
    f.write('right_s1,')
    f.write('right_e0,')
    f.write('right_e1,')
    f.write('right_w0,')
    f.write('right_w1,')
    f.write('right_w2\n')
        
    for i in range(train_len):
        f.write("%f," % (resample_t[i],))
        f.write(str(joint0_data_plan[i])+','+str(joint1_data_plan[i])+','+str(joint2_data_plan[i])+','
        +str(joint3_data_plan[i])+','+str(joint4_data_plan[i])+','+str(joint5_data_plan[i])+','+str(joint6_data_plan[i])
        +'\n')        
    f.close()
###########    
#    
#    print "finished"
    
    f2, axarr2 = plt.subplots(7, sharex=True)
    axarr2[0].plot(resample_t, joint0_data_plan)
    axarr2[0].set_title('right_arm_joint_space1')
    axarr2[1].plot(resample_t, joint1_data_plan)
    axarr2[2].plot(resample_t, joint2_data_plan)
    axarr2[3].plot(resample_t, joint3_data_plan)
    axarr2[4].plot(resample_t, joint4_data_plan)
    axarr2[5].plot(resample_t, joint5_data_plan)
    axarr2[6].plot(resample_t, joint6_data_plan)


    plt.show()
#    rospy.spin()

