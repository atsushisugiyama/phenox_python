# -*- coding: utf-8 -*-

"""this is a module to operate Phenox.

This is a thin lapper code of shared object library 'pxlib.so'. 
Therefore, if you modified base library code 'pxlib.c / pxlib.h' 
and rebuild it with '-shared' option, this module will be affected.

for the safety and usability, this module executes
initialization process.

init_chain()
while not get_cpu1ready():
    pass

this process might take a few second to complete.

in this module the unit is uniformed as follows unless explicitly declared:

length: centi-meter
angle: degree

"""

#changed from "from ctypes import *" for the clean namespaces
import struct
import ctypes

#this module is used to transform IplImage* to python types
import cv_c2py

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

PX_LED_RED = 0
PX_LED_GREEN = 1

#Camera data's shape in numpy.ndarray
PX_CAM_DATA_SHAPE = (240, 320, 3)

#if shared object file moves to an other directory,
#modify "_shared_object_path"
_shared_object_path = r"/root/phenox/library/sobjs/pxlib.so"
pxlib = ctypes.cdll.LoadLibrary(_shared_object_path)

class PhenoxOperate(ctypes.Structure):
    """ operation variable """

    _fields_ = [
        ("mode", ctypes.c_int),
        ("vision_dtx", ctypes.c_float),
        ("vision_dty", ctypes.c_float),
        ("sonar_dtz", ctypes.c_float),
        ("dangx", ctypes.c_float),
        ("dangy", ctypes.c_float),
        ("dangz", ctypes.c_float),
        ("led", ctypes.c_int * 2),
        ("buzzer", ctypes.c_int),
        ("fix_selfposition_query", ctypes.c_int),
        ("fix_selfposition_tx", ctypes.c_float),
        ("fix_selfposition_ty", ctypes.c_float)
    ]

class PhenoxPrivate(ctypes.Structure):
    """ operation variable """

    _fields_ = [
        ("ready", ctypes.c_int),
        ("startup", ctypes.c_int),
        ("selxy", ctypes.c_int),
        ("dangz_rotbusy", ctypes.c_int),
        ("keepalive", ctypes.c_int)
    ]


class PhenoxConfig(ctypes.Structure):
    """ basic configuration parameters for Phenox """

    _fields_ = [
        ("duty_hover", ctypes.c_float),
        ("duty_hover_max", ctypes.c_float),
        ("duty_hover_min", ctypes.c_float),
        ("duty_up", ctypes.c_float),
        ("duty_down", ctypes.c_float),
        ("duty_bias_front", ctypes.c_float),
        ("duty_bias_back", ctypes.c_float),
        ("duty_bias_left", ctypes.c_float),
        ("duty_bias_right", ctypes.c_float),
        ("pgain_vision_tx", ctypes.c_float),
        ("pgain_vision_ty", ctypes.c_float),
        ("dgain_vision_tx", ctypes.c_float),
        ("dgain_vision_ty", ctypes.c_float),
        ("pgain_sonar", ctypes.c_float),
        ("dgain_sonar", ctypes.c_float),
        ("whisleborder", ctypes.c_int),
        ("soundborder", ctypes.c_int),
        ("uptime_max", ctypes.c_float),
        ("downtime_max", ctypes.c_float),
        ("selxytime_max", ctypes.c_float),
        ("dangz_rotspeed", ctypes.c_float),
        ("featurecontrast_front", ctypes.c_int),
        ("featurecontrast_bottom", ctypes.c_int),
        ("pgain_degx", ctypes.c_float),
        ("pgain_degy", ctypes.c_float),
        ("pgain_degz", ctypes.c_float),
        ("dgain_degx", ctypes.c_float),
        ("dgain_degy", ctypes.c_float),
        ("dgain_degz", ctypes.c_float),
        ("pwm_or_servo", ctypes.c_int),
        ("propeller_monitor", ctypes.c_int)
    ]

class SelfState(ctypes.Structure):
    """ self state parameters of Phenox """

    _fields_ = [
        ("degx", ctypes.c_float),
        ("degy", ctypes.c_float),
        ("degz", ctypes.c_float),
        ("vision_tx", ctypes.c_float),
        ("vision_ty", ctypes.c_float),
        ("vision_tz", ctypes.c_float),
        ("vision_vx", ctypes.c_float),
        ("vision_vy", ctypes.c_float),
        ("vision_vz", ctypes.c_float),
        ("height", ctypes.c_float),
        ("battery", ctypes.c_int)
    ]

class ImageFeature(ctypes.Structure):
    """ some special color point?? """

    _fields_ = [
        ("pcx", ctypes.c_float),
        ("pcy", ctypes.c_float),
        ("cx", ctypes.c_float),
        ("cy", ctypes.c_float)
    ]


#1. Basic Functions
def init_chain():
    """[DO NOT USE in user code] allocate shared memory space"""
    pxlib.pxinit_chain()

def close_chain():
    """[DO NOT USE in user code]release shared memory space"""
    pxlib.pxclose_chain()

