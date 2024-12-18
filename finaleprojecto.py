import pygame # Import the pygame module
import math
import sys # Import the sys to exit the program when the user clicks the X
import random 
import os
from utils import load_image, load_images, Animation
from entities import PhysicsEntity, Player, Enemy
from map import Tilemap
from cloud import Clouds
from particles import Particle
from spark import Spark

class Game():
    def __init__(self): # Initialize the game
        pygame.init() # Start the pygame
        pygame.display.set_caption("Samurai Dash") # Rename the window title
        self.screen = pygame.display.set_mode((960,720)) # Create the window for the game
        self.display = pygame.Surface((640,480)) # Create an empty image that has 320,240px size
        self.clock = pygame.time.Clock() # Set the fps at 60
        self.movement = [False,False] # To move the image --> Boolean that could be updated by the if event.type statement

        # Load assets for the game
        self.assets = {
            'decor': (load_images('tiles/decor', colorkey=(0,0,0))),
            'grass': (load_images('tiles/grass')),
            'large_decor': (load_images('tiles/large_decor' , colorkey=(0,0,0))),
            'stone': (load_images('tiles/stone')),
            'player': (load_image('Player/idle/00_idle.png')),
            'background': load_image('Background/mountain.png'),
            'clouds': self.scale_clouds(load_images('clouds')),
            'enemy/idle': Animation(self.scale_images(load_images('Enemy/idle')), img_dur=9),
            'enemy/walk': Animation(self.scale_images(load_images('Enemy/walk')), img_dur=4),
            'enemy/attack': Animation(self.scale_images(load_images('Enemy/attack')), img_dur=4),
            'player/idle': Animation(self.scale_images(load_images('Player/idle')), img_dur=10),
            'player/run': Animation(self.scale_images(load_images('Player/run')), img_dur=4),
            'player/jump': Animation(self.scale_images(load_images('Player/jump')), img_dur=5.5),
            'particle/leaf': Animation((load_images('particles/leaf')), img_dur=20, loop=False),
            'particle/particle': Animation((load_images('particles/particle')), img_dur=6, loop=False),
            'projectiles': load_image('tiles/projectile/blue.png'),
        }

        #Sound effects assets
        self.sfx = {
            'jump' : pygame.mixer.Sound('sfx/jump.mp3'),
            'dash' : pygame.mixer.Sound('sfx/dash.mp3'),
            'hit' : pygame.mixer.Sound('sfx/hit.mp3'),
            'shoot' : pygame.mixer.Sound('sfx/shoot.mp3'),
        }
        #Load the sound effects 
        self.sfx['shoot'].set_volume(0.3)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)



        self.clouds = Clouds(self.assets['clouds'], count=16) #Load the clouds on the screen(atleast there's 16 clouds)
        self.player = Player(self, (90, 90), (16,16)) # Adjust player size to match tile size
        self.tilemap = Tilemap(self, tile_size=16) # Display the tile image on the screen with size (32,32)
        self.level = 0
        self.load_level(self.level)

        self.win_screen = False  # Initialize win screen flag
        self.max_levels = 3  # Set the maximum number of levels to 3 (0, 1, 2)


    def scale_images(self, images):
        return [pygame.transform.scale(img, (16,19)) for img in images] # Scale the image so the physics will align correctly as the image and the player

    def scale_clouds(self, images):
        return [pygame.transform.scale(img, (50,25)) for img in images] # Scale the clouds so it will fit the screen

    def load_level(self, map_id): # Load the map from the map.json file
        self.tilemap.load('maps/' + str(map_id) + '.json')

        self.leaf_spawners = []
        # Extract 'large_decor' tiles with variant 2 and create leaf spawners
        for tree in self.tilemap.extract([('large_decor' , 2)], keep=True):
            # Create a rectangle for each tree to spawn leaves and add to leaf spawners list
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = [] # Store the enemies in the game
        self.enemy_count = 0
        # Extract 'spawners' tiles with variant 0 and 1 to create enemies and player
        for spawner in self.tilemap.extract([('spawners',0),('spawners',1)]):
            if spawner['variant'] == 0:
                # Set player position if spawner variant is 0
                self.player.pos = spawner['pos']
                self.player.air_time = 0 # Reset player's air time
            else: 
                # Create an enemy if spawner variant is 1 and add to enemies list
                self.enemies.append(Enemy(self, spawner['pos'], (16,16)))
                self.enemy_count += 1 # Increment enemy counter
        self.total_enemies = self.enemy_count # Set total enemy counter

        self.projectiles = [] # Store the projectiles in the game
        self.particles = []
        self.sparks = []
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    def run(self): # To run the game
        pygame.mixer.music.load('sfx/bgm.mp3') # Load the background music
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1) # Play the background music infinitely

        while True: # Create a game loop
            self.display.blit(self.assets['background'], (0, 0)) # Draw the background

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    if self.level < self.max_levels - 1:
                        self.level += 1
                        self.load_level(self.level)
                    else:
                        self.win_screen = True
            if self.transition < 0:
                self.transition += 1

            if self.dead: 
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40: 
                    self.load_level(self.level)

            # Update scroll position based on player position (Center of the rectangle)
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20
            #Render the scroll to move horizontally or vertically, depends on the player movement
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Leaf spawn rates (If we have a bigger tree it'll spawn more leafs)
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height: # *49999 to control the spawn rate of the leaf (Make it doesn't spawn every frame)
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1,0.3], frame=random.randint(0,20)))
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll) # Render the clouds and whenever the player moves it will still spawn the clouds out of the screen

            self.tilemap.render(self.display, offset=render_scroll) # Render the tilemap

            # Update and render enemies
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0,0))
                enemy.render(self.display, offset=render_scroll) #Render the enemy even though it is out of the screen
                if kill:
                    self.enemies.remove(enemy)
                    self.enemy_count -= 1 # Decrement enemy counter

            if not self.dead: 
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # Update and render projectiles (If the projectile hits the player or a wall, it will remove the projectile and spawn the particles)
            for projectile in self.projectiles.copy(): 
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectiles']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]): 
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        for i in range(30): 
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0,7)))
            
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            # Copy, update, render each particle in the list, also remove the particle if it's on a certain condition. 
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf': 
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            # Movement stuffs for the player
            for event in pygame.event.get(): # To make the mini screen so it doesn't freeze
                if event.type == pygame.QUIT: # To exit the window if the user clicks the X
                    pygame.quit() # To quit the game
                    sys.exit()
                if event.type == pygame.KEYDOWN: # To move the sprite
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_LSHIFT:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255,255,255))
                self.display.blit(transition_surf, (0,0))
                
            # Display enemy count and total enemies
            font = pygame.font.SysFont(None, 24)
            enemy_count_text = font.render(f'Enemies: {self.enemy_count}/{self.total_enemies}', True, (255, 255, 255))
            self.display.blit(enemy_count_text, (10, 10))

            # Check if all levels are completed
            if self.level == self.max_levels and not len(self.enemies):
                self.win_screen = True

            # Display win screen if all levels are completed
            if self.win_screen:
                self.display.fill((0, 0, 0))  # Clear the screen
                win_text = font.render('You Win!', True, (255, 255, 255))
                self.display.blit(win_text, (self.display.get_width() // 2 - win_text.get_width() // 2, self.display.get_height() // 2 - win_text.get_height() // 2))
                self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
                pygame.display.update()
                continue

            

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0)) # To draw the game display on the screen
            pygame.display.update()
            self.clock.tick(60) # Force the loop to run at 60 fps
Game().run()


