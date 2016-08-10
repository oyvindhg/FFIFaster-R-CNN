#!/usr/bin/env python

import detection
import caffe
from utils.timer import Timer
import os
import matplotlib.pyplot as plt
import numpy

image_dir = '/home/ogn/Dropbox/Testbilder 2016-06-29/10m/Med mennesker/Helges godtepose'

im_names = os.listdir(image_dir)


fig, ax = plt.subplots(figsize=(12, 12))

i = 0
for im_name in im_names: #Iterate through the files in the folder

    ax.cla()

    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    file_name = os.path.join(image_dir, im_name)
    if os.path.isdir(file_name):
        continue
    print 'Analyzing {}'.format(file_name)
    detections = detection.analyze_image(file_name, cpu=True, gpu_id=0)
    detection.draw_result(file_name, detections, True, ax)

    if i == 10 - 1:
        break
    i += 1

#plt.show()