def get_cpu1ready():
    """[DO NOT USE in user code]

    return bool value indicating whether the CPU1 is ready
    """
    return bool(pxlib.pxget_cpu1ready())

def get_motorstatus():
    """return bool value indicating whether motor is rotating"""
    return bool(pxlib.pxget_motorstatus())

def set_pconfig(param):
    """set PhenoxConfig defined by user

    the argument must be 'PhenoxConfig' type, and
    each property values have to be modified carefully for the safety
    """
    if isinstance(param, PhenoxConfig):
        pxlib.pxset_pconfig(ctypes.byref(param))
    else:
        raise ValueError("pxset_pconfig only accepts 'PhenoxConfig'")

def get_pconfig(param=None):
    """get current PhenoxConfig setting

    if argument type is 'PhenoxConfig',
    the attributes of the argument is overwritten by
    current parameters.

    in other cases, this function returns new 'PhenoxConfig' instance 
    with current parameters.

    NOTE: using PhenoxConfig argument fasten the code.
    """
    if isinstance(param, PhenoxConfig):
        pxlib.pxget_pconfig(ctypes.byref(param))
    else:
        result = PhenoxConfig()
        pxlib.pxget_pconfig(ctypes.byref(result))
        return result

def get_selfstate(state=None):
    """ get current self attitude and position value.

    if the argument type is 'SelfState',
    the attributes of the argument will be overwritten 
    by current parameters and this function return None

    else, this function returns new "SelfState" instance
    with current state parameters.

    NOTE: using SelfState arguments fasten the code
    """

    if isinstance(state, SelfState):
        pxlib.pxget_selfstate(ctypes.byref(state))
    else:
        result = SelfState()
        pxlib.pxget_selfstate(ctypes.byref(result))
        return result

def set_keepalive():
    """ publish the signal which indicates user code is running 

    in user program, this function has to be called periodically
    """
    pxlib.pxset_keepalive()


#2. Auto control functions
def set_operate_mode(val):
    """set current operate mode

    argument must be in [PX_HALT, PX_UP, PX_HOVER, PX_DOWN]
    for the detail, please see Phenox wiki(for C lang)
    """
    if val in [PX_HALT, PX_UP, PX_HOVER, PX_DOWN]:
        pxlib.pxset_operate_mode(val)
    else:
        raise ValueError("pxset_operate_mode only accepts 'int'")

