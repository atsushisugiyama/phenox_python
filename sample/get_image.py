# -*- coding: utf-8 -*-

import threading
import time

import cv2.cv as cv

import phenox as px

timer_interval_sec = 0.01
camera = px.PX_FRONT_CAM

def do_call_set_img_seq():
    while True:
        px.set_img_seq(camera)
        time.sleep(timer_interval_sec)

if __name__ == "__main__":
    #daemon thread pattern can be used for 
    #non-strict periodical function calling
    t = threading.Thread(target=do_call_set_img_seq)
    t.setDaemon(True)
    t.start()

    print("wait for preparing image...")
    time.sleep(1.0)
    print("start to try save image")
    while True:
        array = px.get_image(camera)
        if array == None:
            time.slep(timer_interval_sec)
            continue
        else:
            cv.SaveImage("test.jpg", img)
            print("save image succeeded")
            break

