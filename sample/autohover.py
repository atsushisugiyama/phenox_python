#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from threading import Timer

import phenox as px

#const values
camera_id = px.PX_BOTTOM_CAM
timer_interval_ms = 10
features_max = 200

#variables for timer thread
st = px.Selfstate()
msec_cnt = 0
prev_operatemode = px.PX_HALT
timer_enabled = False
timer_busy = False
has_serious_trouble = False


def timer_tick():
    global msec_cnt, prev_operatemode
    global timer_enabled, timer_busy, has_serious_trouble
    global st
    if not timer_enabled: return

    #reserve next timer_tick
    timer = Timer(timer_interval_ms * 0.001, timer_tick)
    timer.start()

    if timer_busy: return

    timer_busy = True

    px.set_keepalive()
    px.set_systemlog()

    px.get_selfstate(st)
    msec_cnt += 1
    if msec_cnt % 3 == 0:
        print(" | ".join("{:.2f}".format(v) for v in [
            st.degx,
            st.degy,
            st.degz,
            st.vision_tx,
            st.vision_ty,
            st.vision_tz,
            st.height
            ]))

    current_operatemode = px.get_operate_mode()
    if prev_operatemode == px.PX_UP and current_operatemode == px.PX_HOVER:
        px.set_visioncontrol_xy(st.vision_tx, st.vision_ty)
    prev_operatemode = current_operatemode

    if px.get_whistle_is_detected():
        #reset is not needed
        #  because this flag turns to False when
        #  return value is True
        #px.reset_whistle_is_detected()
        if current_operatemode == px.PX_HOVER:
            px.set_operate_mode(px.PX_DOWN)
        elif current_operatemode == px.PX_HALT:
            px.set_rangecontrol_z(150.0)
            px.set_operate_mode(px.PX_UP)

    if px.get_battery_is_low():
        has_serious_trouble = True
        timer_enabled = False

    timer_busy = False

if __name__ == '__main__':
    global timer_enabled

    try:
        timer_enabled = True
        timer_tick()
        
        #You may insert your own code in this try statement
        feature_capture_state = 0
        feature_number = 0

        #main thread processes image feature
        while timer_enabled:
            if feature_capture_state == 0:
                if px.get_imgfeature_query(camera_id) == 1:
                    feature_capture_state = 1
            elif feature_capture_state == 1:
                res = px.get_imgfeature(features_max)
                if res:
                    feature_number = str(len(res))
                    print("feature point number: " + feature_number)
                    feature_capture_state = 0
            time.sleep(1)

    #what kind of error will be occur? 
    # -> the most likely one is KeyboardInterrupt.
    except Exception as error:
        print(error)

    finally:
        timer_enabled = False
        px.set_operate_mode(px.PX_HALT)
        if has_serious_trouble:
            os.system("umount /mnt\n")
            os.system("shutdown -h now\n")
