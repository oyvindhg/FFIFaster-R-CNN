#!/usr/bin/env python

# --------------------------------------------------------
# Faster R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""

import _init_paths
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import caffe, os, sys, cv2
import argparse
import random

########################################VARIABLES#############################################

#Confidence threshold: Increase this value to be more strict about which objects to show. Only objects with P(obj|box) > CONF_THRESH will be shown
CONF_THRESH = 0.8

#Non-Maximum Suppression: Increase this value to allow more squares close to each other.
NMS_THRESH = 0.09

#Mappen med bildene som skal bli analysert. Can be overrided with --images.
IMAGE_DIRECTORY = '/home/sommerstudent/testdata/2016-08-05'

#Run with either "bbox_pred" or "bbox_pred_sgs"
BOX_DELTAS_SGS = "bbox_pred"

#The path to to caffemodel and prototxt that are to be used. These can be overrided with --caffemodel and --prototxt when running demo.py.
CAFFEMODEL = '/home/sommerstudent/fvr-py-FFI/output/faster_rcnn_end2end/ffi_trainval/ffi2016_faster_rcnn_iter_200.caffemodel'
PROTOTXT = '/home/sommerstudent/fvr-py-FFI/models/FFINett/faster_rcnn_end2end/test.prototxt'

#Name of the different classes
#CLASSES = ('__background__', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant','sheep', 'sofa', 'train', 'tvmonitor')
CLASSES = ('__background__', 'person')

#Nets to choose from  #CURRENTLY NOT USED
NETS = {'vgg16': ('VGG16',
                  'VGG16_faster_rcnn_final.caffemodel',
                  'VGG16.v2.caffemodel'),
        'zf': ('ZF',
               'ZF_faster_rcnn_final.caffemodel',
               'ZF.v2.caffemodel'),
        'ffi': ('FFINett01',
                 'FFINett01_faster_rcnn_final.caffemodel')
	}

COLOR = random.randint(0, 9)
NET = caffe.Net(PROTOTXT, CAFFEMODEL, caffe.TEST)
print '\n\nLoaded network {:s}'.format(CAFFEMODEL)

fig, ax = plt.subplots(figsize=(12, 12))    #DRAWING: Initialize figure ready to be drawn to

def int_to_col(number):
    """Convert an integer into one of several pre-defined colors."""

    switcher = {
        0: 'crimson',
        1: 'deeppink',
        2: 'dodgerblue',
        3: 'lawngreen',
        4: 'navy',
        5: 'gold',
        6: 'darksalmon',
        7: 'violet',
        8: 'teal',
        9: 'orange'
    }

    return switcher.get(COLOR % len(switcher), "crimson")


def clean_detections(scores, boxes, thresh = CONF_THRESH):
    """Clean up scores and boxes and return the interesting object in a handy format."""

    for detection_index in range(len(scores)):
        if scores[detection_index][0] > (1-CONF_THRESH):
            continue

    for cls_ind, cls in enumerate(CLASSES[1:]): #There is propably a better way to do this.
        #print cls_ind, cls
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]

        detections = []
        inds = np.where(dets[:, -1] >= thresh)[0]
        for i in inds:
            bbox = dets[i, :4]
            score = dets[i, -1]
            detections.append(({"person":score}, tuple(bbox)))

        return detections


def get_im(image_file):
    """Return a numpy image from a path. Return the input if it is already a numpy image."""

    if str(type(image_file)).split("'")[1] == "numpy.ndarray":  # If image_file is already a numpy image
        return image_file
    elif type(image_file) == str:  # image_file is a string (hopefully the path to an image)
        if not os.path.isfile(image_file):
            print("Could not find the file:", image_file)
            exit()
        return cv2.imread(image_file) #Turns the image path into a numpy.ndarray
    else:
        print("Something is wrong with image_name:", type(image_file))
        exit()


def draw_result(im, detections, show=True):#, ax = None):
    """Draw detections on an image.

    Keyword arguments:
    show -- Whether to open the window and show the results immediately (or else it has to be shown manually later with plt.show()) (default True)
    """

    im = get_im(im)
    im = im[:, :, (2, 1, 0)]
    #if ax == None:
        #fig, ax = plt.subplots(figsize=(12, 12))
        #ax.imshow(im, aspect='equal')

    color = random.randint(0, 9) #To get some pleasurable graphical variation

    for finding in detections: #Iterate through the detected objects
        class_name = ""
        for key in finding[0]: #Find the class with the highest confidence and call it class_name
            if class_name == "" or finding[0][key] > finding[0][class_name]:
                class_name = key

        score = finding[0][class_name]
        xmin, ymin, xmax, ymax = finding[1]

        #Draw rectangle with class name
        ax.add_patch(
            plt.Rectangle((xmin, ymin),
                          xmax - xmin,
                          ymax - ymin, fill=False,
                          edgecolor=int_to_col(color), linewidth=3.5, alpha=0.8)
        )
        ax.text(xmin + 1, ymin,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor=int_to_col(color), alpha=0.6),
                fontsize=14, color='snow')

    #Draw window
    ax.set_title(('{} detection with '
              'p({} | box) >= {:.1f}').format('Object', 'obj',
                                              CONF_THRESH),
             fontsize=14)
    plt.axis('off')
    plt.tight_layout()

    if ax != None:
        #aximage = ax.imshow(im)
        ax.imshow(im)
        #aximage.axes.figure.canvas.draw()
        plt.pause(0.0001)
    # else:
    #     plt.draw()
    #     if show:
    #         plt.show()


