# -*- coding: utf-8 -*-

from ctypes import *

from numpy import asarray
import cv2


# Image type (IplImage)
IPL_DEPTH_SIGN = 0x80000000

IPL_DEPTH_1U = 1
IPL_DEPTH_8U = 8
IPL_DEPTH_16U = 16
IPL_DEPTH_32F = 32
IPL_DEPTH_64F = 64

IPL_DEPTH_8S = IPL_DEPTH_SIGN + IPL_DEPTH_8U
IPL_DEPTH_16S = IPL_DEPTH_SIGN + IPL_DEPTH_16U
IPL_DEPTH_32S = IPL_DEPTH_SIGN + 32

class IplTileInfo(Structure):
    _fields_ = []

class IplROI(Structure):
    _fields_ = [
        # 0 - no COI (all channels are selected)
        # 1 - 0th channel is selected ...
        ('coi', c_int),
        ('xOffset', c_int),
        ('yOffset', c_int),
        ('width', c_int),
        ('height', c_int),
        ]

# ipl image header
class IplImage(Structure):
    pass

IplImage._fields_ = [
    ("nSize", c_int),
    ("ID", c_int),
    ("nChannels", c_int),
    ("alphaChannel", c_int),
    ("depth", c_int),
    ("colorModel", c_char * 4),
    ("channelSeq", c_char * 4),
    ("dataOrder", c_int),
    ("origin", c_int),
    ("align", c_int),
    ("width", c_int),
    ("height", c_int),
    ("roi", POINTER(IplROI)),
    ("maskROI", POINTER(IplImage)),
    ("imageID", c_void_p),
    ("tileInfo", POINTER(IplTileInfo)),
    ("imageSize", c_int),
    #be careful to use c_void_p!!
    #When making python type 2 IplImage* function, memory allocate is required
    ("imageData", c_void_p), 
    ("widthStep", c_int),
    ("BorderMode", c_int * 4),
    ("BorderConst", c_int * 4),
    ("imageDataOrigin", c_char_p)
    ]

def ipl2iplimage(ipl_ptr, img_shape):
    """get cv2.cv.iplimage from C's IplImage*

    ipl_ptr: POINTER(IplImage) that points to valid image
    img_shape: 3 element int tuple (height, width, n_channels)
    """
    #allocate Python memory for image
    height, width, n_channels = img_shape
    cv_img = cv2.cv.CreateImageHeader((width, height), IPL_DEPTH_8U, n_channels)
    # getting the IplImage* and set memory
    iplimage = ipl_ptr.contents
    str_data = string_at(iplimage.imageData, iplimage.imageSize)
    cv2.cv.SetData(cv_img, str_data, iplimage.widthStep)
    return cv_img

def ipl2array(ipl_ptr, img_shape):
    """get numpy.ndarray from IplImage*

    ipl_ptr: POINTER(IplImage) that points to valid image
    img_shape: 3 element int tuple (height, width, n_channels)
    """
    cv_img = ipl2iplimage(ipl_ptr, img_shape)
    # building a CvMat image by slice operation([:,:]), 
    # and build ndarray from CvMat
    return asarray(cv_img[:, :])