def get_operate_mode():
    """get int value that indicates operate mode

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
        pxlib.pxset_visioncontrol_xy(ctypes.c_float(tx), ctypes.c_float(ty))
    else:
        raise ValueError("pxset_visioncontrol_xy only accepts 'float', 'float'")

def set_rangecontrol_z(tz):
    """set range control target height by choosing tz

    tz must be float value.
    """
    if isinstance(tz, float) or isinstance(tz, int):
        pxlib.pxset_rangecontrol_z(ctypes.c_float(tz))
    else:
        raise ValueError("pxset_rangecontrol_z only accepts 'float'")

def set_dst_degx(val):
    """set destination pitch angle

    angle must be float value
    """
    if isinstance(val, float) or isinstance(val, int): 
        pxlib.pxset_dst_degx(ctypes.c_float(val))
    else:
        raise ValueError("pxset_dst_pitch only accepts 'float'")

def set_dst_degy(val):
    """set destination roll angle

    angle must be float value
    """
    if isinstance(val, float) or isinstance(val, int):
        pxlib.pxset_dst_degy(ctypes.c_float(val))
    else:
        raise ValueError("pxset_dst_roll only accepts 'float'")

def set_dst_degz(val):
    """set destination yaw angle

    angle must be float value
    """
    if isinstance(val, float) or isinstance(val, int):
        pxlib.pxset_dst_degz(ctypes.c_float(val))
    else:
        raise ValueError("pxset_dst_yaw only accepts 'float'")

def set_visualselfposition(tx, ty):
    """ set selfposition value to adjust or reset coordinate

    tx and ty must be float value
    """
    if isinstance(tx, float) and isinstance(ty, float):
        return pxlib.pxset_visualselfposition(
            ctypes.c_float(tx), 
            ctypes.c_float(ty)
            )
    else:
        raise ValueError(
            "pxset_visualselfposition only accepts 'float, float, float'"
            )

#3. Image processing
#3-a. raw image 
def get_image(cameraId, restype='iplimage'):
    """try to get image data obtained by camera.

    if use this function, 'set_img_seq' function has to be called periodically.

    argument means:
        cameraId: phenox.PX_FRONT_CAM or phenox.PX_BOTTOM_CAM
        restype: result images's type from 2 choices below
            'iplimage' -> cv2.cv.iplimage
            'ndarray'  -> numpy.ndarray
            NOTE: invalid option is treated same as 'iplimage'

    return: 
        if succeed to get image -> image data(iplimage or ndarray)
        if failed to get image  -> None
    """
    if not (cameraId == PX_FRONT_CAM or cameraId == PX_BOTTOM_CAM):
        raise ValueError("cameraId must be PX_FRONT_CAM or PX_BOTTOM_CAM")

    img_ptr = ctypes.POINTER(cv_c2py.IplImage)()
    result = pxlib.pxget_imgfullwcheck(cameraId, ctypes.byref(img_ptr))

    if result != 1:
        return None
    
    if restype == 'ndarray':
        return cv_c2py.ipl2array(img_ptr, PX_CAM_DATA_SHAPE)
    else:
        return cv_c2py.ipl2iplimage(img_ptr, PX_CAM_DATA_SHAPE)


def set_img_seq(cameraId):
    """send command to write a part of image

    when use 'get_image' this function has to be called periodically.
    """
    if not (cameraId == PX_FRONT_CAM or cameraId == PX_BOTTOM_CAM):
        raise ValueError(
            "cameraId must be PX_FRONT_CAM or PX_BOTTOM_CAM"
            )

    pxlib.pxset_img_seq(cameraId);

#3-b. image feature points
def set_imgfeature_query(cameraId):
    if not (cameraId == PX_FRONT_CAM or cameraId == PX_BOTTOM_CAM):
        raise ValueError(
            "cameraId must be PX_FRONT_CAM or PX_BOTTOM_CAM"
            )

    result = pxlib.pxset_imgfeature_query(cameraId);
    if result == 1:
        return True
    else:
        return False

def set_imgfeature(maxnum, feature=None):
    """set image feature.
    
    maxnum : int
    feature : None or ImageFeature instance.
    
    if feature is (ImageFeature * maxnum) array, then
        feature is overwritten and return the number of detected feature point.
        the case failed to obtain feature (because of busy) return -1

    else, return value is:
        if succeed  : list(ImageFeature)
        else        : None
    in success case, length of the list is trimmed to valid data length, so
    the number of detected feature points is equal to len(result)
    """
    if not isinstance(maxnum, int):
        raise ValueError("set_imgfeature only accepts 'int[, px_imgfeature]')")

    if isinstance(feature, ImageFeature * maxnum):
        return pxlib.pxget_imgfeature(feature, maxnum)
    else:
        ft = (ImageFeature * maxnum)()
        res = pxlib.pxget_imgfeature(ft, maxnum)
        if res == -1:
            return None
        else:
            return list(ft)[:res]

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
        res = pxlib.pxset_blobmark(
            cameraId, 
            ctypes.c_float(min_y),
            ctypes.c_float(max_y),
            ctypes.c_float(min_u),
            ctypes.c_float(max_u),
            ctypes.c_float(min_v),
            ctypes.c_float(max_v)
        )
        if res == 1:
            return True
        else:
            return False
    else:
        raise TypeError("set_blobmark_query received incorrect type arguments.")

def get_blobmark():
    """get blob mark"""
    x, y, size = ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
    result = pxlib.pxget_blobmark(
        ctypes.byref(x), 
        ctypes.byref(y), 
        ctypes.byref(size)
        )
    if result == 1:
        return (True, x.value, y.value, size.value)
    else:
        return (False, x.value, y.value, size.value)

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
        return pxlib.pxset_sound_recordquery(ctypes.c_float(recordtime))
    else:
        raise ValueError("set_sound_recordquery only accepts 'float'")

def get_sound(recordtime, restype='str'):
    """get raw sound file.

    recordtime should be expressed with second.
    restype must be 'str' or 'list'.

    returns:
        if succeed to get sound data: 
            if restype == 'list' -> raw sound value list
            if restype == 'str' -> binary str filled with raw sound data
        if failed to get sound data (by busy or other reasons):
            if restype == 'list' -> empty list(= [])
            if restype == 'str' -> empty str("")
    """
    if isinstance(recordtime, float):
        size = int(recordtime * 10000)
        buffer = (ctypes.c_short * size)()
        result = pxlib.pxget_sound(buffer, ctypes.c_float(recordtime))
        if result == 1:
            return (result, list(buffer))
        else:
            return (result, [])
    else:
        raise ValueError("get_sound only accepts 'float'")



#5. logger and indicator
def set_led(led, state):
    """set led state.

    led: select LED (phenox.PX_LED_RED or phenox.PX_LED_GREEN)
    state: 
        True -> LED ON
        False -> LED OFF
    """
    if not (led == PX_LED_RED or led == PX_LED_GREEN):
        raise ValueError("led must be PX_LED_RED or PX_LED_GREEN")

    pxlib.pxset_led(led, int(bool(state)))

def set_buzzer(state):
    """set buzzer state

    Phenox buzzer has only 2 states(ON of OFF).
    if bool(state) == True, buzzer turns on, else turns off.
    """
    pxlib.pxset_buzzer(int(bool(state)))


def set_systemlog():
    """set systemlog."""
    pxlib.pxset_systemlog()

def get_battery_is_low():
    """return whether battery voltage is low"""
    return bool(pxlib.pxget_battery())

def __initialize():
    """[DO NOT USE in user code]initialization function"""
    init_chain()
    while not get_cpu1ready():
        pass

#excecuted when loaded for the first time in the program
__initialize()

