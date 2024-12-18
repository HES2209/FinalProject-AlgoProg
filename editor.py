import pygame # Import the pygame module
import sys # Import the sys to exit the program when the user clicks the X
from utils import load_images
from map import Tilemap

RENDER_SCALE = 1.5

class Editor():
    def __init__(self): # Initialize the game
        pygame.init() # Start the pygame
        pygame.display.set_caption("Editor") # Rename the window title
        self.screen = pygame.display.set_mode((960,720)) # Create the window for the game
        self.display = pygame.Surface((640,480)) # Create an empty image that has 320,240px size
        self.clock = pygame.time.Clock() # Set the fps at 60

        # Load assets
        self.assets = {
            'decor' : (load_images ('tiles/decor' , colorkey = (0,0,0))),
            'grass' : (load_images ('tiles/grass')),
            'large_decor' : (load_images ('tiles/large_decor' , colorkey = (0,0,0))),
            'stone' : (load_images ('tiles/stone')),
            'spawners' : load_images('tiles/spawners'),
        }
        
        self.movement = [False,False,False,False] # To move the image --> Boolean that could be updated by the if event.type statement
        self.tilemap = Tilemap(self, tile_size=16)
        
        try:
            self.tilemap.load('map.json') # Load the map
        except FileNotFoundError:
            pass

        self.scroll = [0,0] # Camera position at [0,0]
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

    def scale_images(self, images):
        return [pygame.transform.scale(img, (32,32)) for img in images] # Scale images to 32x32

    def run(self): # To run the game
        while True: # Create a game loop
            self.display.fill((0,0,0)) # Set the background

            # Update scroll position based on movement
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 5
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 5

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll) # Render the tilemap

            # Set the current tile image fully transparent
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)

            mpos = pygame.mouse.get_pos() # Get the pixel position of the mouse pointer
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE) # Get the mouse coordinates
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            # If the mouse is over a tile, then it will show the tile variant
            if self.ongrid:     
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1])) 
            else:
                self.display.blit(current_tile_img, mpos)

            # Handle tile placement and removal
            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type' : self.tile_list[self.tile_group], 'variant' : self.tile_variant, 'pos' : tile_pos}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.display.blit(current_tile_img, (5,5)) # Display the current tile image

            for event in pygame.event.get(): # Handle events
                if event.type == pygame.QUIT: # Exit the window if the user clicks the X
                    pygame.quit() # Quit the game
                    sys.exit()

                # Mouse button down events
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type' : self.tile_list[self.tile_group], 'variant' : self.tile_variant, 'pos' : (mpos[0] + self.scroll [0], mpos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    
                    # Scroll through tile variants or groups
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]]) # Modulo for looping
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else: 
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                # Keyboard events for movement and actions
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid # Toggle between grid and non-grid mode
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.save('map.json')
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0)) # Draw the game display on the screen
            pygame.display.update()
            self.clock.tick(60) # Force the loop to run at 60 fps

Editor().run()


