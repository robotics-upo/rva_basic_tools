#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import math
import rospy
import tf
from geometry_msgs.msg import PoseStamped, PointStamped

if __name__ == '__main__':
    
    point_publisher = rospy.Publisher('/publish_point', PointStamped, queue_size=10, latch=True)
    rospy.init_node('point_publisher', anonymous=False)  
    seq = 0
    x = rospy.get_param(param_name = '~x', default = 1.0)
    y = rospy.get_param(param_name = '~y', default = 1.0)
    z = rospy.get_param(param_name = '~z', default = 0.0)
    n = 1
    while not rospy.is_shutdown() and n > 0:
        point = PointStamped()
        point.header.frame_id = rospy.get_param("~frame", default="map")
        point.header.stamp = rospy.Time.now()
        point.header.seq = seq
        point.point.x = x
        point.point.y = y
        point.point.z = z
        point_publisher.publish(point)
        rospy.loginfo("Point enviado. Coords: %f %f %f"%(point.point.x, point.point.y, point.point.z))
            
        seq = seq + 1
        n = n - 1
        for i in range(5):
            rospy.sleep(rospy.Duration(1.0))

