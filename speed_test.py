#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import numpy
import matplotlib.pyplot as plt
import os
import cv2

image_directory = '/home/sommerstudent/testdata/2016-08-03'
im_names = os.listdir(image_directory)

#tstart = time.time()
# Initialize image size on screen
#screen = pygame.display.set_mode((1920, 1080))

#for a in xrange( 100 ):

#  data = pygame.image.load(os.path.join(image_directory, im_names[a]))  # Random image to display

#  # Show image on screen
#  screen.blit(data, (0, 0))
#  pygame.display.flip()


#print ( 'FPS_1:', 100 / ( time.time() - tstart ) )


#fig = plt.figure()
#ax = fig.add_subplot( 111 )

fig, ax = plt.subplots(figsize=(12, 12))

aximage = ax.imshow(numpy.zeros((1080, 1920, 3))) # Blank starting image
#b = ax


#BRUK DENNE METODEN FORELOPIG:

tstart = time.time()
for a in xrange( 100 ):
  ax.cla()
  data = cv2.imread(os.path.join(image_directory, im_names[a]))
  data = data[:, :, (2, 1, 0)]
  ax.set_title( str( a ) )
  ax.text(30 + a, 30,
          '{:s} {:.3f}'.format('lol', 100),
          bbox=dict(facecolor='blue', alpha=0.6),
          fontsize=14, color='snow')
  aximage = ax.imshow(data)

  plt.axis('off')
  plt.tight_layout()
  ax.set_title("My Title")
  aximage.axes.figure.canvas.draw()
  plt.pause(0.0000000000001)

print ( 'FPS_1:', 100 / ( time.time() - tstart ) )

fig, ax = plt.subplots(figsize=(12, 12))
plt.axis('off')
plt.tight_layout()
#ax.set_title("My Title")

tstart = time.time()
plt.ion()

for a in xrange( 100 ):
    ax.cla()
    data = cv2.imread(os.path.join(image_directory, im_names[a]))
    data = data[:, :, (2, 1, 0)]
    ax.imshow(data, aspect='equal')
    ax.set_title(str(a))
    ax.text(30 + a, 30,
            '{:s} {:.3f}'.format('lol', 100),
            bbox=dict(facecolor='blue', alpha=0.6),
            fontsize=14, color='snow')
    plt.pause(0.0000000000001)
    plt.show()

print ( 'FPS_2:', 100 / ( time.time() - tstart ) )
