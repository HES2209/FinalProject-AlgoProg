import pygame
import os

# Base path for images
BASE_IMG_PATH = 'images/'

# Function to load a single image
def load_image(path, colorkey=(255, 255, 255)):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    img.set_colorkey(colorkey)  # Make transparent the background color (white) to remove the white border around the image.
    return img

# Function to load multiple images from a directory
def load_images(path, colorkey=(0, 0, 0)):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):  # Display all images that are in the path (Easier way to load many images)
        images.append(load_image(path + '/' + img_name, colorkey))
    return images

# To handle animations
class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
    
    #Create a copy of the animation
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    #Updates the animation frame
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    #To get the current image of the animation
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
