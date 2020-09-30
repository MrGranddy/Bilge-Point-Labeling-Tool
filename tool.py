import pygame
import sys, os
from os import listdir
from os.path import isfile, join
import json
from PIL import Image
import numpy as np

IMAGES_PATH = "img/"    # Images to annotate
DATA_PATH = "data/data.json"    # Frame information
LABELS = [label for label in sys.argv[1:]]  # Possible classes for objects ( Given as console argument )

class Circle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

pygame.init()   # Initialize PyGame
pygame.display.set_caption("Bilge Point Labeling Tool")   # Window title

screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h  # Resolution of screen in pixel length

size = width, height = (1000, 750) # Change this in order to change window size
window = pygame.display.set_mode(size)
screen = pygame.display.get_surface()
bg_color = (255,255,255) 

if isfile(DATA_PATH):
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    keys = data.keys()
else:
    data = {}
    keys = set()

circles = []

images = sorted([f for f in listdir(IMAGES_PATH) if isfile(join(IMAGES_PATH, f)) and f not in keys])

curr_img = 0

def delete_circle(x, y, zoom_ratio):
    global selected_circle # use global variable selected frame
    to_delete = None      # if a frame can be found containing the given point
                          # this will be the index of it
    for index, circle in enumerate(circles):
        if (x - circle.x) ** 2 + (y - circle.y) ** 2 <= (1.0 * circle.radius / (height * zoom_ratio)) ** 2:
            to_delete = index
            break
    if to_delete is not None: del circles[to_delete] # If found delete it
    selected_frame = None # Selected frame is reset because indices may shift

def load_image(img_path, zoom_config=None):
    
    image = np.array(Image.open(img_path).convert("RGB"))
    h, w, _ = image.shape

    if zoom_config == None or len(zoom_config) == 0:
        center = ( 0.0, 0.0 )
        zoom_ratio = 1.0
    else:
        zoom_ratio, center = zoom_config[-1]

    unit_len = 1.0 / zoom_ratio


    t = center[0] - unit_len / 2 + 0.5
    b = t + unit_len
    if t < 0:
        t = 0
        b = t + unit_len
    elif b > 1.0:
        b = 1.0
        t = b - unit_len
    l = center[1] - unit_len / 2 + 0.5
    r = l + unit_len
    if l < 0:
        l = 0
        r = l + unit_len
    elif r > 1.0:
        r = 1.0
        l = r - unit_len

    top = int( t * h )
    bottom = int( b * h )
    left = int( l * w )
    right = int( r * w )

    new_image = Image.fromarray(image[top:bottom, left:right, :]).resize((width, height))
    image = np.array(new_image)
    image = pygame.surfarray.make_surface(image.swapaxes(0,1))

    return image

def jsonify(circle):
    return [ circle.y + 0.5, circle.x + 0.5 ]

def save_curr_circles():
    with open(DATA_PATH, "w") as f:
        json.dump(data, f)

def draw_image(image):
    screen.fill(bg_color) # Erase everything ( fill with background color)
    screen.blit(image, (0,0)) # Draw image

def draw_circles(last_zoom_config):
    zoom_ratio, center = last_zoom_config
    for circle in circles:

        rel_x = zoom_ratio * (circle.x - center[0])
        rel_y = zoom_ratio * (circle.y - center[1])

        if abs(rel_x) > 1.0:
            continue
        if abs(rel_y) > 1.0:
            continue

        rel_x = int(height * ( rel_x + 0.5 ))
        rel_y = int(width * ( rel_y + 0.5 ))

        pygame.draw.circle(screen, (255, 0, 0), (rel_y, rel_x), circle.radius, 1)
        pygame.draw.circle(screen, (255, 0, 0), (rel_y, rel_x), 1, 1)

def create_circle(x, y, radius):
    return Circle(x, y, radius)

load_flag = True    # To prevent loading the image every frame
img_width = None    # Current image's width
img_height = None   # Current image's height
img = None  # Current image object
zoom_config = None

while True :

    if load_flag:   # If the current image to display is not loaded to the RAM yet
        img = load_image(IMAGES_PATH + images[curr_img])
        pygame.display.set_caption(images[curr_img])
        # Load the image
        load_flag = False
        zoom_config = [(1.0, (0.0, 0.0))]
        # Since image is loaded make the flag false so it will not be loaded
        # over and over.

    draw_image(img)
    draw_circles(zoom_config[-1])
    pygame.display.flip()
    # Default drawing phase

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and pygame.mouse.get_pos()[0] < width:
            # if left clicked start frame selecting process
            curr_pos = pygame.mouse.get_pos()   # Current position of the mouse
            zoom_ratio, center = zoom_config[-1]

            rel_x = ((1.0 * curr_pos[1] / height) - 0.5) / zoom_ratio + center[0]
            rel_y = ((1.0 * curr_pos[0] / width) - 0.5) / zoom_ratio + center[1]

            circle = create_circle(rel_x, rel_y, 10)
            if circle is not None:
                circles.append(circle)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            # if right clicked on a frame, delete it
            curr_pos = pygame.mouse.get_pos()
            zoom_ratio, center = zoom_config[-1]
            rel_x = ((1.0 * curr_pos[1] / height) - 0.5) / zoom_ratio + center[0]
            rel_y = ((1.0 * curr_pos[0] / width) - 0.5) / zoom_ratio + center[1]
            delete_circle(rel_x, rel_y, zoom_config[-1][0])

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                # if RETURN key is pressed add the frames to data dict and move to the next img
                data[images[curr_img]] = [jsonify(circle) for circle in circles]
                circles = [] # Empty the old images frame list
                curr_img += 1 # Iterate to the next image
                load_flag = True # Since new image will be loaded make the flag True
                save_curr_circles()

                if curr_img == len(images):
                    # If there are no image left save and exit
                    sys.exit()

            if event.key == pygame.K_UP:
                zoom_ratio, center = zoom_config[-1]
                curr_pos = pygame.mouse.get_pos()
                dh = (1.0 * curr_pos[1] / height - 0.5) / zoom_ratio
                dw = (1.0 * curr_pos[0] / width - 0.5) / zoom_ratio
                zoom_ratio *= 2
                center = ( center[0] + 0.5 * dh, center[1] + 0.5 * dw )
                zoom_config += [ (zoom_ratio, center) ]
                img = load_image(IMAGES_PATH + images[curr_img], zoom_config=zoom_config)


            if event.key == pygame.K_DOWN:
                if len(zoom_config) > 1:
                    zoom_config = zoom_config[:-1]
                    img = load_image(IMAGES_PATH + images[curr_img], zoom_config=zoom_config)


        if event.type == pygame.QUIT:
            save_curr_circles()
            sys.exit()

