import random

class Cloud:
    def __init__ (self, pos, img, speed, depth):
        self.pos = list(pos) # Position of the cloud
        self.img = img # Image of the cloud
        self.speed = speed # Speed of the cloud
        self.depth = depth # Depth of the cloud for parallax effect

    def update(self) : 
        self.pos[0] += self.speed # Update the position of the cloud

    def render(self, surf, offset=(0,0)) :
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        surf.blit(self.img, (render_pos[0] %  (surf.get_width() + self.img.get_width()) - self.img.get_width(),render_pos[1] %  (surf.get_height() + self.img.get_height()) - self.img.get_height()))
       

class Clouds :
    def __init__(self, cloud_images,count=16):
        self.clouds = []

        # Create clouds with random positions, images, speeds, and depths
        for i in range(count):
            self.clouds.append(Cloud((random.random() * 999999, 
                                     random.random() * 999999), 
                                     random.choice(cloud_images), 
                                     random.random() * 0.05 + 0.05, 
                                     random.random() * 0.6 + 0.2
                                     ))

        self.clouds.sort(key=lambda x : x.depth) # Sort clouds by depth for correct layering

    def update(self) :
        for cloud in self.clouds:
            cloud.update() # Update each cloud

    def render(self, surf, offset=(0,0)) :
        for cloud in self.clouds:
            cloud.render(surf, offset=offset) # Render each cloud
