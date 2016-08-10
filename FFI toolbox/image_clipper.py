#!/usr/bin/python
# -*- coding: utf-8 -*-
from compiler.ast import obj

import pygame, sys
import os
from PIL import Image
from ImageObject import ImageObject
from xml_creator import create_xml
import xml_creator
import subprocess

pygame.init()

####################################VARIABLES########################################

#Image depth as seen in the XML. Probably 3 for all color images
IMAGE_DEPTH = 3

#Name of the folder of the images that are to be classified, and the xml files that are to be created
IMAGE_PATH = '/home/mathias/Dropbox/Testbilder_2016-08-05'
XML_PATH = '/home/mathias/Dropbox/Testbilder_2016-08-05/XML'

#The image you want to start classifying from. Write 'all' to classify all
#IMAGE = 'index.jpeg'
IMAGE = 'left0078.jpg'

#####################################################################################

def fix_topleft_and_bottomright(topleft,bottomright,pictureSize):
    """Makes sure that topleft and bottomright are valid.
    Returns a valid topleft, bottomright."""

    #Makes sure that topleft is at the top left and bottomright is at the bottom right
    tlx, tly = topleft
    brx, bry = bottomright
    topleft = (min(tlx, brx), min(tly, bry))
    bottomright = (max(tlx, brx), max(tly, bry))

    if pictureSize:
        #Makes sure that the selection is within the image
        topleft = (max(topleft[0],1), max(topleft[1], 1))
        bottomright = (min(bottomright[0],pictureSize[0]), min(bottomright[1],pictureSize[1]))

    return topleft, bottomright

def read_old_xml(imagefilename, resizefactor):
    image_name = "".join(imagefilename.split(".")[:-1])
    objectlist = xml_creator.read_xml(image_name, XML_PATH)

    if objectlist == None:
        print("No existing xml file.")
        return [], []
    print("Found previous xml file.")

    # Make permanent rectangles
    obj_rect_list = []
    for old in objectlist:
        xmin = int(old.getXmin() * resizefactor)
        xmax = int(old.getXmax() * resizefactor)
        ymin = int(old.getYmin() * resizefactor)
        ymax = int(old.getYmax() * resizefactor)
        topleft = (xmin, ymin)
        bottomright = (xmax, ymax)
        obj_rect, topleft = make_rectangle(topleft, bottomright, (0, 0, 0), (255, 255, 255), 50)
        obj_rect_list.append((obj_rect, topleft))

    return obj_rect_list, objectlist


def delete_xml(path, filename):
    full_path = os.path.join( path, filename.split('.')[0] + '.xml' )
    try:
        os.remove(full_path)
    except OSError:
        print("No xml file to remove")


def selection_from_points(list_of_points):
    x_values = []
    y_values = []
    for point in list_of_points:
        x_values.append(point[0])
        y_values.append(point[1])

    topleft = (min(x_values), min(y_values))
    bottomright = (max(x_values), max(y_values))
    return topleft, bottomright

#Find the highest possible resize factor for images to be contained within the window
def calculate_resize_factor(image_size, container_size):
    xFactor = container_size[0] / float(image_size[0])
    yFactor = container_size[1] / float(image_size[1])
    return min(xFactor, yFactor)


def make_rectangle(topleft, bottomright, edge_color, fill_color, alpha=255):
    """Returns a surface and a position. Takes a topleft, bottomright, edge color and fill color as tuples of RGB values and an alpha value."""

    topleft, bottomright = fix_topleft_and_bottomright(topleft,bottomright,None)

    width = bottomright[0] - topleft[0]
    height = bottomright[1] - topleft[1]

    rect = pygame.Surface((width, height))
    rect.fill(fill_color)
    pygame.draw.rect(rect, edge_color, rect.get_rect(), 1)
    rect.set_alpha(alpha)

    return rect, topleft


def setup(path):
    px = pygame.image.load(path)

    #Tilpasse størrelsen på bildet til størrelsen på vinduet
    px_orig_size = px.get_rect()[2:]
    factor = calculate_resize_factor(px_orig_size, window_size)
    px_size = tuple([int(i*factor) for i in px_orig_size])
    px = pygame.transform.scale(px, px_size)

    screen = pygame.display.set_mode((window_size), pygame.RESIZABLE)
    screen.blit(px, px.get_rect())
    pygame.display.flip()
    return screen, px, factor, px_orig_size

def move(screen, location, command):
    width, height = screen.get_size()
    if command == 'up' and location[1] > 0:
        print 'up'
        return (location[0], location[1] - 1)
    if command == 'left' and location[0] > 0:
        print 'left'
        return (location[0] - 1, location[1])
    if command == 'down' and location[1] < height - 1:
        print 'down'
        return (location[0], location[1] + 1)
    if command == 'right' and location[0] < width - 1:
        return (location[0] + 1, location[1])
    return (location[0], location[1])

def create_object(name, topleft, bottomright):

    left = min(topleft[0], bottomright[0])
    right = max(topleft[0], bottomright[0])
    top = min(topleft[1], bottomright[1])
    bottom = max(topleft[1], bottomright[1])

    return ImageObject(name, left, top, right, bottom)


