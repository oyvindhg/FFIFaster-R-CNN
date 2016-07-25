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

#####################################################################################

# Draw the grid
def draw_grid(screen):
    width, height = screen.get_size()

    for row in range(height):
        if row % GRID_SPACE != 0:
            continue
        for column in range(width):
            if column % GRID_SPACE != 0:
                continue

            pygame.draw.line(screen, (128, 128, 128), [column, 0], [column, height], 1)

        pygame.draw.line(screen, (128, 128, 128), [0, row], [width, row], 1)



def displayImageMove(screen, px, topleft, prior, grid_on):

    # ensure that the rect always has positive width, height
    x, y = topleft
    width = pygame.mouse.get_pos()[0] - topleft[0]
    height = pygame.mouse.get_pos()[1] - topleft[1]
    if width < 0:
        x += width
        width = abs(width)
    if height < 0:
        y += height
        height = abs(height)

    # eliminate redundant drawing cycles (when mouse isn't moving)
    current = x, y, width, height
    if not (width and height):
        return current
    if current == prior:
        return current

    # draw transparent box and blit it onto canvas
    screen.blit(px, px.get_rect())
    im = pygame.Surface((width, height))
    im.fill((250, 250, 120))
    pygame.draw.rect(im, (0, 0, 0), im.get_rect(), 1)
    im.set_alpha(150)
    screen.blit(im, (x, y))

    if grid_on:
        draw_grid(screen)

    basicfont = pygame.font.SysFont(None, 28)
    text = basicfont.render('x: ' + str(pygame.mouse.get_pos()[0]) + ', y: ' + str(pygame.mouse.get_pos()[1]), True, (255, 0, 0), (255, 255, 255))
    textrect = text.get_rect()
    textrect.centerx = screen.get_rect().topleft[0] + 150
    textrect.centery = screen.get_rect().topleft[1] + 40

    screen.blit(text, textrect)

    pygame.display.flip()

    # return current box extents
    return (x, y, width, height)

def displayImageAdj(screen, px, topleft, bottomright, prior, grid_on):

    x, y = topleft

    width = bottomright[0] - topleft[0]
    height = bottomright[1] - topleft[1]

    if width < 0:
        x += width
        width = abs(width)
    if height < 0:
        y += height
        height = abs(height)

    # eliminate redundant drawing cycles
    current = x, y, width, height
    if not (width and height):
        return current
    if current == prior:
        return current

    # draw transparent box and blit it onto canvas
    screen.blit(px, px.get_rect())
    im = pygame.Surface((width, height))
    im.fill((250, 250, 120))
    pygame.draw.rect(im, (0, 0, 0), im.get_rect(), 1)
    im.set_alpha(150)
    screen.blit(im, (x, y))

    if grid_on:
        draw_grid(screen)

    pygame.display.flip()

    # return current box extents
    return (x, y, width, height)


def setup(path):
    px = pygame.image.load(path)
    screen = pygame.display.set_mode( px.get_rect()[2:], pygame.RESIZABLE)
    #screen = pygame.display.set_mode(px.get_rect()[2:], pygame.FULLSCREEN)
    screen.blit(px, px.get_rect())
    pygame.display.flip()
    return screen, px

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


def mainLoop(screen, px):
    grid_on = False
    topleft = bottomright = prior = None
    esc = 0
    n=0
    obj_list = []
    while n!=1:
        for event in pygame.event.get():


            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    topleft = event.pos
                    bottomright = None
                elif event.button == 3:
                    grid_on = not grid_on
                    if topleft == None:
                        draw_grid(screen)
                        pygame.display.flip()


            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    bottomright = event.pos
                    if bottomright == topleft:
                        topleft = bottomright = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    obj_list = []
                    n = 1
                    esc = 1
                elif event.key == pygame.K_SPACE:
                    n = 1

                elif topleft and bottomright:
                    if event.key == pygame.K_w:
                        topleft = move(screen, topleft, 'up')
                    if event.key == pygame.K_a:
                        topleft = move(screen, topleft, 'left')
                    if event.key == pygame.K_d:
                        topleft = move(screen, topleft, 'right')
                    if event.key == pygame.K_s:
                        topleft = move(screen, topleft, 'down')
                    if event.key == pygame.K_UP:
                        bottomright = move(screen, bottomright, 'up')
                    if event.key == pygame.K_LEFT:
                        bottomright = move(screen, bottomright, 'left')
                    if event.key == pygame.K_RIGHT:
                        bottomright = move(screen, bottomright, 'right')
                    if event.key == pygame.K_DOWN:
                        bottomright = move(screen, bottomright, 'down')

                    if event.key == pygame.K_p:
                        obj_class = 'Person'
                        obj = create_object(obj_class, topleft, bottomright)
                        obj_list.append(obj)
                        topleft = bottomright = prior = None
                        screen.blit(px, px.get_rect())
                        pygame.display.flip()
                        print 'Saved a person!'

        if topleft and bottomright:
            prior = displayImageAdj(screen, px, topleft, bottomright, prior, grid_on)
        elif topleft:
            prior = displayImageMove(screen, px, topleft, prior, grid_on)

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

        screen, px = setup(os.path.join(path, filename))

        obj_list, esc = mainLoop(screen, px)

        if esc:
            break

        width, height = screen.get_size()

        create_xml(FOLDER, filename, width, height, 3, obj_list)



    #im = Image.open(input_loc)
    #im = im.crop(( left, upper, right, lower))
    #pygame.display.quit()
    #im.save(output_loc)