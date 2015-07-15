# -*- encoding: utf-8 -*-

"""this is a module to operate Phenox.

This is a thin lapper code of shared object(dynamic link) library 
'pxlib.so'. Therefore, if you modified base library code 'pxlib.c' 
and rebuild it with '-shared' option, this module will be affected.

when you operate Phenox by Python, your code must be started with

"phenox.init_chain()"

before using other phenox functions. 
Similarly, your code have to call

"phenox.close_chain()"

before ending process (even when some error occurred).

in this module the unit is uniformed as follows:

length: meter
angle: degree

"""

from ctypes import *

"""
consts below are defined in C by this code.

  typedef enum {
    PX_HALT,
    PX_UP,
    PX_HOVER,
    PX_DOWN
  } px_flymode;

  typedef enum {
    PX_FRONT_CAM,
    PX_BOTTOM_CAM
  } px_cameraid;

"""

PX_HALT = 0
PX_UP = 1
PX_HOVER = 2
PX_DOWN = 3

PX_FRONT_CAM = 0
PX_BOTTOM_CAM = 1

#if shared object file moves to an other directory,
#modify "_shared_object_path"
_shared_object_path = r"/root/phenox/library/sobjs/pxlib.so"
pxlib = cdll.LoadLibrary(_shared_object_path)

class PhenoxOperate(Structure):
    """ operation variable """

    _fields = [
        ("mode", c_int),
        ("vision_dtx", c_float),
        ("vision_dty", c_float),
        ("sonar_dtz", c_float),
        ("dangx", c_float),
        ("dangy", c_float),
        ("dangz", c_float),
        ("led", c_int * 2),
        ("buzzer", c_int),
        ("fix_selfposition_query", c_int),
        ("fix_selfposition_tx", c_float),
        ("fix_selfposition_ty", c_float)
    ]

class PhenoxPrivate(Structure):
    """ operation variable """

    _fields = [
        ("ready", c_int),
        ("startup", c_int),
        ("selxy", c_int),
        ("dangz_rotbusy", c_int),
        ("keepalive", c_int)
    ]


class PhenoxConfig(Structure):
    """ basic configuration parameters for Phenox """

    _fields_ = [
        ("duty_hover", c_float),
        ("duty_hover_max", c_float),
        ("duty_hover_min", c_float),
        ("duty_up", c_float),
        ("duty_down", c_float),
        ("duty_bias_front", c_float),
        ("duty_bias_back", c_float),
        ("duty_bias_left", c_float),
        ("duty_bias_right", c_float),
        ("pgain_vision_tx", c_float),
        ("pgain_vision_ty", c_float),
        ("dgain_vision_tx", c_float),
        ("dgain_vision_ty", c_float),
        ("pgain_sonar", c_float),
        ("dgain_sonar", c_float),
        ("whisleborder", c_int),
        ("soundborder", c_int),
        ("uptime_max", c_float),
        ("downtime_max", c_float),
        ("selxytime_max", c_float),
        ("dangz_rotspeed", c_float),
        ("featurecontrast_front", c_int),
        ("featurecontrast_bottom", c_int),
        ("pgain_degx", c_float),
        ("pgain_degy", c_float),
        ("pgain_degz", c_float),
        ("dgain_degx", c_float),
        ("dgain_degy", c_float),
        ("dgain_degz", c_float),
        ("pwm_or_servo", c_int),
        ("propeller_monitor", c_int)
    ]

    #do not need to define __init__ ??
    #it may be required for the safety

class Selfstate(Structure):
    """ self state parameters of Phenox """

    _fields_ = [
        ("degx", c_float),
        ("degy", c_float),
        ("degz", c_float),
        ("vision_tx", c_float),
        ("vision_ty", c_float),
        ("vision_tz", c_float),
        ("vision_vx", c_float),
        ("vision_vy", c_float),
        ("vision_vz", c_float),
        ("height", c_float),
        ("battery", c_int)
    ]

class Blobmark(Structure):
    """ some special color point?? """

    _fields_ = [
        ("cx", c_float),
        ("cy", c_float),
        ("size", c_float)
    ]

class BlobmarkConfig(Structure):
    """ some special color point?? """

    _fields_ = [
        ("min_y", c_int),
        ("min_u", c_int),
        ("min_v", c_int),
        ("max_y", c_int),
        ("max_u", c_int),
        ("max_v", c_int),
        ("state", c_int),
        ("cam", c_int),
        ("num", c_int)
    ]

class ImageFeature(Structure):
    """ some special color point?? """

    _fields_ = [
        ("pcx", c_float),
        ("pcy", c_float),
        ("cx", c_float),
        ("cy", c_float)
    ]



