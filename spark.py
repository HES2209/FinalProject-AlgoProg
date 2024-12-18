import math
import pygame

# Class to represent a single spark
class Spark:
    def __init__(self, pos, angle, speed):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed

    # Method to update the spark's position and speed
    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        self.speed = max(0, self.speed - 0.1)
        # Return True if the spark has stopped moving
        return not self.speed
    
    # Method to render the spark on the surface
    def render(self, surf, offset=(0, 0)):
        # Calculate the points of the polygon to render based on the spark's position, angle, and speed
        render_points = [
            # First point: in the direction of the angle, scaled by speed * 3
            (self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1]),
            # Second point: 90 degrees clockwise from the angle, scaled by speed * 0.5
            (self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]),
            # Third point: opposite direction of the angle, scaled by speed * 3
            (self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1]),
            # Fourth point: 90 degrees counterclockwise from the angle, scaled by speed * 0.5
            (self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[1]),
        ]
        pygame.draw.polygon(surf, (255, 255, 255), render_points)