def mainLoop(screen, px, origSize, image_name, resizefactor):
    grid_on = False
    topleft = bottomright = None
    esc = 0
    n=0
    obj_rect_list, obj_list = read_old_xml(image_name, resizefactor)

    selected_points = [] #The (up to) four marker points that have been selected so far
    movement = 1 #1 to go to the next image after this one. -1 to go to the previous image after finishing this one.

    while n != 1:
        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    selected_points.append(event.pos)
                    topleft, bottomright = selection_from_points(selected_points)
                    if len(selected_points) == 4:
                        print(topleft, bottomright)
                        selected_points = [] #Reset marker points
                if event.button == 3:
                    selected_points = [] #Reset marker points
                    topleft = event.pos
                    bottomright = None

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    bottomright = event.pos
                    if bottomright == topleft:
                        topleft = bottomright = None

            elif event.type == pygame.QUIT:
                n = 1
                esc = 1

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    n = 1
                    esc = 1
                elif event.key == pygame.K_SPACE:
                    n = 1
                elif event.key == pygame.K_b:
                    print("Changed your mind?")
                    n = 1
                    movement = -1
                elif event.key == pygame.K_DELETE:
                    obj_rect_list = []
                    obj_list = []
                    print("Removed all selections.")
                    n = 1
                    movement = 0

                elif topleft and bottomright:
                    if event.key == pygame.K_w:
                        topleft = move(screen, topleft, 'up')
                    elif event.key == pygame.K_a:
                        topleft = move(screen, topleft, 'left')
                    elif event.key == pygame.K_d:
                        topleft = move(screen, topleft, 'right')
                    elif event.key == pygame.K_s:
                        topleft = move(screen, topleft, 'down')
                    elif event.key == pygame.K_UP:
                        bottomright = move(screen, bottomright, 'up')
                    elif event.key == pygame.K_LEFT:
                        bottomright = move(screen, bottomright, 'left')
                    elif event.key == pygame.K_RIGHT:
                        bottomright = move(screen, bottomright, 'right')
                    elif event.key == pygame.K_DOWN:
                        bottomright = move(screen, bottomright, 'down')

                    elif event.key == pygame.K_p:

                        topleft, bottomright = fix_topleft_and_bottomright(topleft, bottomright, px.get_rect()[2:] )

                        #Make a permanent rectangle
                        obj_rect, topleft = make_rectangle(topleft,bottomright,(0,0,0),(255,255,255), 50)
                        obj_rect_list.append((obj_rect, topleft))

                        topleft = tuple([int(i / resize_factor) for i in topleft])
                        bottomright = tuple([int(i / resize_factor) for i in bottomright])

                        topleft, bottomright = fix_topleft_and_bottomright(topleft, bottomright, (origSize[0]-1, origSize[1]-1))

                        obj_class = 'person'
                        obj = create_object(obj_class, topleft, bottomright)
                        obj_list.append(obj)

                        print 'Saved a person!', topleft, bottomright
                        topleft = bottomright = None
                        selected_points = []


        #Draw the screen

        #Draw image
        screen.blit(px, px.get_rect())

        #Draw current rectangle
        new_bottomright = bottomright
        if topleft and not bottomright:
            new_bottomright = pygame.mouse.get_pos()
        if topleft:
            new_topleft, new_bottomright = fix_topleft_and_bottomright(topleft, new_bottomright, px.get_rect()[2:])
            im, new_topleft = make_rectangle(new_topleft, new_bottomright, (0, 0, 0), (204, 0, 0), 60) #Utah crimson
            screen.blit(im, new_topleft)
            #print(topleft, bottomright)

        #Draw previous rectangles
        for obj_rect_tuple in obj_rect_list:
            screen.blit(obj_rect_tuple[0], obj_rect_tuple[1])

        #Update screen
        pygame.display.flip()

    return obj_list, esc, movement


if __name__ == "__main__":

    path = IMAGE_PATH #os.path.join(os.path.dirname(os.path.abspath(__file__)), IMAGE_FOLDER)

    files = sorted(os.listdir(path))

    classify = False

    #Finds the size of the monitor and gives the window a reasonable size.
    rawsize = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4', shell = True, stdout = subprocess.PIPE).communicate()[0]
    rawsize = rawsize[:-1].split("x")
    window_size = (int(0.94 * int(rawsize[0])), int(0.94 * int(rawsize[1])))

    fileindex = 0
    movement = 1
    while True:
        fileindex %= len(files)
        fileindex = max(0, fileindex)
        filename = files[fileindex]

        if IMAGE != 'all':
            if IMAGE == filename:
                classify = True
            elif classify == False :
                fileindex += movement
                if fileindex == len(files):
                    print("No file called \"{}\"".format(IMAGE))
                continue

        if os.path.isdir(os.path.join(path,filename)):
            print(filename, "is a directory")
            fileindex += movement
            continue

        print 'Let\'s classify', filename

        screen, px, resize_factor, image_size = setup(os.path.join(path, filename))

        obj_list, esc, movement = mainLoop(screen, px, image_size, filename, resize_factor)

        if esc:
            break

        width = image_size[0]
        height = image_size[1]
        FOLDER = "JPEGImages"
        if obj_list:
            create_xml(XML_PATH, FOLDER, filename, width, height, 3, obj_list)
        else:
            delete_xml(XML_PATH, filename)

        fileindex += movement

    #im = Image.open(input_loc)
    #im = im.crop(( left, upper, right, lower))
    #pygame.display.quit()
    #im.save(output_loc)