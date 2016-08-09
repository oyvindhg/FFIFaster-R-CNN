#!/usr/bin/env python

import detection
import caffe
from utils.timer import Timer


#The path to to caffemodel and prototxt that are to be used. These can be overrided with --caffemodel and --prototxt when running demo.py.

file = '/home/sommerstudent/testdata/2016-08-09/left0042.jpg'

for j in range(3):
    detections = detection.analyze_image(file)

    detection.draw_result(file, detections, show=True)


#print len(scores), len(boxes)
#print(scores)
#for i in boxes:
#    print(i)
#detection.draw_result(file, scores, boxes)
