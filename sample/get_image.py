# -*- coding: utf-8 -*-

import threading
import time

import cv2
import cv2.cv as cv

import phenox as px

timer_interval_sec = 0.01
camera = px.PX_FRONT_CAM

def do_set_img_seq():
    while True:
        px.set_img_seq(camera)
        time.sleep(timer_interval_sec)

if __name__ == "__main__":
    #daemon thread pattern can be used for 
    #non-strict periodical function calling
    t = threading.Thread(target=do_set_img_seq)
    t.setDaemon(True)
    t.start()

    print("wait for preparing image buffer...")
    time.sleep(1.0)
    counter_getimage = 0

    #Pattern 1: get image as 'cv2.cv.iplimage' type variable
    while True:
        img = px.get_image(camera, 'iplimage')
        if img == None:
            #time.sleep(timer_interval_sec)
            counter_getimage += 1
            continue
        else:
            #"cv.SaveImage" is available for "cv2.cv.iplimage"
            cv.SaveImage("test_iplimage.jpg", img)
            print("save image using 'cv2.cv.iplimage' succeeded")
            break

    print("'get_image' called {0} times".format(counter_getimage))

    #Pattern 2: get image as 'numpy.ndarray' type variable
    while True:
        array = px.get_image(camera, 'ndarray')
        if array == None:
            #time.sleep(timer_interval_sec)
            counter_getimage += 1
            continue
        else:
            #"cv2.imwrite" is available for "numpy.ndarray"
            cv2.imwrite("test_ndarray.jpg", array)
            print("save image using 'numpy.ndarray' succeeded")
            break

    print("'get_image' called {0} times".format(counter_getimage))

