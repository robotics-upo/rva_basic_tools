#!/usr/bin/env python



# A very basic TurtleBot script that moves TurtleBot forward indefinitely. Press CTRL + C to stop.  To run:
# On TurtleBot:
# roslaunch turtlebot_bringup minimal.launch
# On work station:
# python goforward.py

import sys
import math
import rospy
import tf
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PointStamped
from nav_msgs.msg import Path

class Turtlebot():
    def __init__(self):


    # Create a publisher which can "talk" to TurtleBot and tell it to move
        # Tip: You may need to change cmd_vel_mux/input/navi to /cmd_vel if you're not using TurtleBot2
        self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        self.sub = rospy.Subscriber('/path', Path, self.callback)
        self.listener = tf.TransformListener()
        self.max_linear_speed = rospy.get_param('~max_linear_speed')
        self.max_angular_speed = rospy.get_param('~max_angular_speed')
        self.distance_tolerance = rospy.get_param('~distance_tolerance')
        self.camino=None
        self.control=0

    def callback(self, path):
        rospy.loginfo("Camino recibido. Numero de puntos: %d", len(path.poses))
        self.camino=path

    def command(self):
        rospy.loginfo("Command")

        goal = PointStamped();
        base_goal = PointStamped();
        goal.header.frame_id = "odom";

        goal.header.stamp = rospy.Time();

        #goal.point.x = gx;
        #goal.point.y = gy;
        goal.point.z = 0.0;

        if (self.camino != None):
            if( self.control < len(self.camino.poses)):
                goal.point.x = self.camino.poses[self.control].pose.position.x
                goal.point.y = self.camino.poses[self.control].pose.position.y
        try:
            base_goal = self.listener.transformPoint('base_footprint', goal)
            if (self.camino != None):
                if (self.meta(base_goal)):
                    self.control+=1
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rospy.loginfo("Problem TF")
            return

        # TODO: put the control law here
        linear = self.lineal_vel(base_goal)
        angular = self.angular_vel(base_goal)
        alpha = math.atan2(base_goal.point.y, base_goal.point.x)
        # alpha=math.fabs(alpha)
        if (alpha > 0.1):
            angular = alpha * 0.5
            linear=0
        else:
            angular = 0
        if (angular > self.max_angular_speed):
            angular = self.max_angular_speed
            linear=0

        rospy.loginfo('Lineal :')
        rospy.loginfo(linear)
        rospy.loginfo('Angular :')
        rospy.loginfo(angular)

        #Publica la velocidad angular y lineal del robot
        self.publish(linear, angular)

    def publish(self,lin_vel, ang_vel):
    # Twist is a datatype for velocity
        move_cmd = Twist()
    # let's go forward at 0.2 m/s
        move_cmd.linear.x = lin_vel
    # let's turn at 0 radians/s
        move_cmd.angular.z = ang_vel

        self.cmd_vel.publish(move_cmd)

    def shutdown(self):
        # stop turtlebot
        rospy.loginfo("Stop TurtleBot")
    # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop TurtleBot
        self.cmd_vel.publish(Twist())
    # sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
        rospy.sleep(1)

    '''
    def lineal_vel(self, base_goal):
        x = base_goal.point.x
        y = base_goal.point.y
        lineal = 0
        dist = math.sqrt(pow(x, 2) + pow(y, 2))
        alfa = 0.4
        if (dist > self.distance_tolerance):
            lineal = alfa * dist
        else:
            lineal = 0
        if (lineal > self.max_linear_speed):
            lineal = self.max_linear_speed
        return lineal
    '''
    def lineal_vel(self, base_goal):
        x = base_goal.point.x
        y = base_goal.point.y
        lineal=0
        dist= math.sqrt(pow(x,2)+pow(y,2))
        alfa= 0.4
        if(dist>self.distance_tolerance):
            if(self.angular_vel(base_goal)>self.max_angular_speed-0.02):
                lineal=0.1
            else:
                lineal = alfa * dist
        else:
            lineal=0
        if(lineal>self.max_linear_speed):
            lineal=self.max_linear_speed
        return lineal


    def angular_vel(self, base_goal):
        x=base_goal.point.x
        y = base_goal.point.y
        alpha=math.atan2(y,x)
        #alpha=math.fabs(alpha)
        if(alpha>0.1):
            angular=alpha*0.5
        else:
            angular=0
        if (angular>self.max_angular_speed):
            angular=self.max_angular_speed
        return angular

    def meta(self, base_goal):
        try:
            x = base_goal.point.x
            y = base_goal.point.y
            dist = math.sqrt(pow(x, 2) + pow(y, 2))
            if(dist<0.1):
                return 1
            else:
                return 0
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rospy.loginfo("Problem meta")
            return
 
if __name__ == '__main__':
    try:
     # initiliaze
        rospy.init_node('robotcontrol', anonymous=False)

    # tell user how to stop TurtleBot
        rospy.loginfo("To stop TurtleBot CTRL + C")

        robot = Turtlebot()
     # What function to call when you ctrl + c
        rospy.on_shutdown(robot.shutdown)

        #goalx=float(sys.argv[1])
        #goaly=float(sys.argv[2])
        #goalx=rospy.get_param('~xgoal')
        #goaly=rospy.get_param('~ygoal')
        #print(goalx)
        #print(goaly)

    #TurtleBot will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
        r = rospy.Rate(10);

    # as long as you haven't ctrl + c keeping doing...
        while not rospy.is_shutdown():
            rospy.loginfo("Loop")
        # publish the velocity
            robot.command()
        # wait for 0.1 seconds (10 HZ) and publish again
            r.sleep()

    except:
        rospy.loginfo("robotcontrol node terminated.")