#1. Basic Functions
def init_chain():
    """initialize memory setting and default parameters.

    use this function first in 'phenox' module.
    """
    pxlib.pxinit_chain()

def close_chain():
    """free memory setting.

    use this function before closing the program.
    """
    pxlib.pxclose_chain()

def get_cpu1ready():
    """return bool whether the cpu1 is ready.

    embedded program (for control and image processing) runs on cpu1.
    you have to wait until this function's result becomes True
    """
    return bool(pxlib.pxget_cpu1ready())

#I could not get what this module is(2015.May.11)
def get_motorstatus():
    """get the status of motors"""
    return pxlib.pxget_motorstatus()

def set_pconfig(param):
    """set pconfig defined by user

    the arguement must be 'pconfig' type, and
    each property values have to be modified carefully.
    """
    if isinstance(param, PhenoxConfig):
        pxlib.pxset_pconfig(byref(param))
    else:
        raise TypeError("pxset_pconfig only accepts 'pconfig'")

def get_pconfig(param=None):
    """get pconfig defined by user

    if arguement type is 'pconfig',
    the parameters of the arguement is overwritten by
    current parameters.

    if arguement is None or arguement type is not 'pconfig',
    the result is new 'pconfig' instance filled with 
    current parameters.

    NOTE: using pconfig arguement means cache and it fasten the code.
    """
    if isinstance(param, PhenoxConfig):
        pxlib.pxget_pconfig(byref(param))
    else:
        result = PhenoxConfig()
        pxlib.pxget_pconfig(byref(result))
        return result

def get_selfstate(state=None):
    """ return the self attitude and position value.

    if the argument is left to "None",
    this function instantiate "selfstate" type variable and
    initialie it by "pxget_selfstate" function, and return it.

    if the argument is "selfstate" type, then the argument will be
    used in "pxget_selfstate" function by reference.
    """

    if state == None:
        result = Selfstate()
        pxlib.pxget_selfstate(byref(result))
        return result
    elif isinstance(state, Selfstate):
        pxlib.pxget_selfstate(byref(state))
    else:
        raise TypeError("pxget_selfstate only accepts 'selfstate'")

def set_keepalive():
    pxlib.pxset_keepalive()


#2. Auto control functions
def set_operate_mode(val):
    """set int value that indicates operate mode.

    arguement must be in 
        [PX_HALT, PX_UP, PX_HOVER, PX_DOWN] which is equal to
        [0, 1, 2, 3]
    for detail, please see Phenox wiki(for C lang)
    """
    if isinstance(val, int):
        pxlib.pxset_operate_mode(val)
    else:
        raise TypeError("pxset_operate_mode only accepts 'int'")

def get_operate_mode():
    """get int value that indicates operate mode.

    result means:
        0(PX_HALT): stop all motors
        1(PX_UP): starting and going up to hover
        2(PX_HOVER): hovering or cruising
        3(PX_DOWN): executing landing maneuver
    """
    return pxlib.pxget_operate_mode()

def set_visioncontrol_xy(tx, ty):
    """set vision control target horizontal positions(tx, ty)

    tx and ty must be float value.
    """
    if ((isinstance(tx, float) or isinstance(tx, int)) and 
        (isinstance(ty, float) or isinstance(ty, int))
        ):
        pxlib.pxset_visioncontrol_xy(c_float(tx), c_float(ty))
    else:
        raise TypeError("pxset_visioncontrol_xy only accepts 'float', 'float'")

def set_rangecontrol_z(tz):
    """set range control target height by choosing tz

    tz must be float value.
    """
    if isinstance(tz, float) or isinstance(tz, int):
        pxlib.pxset_rangecontrol_z(c_float(tz))
    else:
        raise TypeError("pxset_rangecontrol_z only accepts 'float'")

def set_dst_degx(val):
    """set destination pitch angle

    angle must be float value written by degree-unit manner.
    """
    if isinstance(val, float) or isinstance(val, int):
        pxlib.pxset_dst_degx(c_float(val))
    else:
        raise TypeError("pxset_dst_pitch only accepts 'float'")

def set_dst_degy(val):
    """set destination roll angle

    angle must be float value written by degree-unit manner.
    """
    if isinstance(val, float) or isinstance(val, int):
        pxlib.pxset_dst_degy(c_float(val))
    else:
        raise TypeError("pxset_dst_roll only accepts 'float'")

def set_dst_degz(val):
    """set destination yaw angle

    angle must be float value written by degree-unit manner.
    """
    if isinstance(val, float) or isinstance(val, int):
        pxlib.pxset_dst_degz(c_float(val))
    else:
        raise TypeError("pxset_dst_yaw only accepts 'float'")

