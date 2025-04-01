import random

class Background:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth
    
    def update(self):
        self.pos[0] += self.speed
        
    def render(self, surf, offset=(0, 0)):
        # Calculate parallax effect based on depth
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        
        # Handle wrapping of background image to create infinite scrolling effect
        img_width, img_height = self.img.get_width(), self.img.get_height()
        surf_width, surf_height = surf.get_width(), surf.get_height()
        
        # Calculate how many times to tile the image horizontally and vertically
        tiles_x = (surf_width // img_width) + 2
        tiles_y = (surf_height // img_height) + 2
        
        # Calculate starting positions for tiling
        start_x = (render_pos[0] % img_width) - img_width
        start_y = (render_pos[1] % img_height) - img_height
        
        # Render the background image in a grid pattern to cover the entire screen
        for i in range(tiles_x):
            for j in range(tiles_y):
                surf.blit(self.img, (start_x + (i * img_width), start_y + (j * img_height)))

class Backgrounds:
    def __init__(self, background_images, count=3):
        self.backgrounds = []
        
        for i in range(count):
            depth = 0.1 + (i * 0.2)  
            speed = 0.2 + random.random()
            
            # If there are enough images, select one for each layer, otherwise choose randomly
            img_index = i % len(background_images) if i < len(background_images) else random.randint(0, len(background_images) - 1)
            
            self.backgrounds.append(
                Background(
                    (0, 0),  # Starting at origin
                    background_images[img_index],
                    speed,
                    depth
                )
            )
        
        # Sort by depth - deeper backgrounds (closer to 0) should be rendered first
        self.backgrounds.sort(key=lambda x: x.depth)
    
    def update(self):
        for background in self.backgrounds:
            background.update()
    
    def render(self, surf, offset=(0, 0)):
        for background in self.backgrounds:
            background.render(surf, offset=offset)