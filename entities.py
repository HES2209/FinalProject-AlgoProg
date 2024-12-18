import pygame

import math

import random

from particles import Particle

from spark import Spark

# Class to represent a physics-based entity
class PhysicsEntity:
    def __init__(self,game,e_type,pos,size):
        self.game = game
        self.type = e_type
        self.pos = list(pos) #To make each PhysicsEntity have its own position (Convert any iterable to a list)
        self.size = size
        self.velocity = [0,0] #Speed of falling down
        self.collisions = {'up' : False, 'down' : False, 'right' : False, 'left' : False}

        self.action = ''
        self.anim_offset = (-3,-3)
        self.flip = False
        self.set_action('idle') #Set the current animation to idle state when not moving
        
    # Method to get the entity's rectangle
    def rect (self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    # Method to set the entity's action
    def set_action(self,action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    # Method to update the entity's position and handle collisions
    def update(self, tilemap, movement=(0,0)):
        self.collisions = {'up' : False, 'down' : False, 'right' : False, 'left' : False}

        frame_movement = (movement[0] + self.velocity[0], movement [1] + self.velocity[1]) #To determine how much will the PhysicsEntity move in this frame
        
        self.pos[0] += frame_movement[0] #To update the PhysicsEntity's position
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos) : 
            if entity_rect.colliderect(rect) :
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions ['right'] = True
                if frame_movement[0] < 0 : 
                    entity_rect.left = rect.right
                    self.collisions ['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos) : 
            if entity_rect.colliderect(rect) :
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions ['down'] = True
                if frame_movement[1] < 0 : 
                    entity_rect.top = rect.bottom
                    self.collisions ['up'] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        #To max out the falling speed (Making the entity to fall down when there is no tiles)
        self.velocity [1] = min(5, self.velocity[1] + 0.1)

        #If there is a tile or collision below or above the entity then the y-velocity will be 0
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
        self.animation.update() #Update the animation

    #Render the entity on the surface
    def render(self,surf, offset=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset [0] + self.anim_offset[0], self.pos[1] - offset [1] + self.anim_offset[1])) #Flip the sprite so it can face right or left

# Class to represent an enemy entity
class Enemy(PhysicsEntity):
    def __init__ (self, game, pos,size):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0

    # To update the enemy's behavior and position (To attack or shoot projectiles)
    def update(self, tilemap, movement=(0,0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else: 
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else: 
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            # To make the enemy shoot projectiles whenever the player is 16 pixels away from the enemy
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16): 
                    if (self.flip and dis[0] < 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dis[0] > 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))

        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('walk')
        else:
            self.set_action('idle')
        
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.sfx['hit'].play()
                for i in range(30): 
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                return True

# Class to represent the player entity
class Player (PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0 
        self.jumps = 2
        self.dashing = 0

    # Method to update the player's behavior and position
    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1

        if self.air_time > 120:
            self.game.dead += 1

        if self.collisions['down'] : 
            self.air_time = 0
            self.jumps = 2

        if self.air_time > 4 : 
            self.set_action('jump')
        elif movement[0]!= 0 :
            self.set_action('run')
        else :
            self.set_action('idle')
        
        if abs(self.dashing) in {60, 50} : 
            for i in range(20) : 
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]    
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = pvelocity, frame = random.randint(0,7)))
        
        if self.dashing > 0 :
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0 :
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50 : 
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51 :
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = pvelocity, frame = random.randint(0,7)))

        if self.velocity[0] > 0 :
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else : 
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    # Method to render the player on the surface
    def render(self, surf, offset=(0,0)):
        if abs(self.dashing) <= 50 :
            super().render(surf, offset=offset)


    # Method to make the player jump
    def jump(self):
        if self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5

    # Method to make the player dash
    def dash(self):
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60