def set_visualselfposition(tx, ty):
    if isinstance(tx, float) and isinstance(ty, float):
        return pxlib.pxset_visualselfposition(c_float(tx), c_float(ty))
    else:
        raise TypeError(
            "pxset_visualselfposition only accepts 'float, float, float'"
            )

#3. Image processing
#3-a. raw image 
def get_imgfullwcheck(cameraId, img):
    #this function arguement is "IplImage" so implementation is hard..
    return None

def set_img_seq(cameraId):
    if isinstance(cameraId, int):
        pxlib.pxset_img_seq(cameraId);
    else:
        raise TypeError("set_img_seq only accepts 'int'")

#3-b. image feature points
def set_imgfeature_query(cameraId):
    if isinstance(cameraId, int):
        return pxlib.pxset_imgfeature_query(cameraId);
    else:
        raise TypeError("set_imgfeature_query only accepts 'int'")

def set_imgfeature(maxnum, feature=None):
    """set image feature.
    
    maxnum : int
    feature : None or px_imgfeature instance.
    
    if feature is None or not px_feature, return value is 2 item tuple.
        (result(int) from pxlib.so), (img_feature_instance))

    if feature is px_feature, return value is only
        result(int) from pxlib.so
    and feature will be overwritten.
    """
    if not isinstance(maxnum, int):
        raise TypeError("set_imgfeature only accepts 'int[, px_imgfeature]')")

    if isinstance(feature, ImageFeature):
        return pxlib.pxget_imgfeature(byref(feature), maxnum)
    else:
        ft = (ImageFeature * maxnum)()
        result = pxlib.pxget_imgfeature(byref(ft), maxnum)
        return result, ft

#3-c. image color blob
def set_blobmark_query(cameraId, min_y, max_y, min_u, max_u, min_v, max_v):
    """set blob mark query."""
    if (isinstance(cameraId, int) and 
        isinstance(min_y, float) and 
        isinstance(max_y, float) and 
        isinstance(min_u, float) and 
        isinstance(max_u, float) and 
        isinstance(min_v, float) and 
        isinstance(max_v, float)
        ):
        return pxlib.pxset_blobmark(
            cameraId, 
            c_float(min_y),
            c_float(max_y),
            c_float(min_u),
            c_float(max_u),
            c_float(min_v),
            c_float(max_v)
        )
    else:
        raise TypeError("set_blobmark_query received incorrect type arguments.")

def get_blobmark():
    """get blob mark"""
    x, y, size = c_float(), c_float(), c_float()
    pxlib.pxget_blobmark(byref(x), byref(y), byref(size))
    return (x.value, y.value, size.value)

#4. sound processing
def get_whistle_is_detected():
    """return True if whistle sound is detected, else return False""" 
    return bool(pxlib.pxget_whisle_detect())

def reset_whistle_is_detected():
    """reset whistle detected flag to 0"""
    pxlib.pxset_whisle_detect_reset()

def get_sound_recordstate():
    """get sound record state."""
    return pxlib.pxget_sound_recordstate()

def set_sound_recordquery(recordtime):
    """set sound record query.

    record time is in the range of (0, 50.0]
    """
    if isinstance(recordtime, float):
        return pxlib.pxset_sound_recordquery(c_float(recordtime))
    else:
        raise TypeError("set_sound_recordquery only accepts 'float'")

def get_sound(recordtime):
    """get raw sound file.

    recordtime should be expressed with second.
    result is tuple of (int, list(int))
    1st value:
        1: succeed to get sound
        -1: failed to get sound
    2nd value:
        (if 1st value == 1): sound data
        (if 1st value == -1): empty list(= [])
    """
    if isinstance(recordtime, float):
        size = int(recordtime * 10000)
        buffer = (c_short * size)()
        result = pxlib.pxget_sound(buffer, c_float(recordtime))
        if result == 1:
            return (result, buffer)
        else:
            return (result, [])
    else:
        raise TypeError("get_sound only accepts 'float'")


#5. logger and indicator
def set_led(led, state):
    """set led state.

    led(0 or 1) indicates which LED light to set
    state(0:OFF or 1:ON) indicates LED state
    """
    if isinstance(led, int) and isinstance(state, int):
        pxlib.pxset_led(led, state)
    else:
        raise TypeError("set_led only accepts 'int, int'")

def set_buzzer(state):
    """set buzzer state.

    Phenox buzzer only take 2 state(ON of OFF).
    by selecting 0, buzzer turns off,
    by selecting 1, buzzer turns on.
    """
    if isinstance(state, int):
        pxlib.pxset_buzzer(state)
    else:
        raise TypeError("set_buzzer only accepts 'int'")

def set_systemlog():
    """set systemlog."""
    pxlib.pxset_systemlog()

def get_battery():
    """get battery status.

    '1' indicates abnormal state???
    """
    return pxlib.pxget_battery()

