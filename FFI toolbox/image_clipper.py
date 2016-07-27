#!/usr/bin/python
# -*- coding: utf-8 -*-
from compiler.ast import obj

import pygame, sys
import os
from PIL import Image
from ImageObject import ImageObject
from xml_creator import create_xml

pygame.init()

####################################VARIABLES########################################

#The space between the grids if the user turns on grid view (right mouse click)
GRID_SPACE = 30

#Image depth as seen in the XML. Probably 3 for all color images
IMAGE_DEPTH = 3

#Name of the folder of the images that are to be classified
FOLDER = 'Images'

#The image you want to start classifying from. Write 'all' to classify all
#IMAGE = 'index.jpeg'
IMAGE = 'all'

#Size of the window.
WINDOW_SIZE = (1200,800)

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
        topleft = (max(topleft[0],0), max(topleft[1], 0))
        bottomright = (min(bottomright[0],pictureSize[0]), min(bottomright[1],pictureSize[1]))

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


# Draw the grid
# def draw_grid(screen):
#     width, height = screen.get_size()
#
#     for row in range(height):
#         if row % GRID_SPACE != 0:
#             continue
#         for column in range(width):
#             if column % GRID_SPACE != 0:
#                 continue
#
#             pygame.draw.line(screen, (128, 128, 128), [column, 0], [column, height], 1)
#
#         pygame.draw.line(screen, (128, 128, 128), [0, row], [width, row], 1)


def display_temporary_rectangle(screen, px, topleft, grid_on):
    """Makes the rectangle that is displayed while the left mouse button is still down."""

    im, topleft = make_rectangle(topleft,pygame.mouse.get_pos(),(0,0,0),(250,250,120),60)
    screen.blit(im, topleft)


def display_current_rectangle(screen, px, topleft, bottomright, grid_on):
    """Makes the rectangle that shows the currently selected object when the mouse button is not pressed."""

    im, topleft = make_rectangle(topleft,bottomright,(0,0,0),(250,250,120),60)
    screen.blit(im, topleft)


def setup(path):
    px = pygame.image.load(path)

    #Tilpasse størrelsen på bildet til størrelsen på vinduet
    px_orig_size = px.get_rect()[2:]
    factor = calculate_resize_factor(px_orig_size,WINDOW_SIZE)
    px_size = tuple([int(i*factor) for i in px_orig_size])
    px = pygame.transform.scale(px, px_size)

    screen = pygame.display.set_mode((WINDOW_SIZE), pygame.RESIZABLE)
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


def mainLoop(screen, px, origSize):
    grid_on = False
    topleft = bottomright = None
    esc = 0
    n=0
    obj_list = []
    obj_rect_list = []

    while n != 1:
        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    topleft = event.pos
                    bottomright = None
                # elif event.button == 3:
                #     grid_on = not grid_on
                #     if topleft == None:
                #         draw_grid(screen)
                #         pygame.display.flip()


            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
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
                        #Reset screen
                        screen.blit(px, px.get_rect())

                        topleft,bottomright=fix_topleft_and_bottomright(topleft, bottomright, px.get_rect()[2:])

                        #Make a permanent rectangle
                        obj_rect, topleft = make_rectangle(topleft,bottomright,(0,0,0),(255,255,255),30)
                        obj_rect_list.append((obj_rect, topleft))

                        topleft = tuple([int(i / resize_factor) for i in topleft])
                        bottomright = tuple([int(i / resize_factor) for i in bottomright])

                        topleft, bottomright = fix_topleft_and_bottomright(topleft, bottomright, (origSize[0]-1, origSize[1]-1))

                        obj_class = 'person'
                        obj = create_object(obj_class, topleft, bottomright)
                        obj_list.append(obj)
                        print 'Saved a person!', topleft, bottomright
                        topleft = bottomright = None


        #Draw the screen

        #Draw image
        screen.blit(px, px.get_rect())

        #Draw current rectangle
        new_bottomright = bottomright
        if topleft and not bottomright:
            new_bottomright = pygame.mouse.get_pos()
        if topleft:
            new_topleft, new_bottomright = fix_topleft_and_bottomright(topleft, new_bottomright, px.get_rect()[2:])
            im, new_topleft = make_rectangle(new_topleft, new_bottomright, (0, 0, 0), (250, 250, 120), 60)
            screen.blit(im, new_topleft)
            #print(topleft, bottomright)

        #Draw previous rectangles
        for obj_rect_tuple in obj_rect_list:
            screen.blit(obj_rect_tuple[0], obj_rect_tuple[1])

        #Update screen
        pygame.display.flip()

    return obj_list, esc


if __name__ == "__main__":

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FOLDER)

    files = sorted(os.listdir(path))

    classify = False

    for filename in files:

        if IMAGE != 'all':
            if IMAGE == filename:
                classify = True
            elif classify == False :
                continue

        if os.path.isdir(filename):
            continue

        print 'Let\'s classify', filename

        screen, px, resize_factor, image_size = setup(os.path.join(path, filename))

        obj_list, esc = mainLoop(screen, px, image_size)

        if esc:
            break

        width = image_size[0]
        height = image_size[1]
        FOLDER = "JPEGImages"
        create_xml(FOLDER, filename, width, height, 3, obj_list)



    #im = Image.open(input_loc)
    #im = im.crop(( left, upper, right, lower))
    #pygame.display.quit()
    #im.save(output_loc)