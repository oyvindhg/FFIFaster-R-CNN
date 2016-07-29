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
CONF_THRESH = 0.4

#Non-Maximum Suppression: Increase this value to allow more squares close to each other.
NMS_THRESH = 0.09

#Mappen med bildene som skal bli analysert. Can be overrided with --images.
IMAGE_DIRECTORY = "/home/sommerstudent/fvr-py-FFI/data/demo"

#Run with either "bbox_pred" or "bbox_pred_sgs"
BOX_DELTAS_SGS = "bbox_pred"

#The path to to caffemodel and prototxt that are to be used. These can be overrided with --caffemodel and --prototxt when running demo.py.
CAFFEMODEL = '/home/sommerstudent/fvr-py-FFI/output/faster_rcnn_end2end/ffi_2016_10m_trainval/ffi2016_faster_rcnn_iter_100.caffemodel'
PROTOTXT = '/home/sommerstudent/fvr-py-FFI/models/new_models/FFINett/faster_rcnn_end2end/test.prototxt'

#Name of the different classes
#CLASSES = ('__background__', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant','sheep', 'sofa', 'train', 'tvmonitor')
CLASSES = ('__background__', 'person')

#Nets to choose from
NETS = {'vgg16': ('VGG16',
                  'VGG16_faster_rcnn_final.caffemodel',
                  'VGG16.v2.caffemodel'),
        'zf': ('ZF',
               'ZF_faster_rcnn_final.caffemodel',
               'ZF.v2.caffemodel'),
        'ffi': ('FFINett01',
                 'FFINett01_faster_rcnn_final.caffemodel')
	}

color = random.randint(0, 9)

def int_to_col(number):

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

    #print number % len(switcher)
    #return switcher.get(number % len(switcher), "red")
    return switcher.get(color,"crimson")

# Visualize detections for each class
def vis_detections(class_name, cls_ind, dets, ax, thresh=0.5):
    """Draw detected bounding boxes."""

    color = random.randint(0, 9)

    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor=int_to_col(color), linewidth=3.5, alpha=0.8)
            )
        ax.text(bbox[0] + 1, bbox[1] ,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor=int_to_col(cls_ind), alpha=0.6),
                fontsize=14, color='snow')


def demo(net, mappe, image_name):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    im_file = os.path.join(mappe, image_name)
    im = cv2.imread(im_file)
    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(net, im, None, BOX_DELTAS_SGS)
    timer.toc()
    print ('Detection took {:.3f}s for '
           '{:d} object proposals').format(timer.total_time, boxes.shape[0])

    fig, ax = plt.subplots(figsize=(12, 12))
    im = im[:, :, (2, 1, 0)]
    ax.imshow(im, aspect='equal')

    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        vis_detections(cls, cls_ind, dets, ax, thresh=CONF_THRESH)
    ax.set_title(('{} detection with '
              'p({} | box) >= {:.1f}').format('Object', 'obj',
                                              CONF_THRESH),
             fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.draw()
def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Faster R-CNN demo')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
                        help='Use CPU mode (overrides --gpu)',
                        action='store_true')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]',
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

analyze_image

if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals

    args = parse_args()
    print(args)

    # prototxt = os.path.join(cfg.ROOT_DIR, 'models', 'pascal_voc',  NETS[args.demo_net][0],
    #                        'faster_rcnn_alt_opt', 'faster_rcnn_test.pt')

    # caffemodel = os.path.join(cfg.DATA_DIR, 'imagenet_models', # 'faster_rcnn_models',
    #                          NETS[args.demo_net][2])

    if not os.path.isfile(args.caffemodel):
        raise IOError(('No caffemodel file found at the path {:s}.\nDid you run ./data/script/'
                       'fetch_faster_rcnn_models.sh?').format(args.caffemodel))

    if args.cpu_mode:
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()
        caffe.set_device(args.gpu_id)
        cfg.GPU_ID = args.gpu_id
    net = caffe.Net(args.prototxt, args.caffemodel, caffe.TEST)

    print '\n\nLoaded network {:s}'.format(args.caffemodel)

    # Warmup on a dummy image
    im = 128 * np.ones((300, 500, 3), dtype=np.uint8)
    for i in xrange(2):
        try:
            _, _= im_detect(net, im, None, BOX_DELTAS_SGS)
        except TypeError:
            print("demo.py: You are using an old version of lib/fast_rcnn/test.py. It has been changed in order to receive a fourth argument which is either \"bbox_pred\" or \"bbox_pred_sgs\".")
            exit()

    im_names = os.listdir(args.image_directory)
    i = 0
    for im_name in im_names:
        print(args.image_count,i)
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Demo for {}'.format(os.path.join(args.image_directory, im_name))
        demo(net, args.image_directory, im_name)
        if i == args.image_count - 1:
            break
        i += 1

    plt.show()