def detection(net, image_name):
    """Detect object classes in an image using pre-computed object proposals."""

    im = get_im(image_name)
    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    try:
        scores, boxes = im_detect(net, im, None, BOX_DELTAS_SGS)
    except TypeError:
        print("detection: You may be using an old version of lib/fast_rcnn/test.py. It has been changed in order to receive a fourth argument which is either \"bbox_pred\" or \"bbox_pred_sgs\". Quitting.")
        exit()
    timer.toc()
    print ('im_detect took {:.3f} s for '
           '{:d} object proposals').format(timer.total_time, boxes.shape[0])

    return scores, boxes


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Faster R-CNN demo')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
                        help='Use CPU mode (overrides --gpu)',
                        action='store_true')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]', #CURRENTLY NOT USED
                        choices=NETS.keys(), default='zf') # vgg16
    parser.add_argument('--caffemodel', dest='caffemodel', help='Path to the .caffemodel-file to use. Defaults to the CAFFEMODEL variable set in demo.py',
                        default=CAFFEMODEL)
    parser.add_argument('--prototxt', dest='prototxt',
                        help='Path to the prototxt-file to use. Defaults to the PROTOTXT variable set in demo.py',
                        default=PROTOTXT)
    parser.add_argument('--images', dest='image_directory', help='The path to the directory containing the image files to be analyzed. Defaults to the IMAGE_DIRECTORY variable set in demo.py',
                        default=IMAGE_DIRECTORY)
    parser.add_argument('--imagecount', dest='image_count', help="Number of images to analyze. Use -1 to analyze all images in the specified folder. [-1]",
                        default=-1, type=int)

    args = parser.parse_args()

    return args

def analyze_image(image, cpu=False, gpu_id=0, thresh=CONF_THRESH):
    """Analyze an image and return a list of all interesting objects.

    Keyword arguments:
        cpu -- Whether to use the CPU instead of the GPU (default False)
        thresh -- The minimum detection confidence required to keep a detection (default CONF_THRESH (defined in detection.py))
    """

    analyze_timer = Timer()
    analyze_timer.tic()

    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    if cpu:
        print "Using CPU"
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()
        caffe.set_device(gpu_id)
        cfg.GPU_ID = gpu_id
    im = get_im(image)
    print("Detecting ...")
    scores, boxes = detection(NET, im)
    print("Detected.")

    detections = clean_detections(scores, boxes, thresh)

    analyze_timer.toc()
    print "Total time usage for this image: {:.3f} s".format(analyze_timer.total_time)

    return detections


def main():

    cfg.TEST.HAS_RPN = True  # Use RPN for proposals

    args = parse_args()
    print(args)

    # Warmup on a dummy image   #Does this serve any purpose at all?
    # im = 128 * np.ones((300, 500, 3), dtype=np.uint8)
    # for i in xrange(2):
    #     try:
    #         _ = analyze_image(im, cpu=False)
    #     except TypeError:
    #         print("detection.py: You may be using an old version of lib/fast_rcnn/test.py. It has been changed in order to receive a fourth argument which is either \"bbox_pred\" or \"bbox_pred_sgs\".")
    #         exit()


    print "plt.subplots"
    #fig, ax = plt.subplots(figsize=(12, 12))    #DRAWING: Initialize figure ready to be drawn to

    print "os.listdir"
    im_names = os.listdir(args.image_directory)
    print "sort"
    im_names.sort()
    print "sortert"
    while True:
        i = 0
        for im_name in im_names: #Iterate through the files in the folder
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

            ax.cla()    #DRAWING: Remove any previous drawings from the figure

            file_name = os.path.join(args.image_directory, im_name)
            if os.path.isdir(file_name):
                continue
            print 'Analyzing {}'.format(file_name)

            detections = analyze_image(file_name, cpu=False, gpu_id=0)
            draw_result(file_name, detections, show=True)#, ax=ax)   #DRAWING: Gives ax as an argument to allow it to be drawn to by draw_result)

            if i == args.image_count - 1:
                break
            i += 1

    #plt.show()

if __name__ == '__main__':
    main()