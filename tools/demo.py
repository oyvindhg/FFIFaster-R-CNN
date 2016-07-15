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

########################################VARIABLES#############################################

#Confidence threshold: Increase this value to be more strict about which objects to show. Only objects with P(obj|box) > CONF_THRESH will be shown
CONF_THRESH = 0.7

#Non-Maximum Suppression: Increase this value to allow more squares close to each other.
NMS_THRESH = 0.3

#Name of the different classes
CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor')

#Nets to choose from
NETS = {'vgg16': ('VGG16',
                  'VGG16_faster_rcnn_final.caffemodel'),
        'zf': ('ZF',
                  'ZF_faster_rcnn_final.caffemodel')}

#############################################################################################

def int_to_col(number):

    switcher = {
        0: 'gold',
        1: 'deeppink',
        2: 'dodgerblue',
        3: 'lawngreen',
        4: 'navy',
        5: 'crimson',
        6: 'darksalmon',
        7: 'violet',
        8: 'teal',
        9: 'orange'
    }

    print number % len(switcher)
    return switcher.get(number % len(switcher), "red")

# Visualize detections for each class
def vis_detections(im, class_name, cls_ind, dets, ax, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    im = im[:, :, (2, 1, 0)]

    ax.imshow(im, aspect='equal')
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor=int_to_col(cls_ind), linewidth=3.5, alpha=0.8)
            )
        ax.text(bbox[0] + 1, bbox[1] ,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor=int_to_col(cls_ind), alpha=0.6),
                fontsize=14, color='snow')



def demo(net, image_name):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    im_file = os.path.join(cfg.DATA_DIR, 'demo', image_name)
    im = cv2.imread(im_file)

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(net, im)
    timer.toc()
    print ('Detection took {:.3f}s for '
           '{:d} object proposals').format(timer.total_time, boxes.shape[0])

    fig, ax = plt.subplots(figsize=(12, 12))

    for cls_ind, cls in enumerate(CLASSES[1:]):

        cls_ind += 1  # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]

        vis_detections(im, cls, cls_ind, dets, ax, thresh=CONF_THRESH)


    ax.set_title(('{} detection with '
              'p({} | box) >= {:.1f}').format('Object', 'obj',
                                              CONF_THRESH),
             fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.draw()


if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals


    prototxt = os.path.join(cfg.MODELS_DIR, NETS['zf'][0],
                            'faster_rcnn_alt_opt', 'faster_rcnn_test.pt')

    caffemodel = os.path.join(cfg.DATA_DIR, 'faster_rcnn_models',
                              NETS['zf'][1])

    if not os.path.isfile(caffemodel):
        raise IOError(('{:s} not found.\nDid you run ./data/script/'
                       'fetch_faster_rcnn_models.sh?').format(caffemodel))

    caffe.set_mode_cpu()

    net = caffe.Net(prototxt, caffemodel, caffe.TEST)

    print '\n\nLoaded network {:s}'.format(caffemodel)
    print '\n\nLoaded network {:s}'.format(caffemodel)

    # Warmup on a dummy image
    #im = 128 * np.ones((300, 500, 3), dtype=np.uint8)
    #for i in xrange(2):
    #    _, _= im_detect(net, im)

    im_names = ['000456.jpg', '000542.jpg', '001150.jpg',
                '001763.jpg', '004545.jpg']


    for im_name in im_names:
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Demo for data/demo/{}'.format(im_name)
        demo(net, im_name)

    plt.show()