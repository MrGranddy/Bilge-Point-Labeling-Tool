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
    print("No labeld image :(")
    exit()

def dejsonify(circle):
    return Circle(circle[1] - 0.5, circle[0] -0.5, 10)

circles = []

images = sorted([f for f in listdir(IMAGES_PATH) if isfile(join(IMAGES_PATH, f)) and f in keys])

curr_img = 0

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
        circles = [ dejsonify(circle) for circle in data[images[curr_img]] ]
        # Since image is loaded make the flag false so it will not be loaded
        # over and over.

    draw_image(img)
    draw_circles(zoom_config[-1])
    pygame.display.flip()
    # Default drawing phase

    for event in pygame.event.get():
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                curr_img += 1 # Iterate to the next image
                load_flag = True # Since new image will be loaded make the flag True
                if curr_img == len(images):
                    # If there are no image lef exit
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
            sys.exit()

