import sys

import pygame

from scripts.utils import load_images, load_image
from scripts.tilemap import Tilemap
from Constants import *

class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.zoom = 10
        self.clock = pygame.time.Clock()
        
        self.tilemap = Tilemap(self, tile_size=TILE_SIZE)

        self.assets = self.reload_assets()
        self.bgIMG = load_image('background.png', scale=(DISPLAY_WIDTH, DISPLAY_HEIGHT))
        
        self.movement = [False, False, False, False]
        
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass
        
        self.scroll = [0, 0]
        
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

    def reload_assets(self):
        IMGscale = (self.tilemap.tile_size, self.tilemap.tile_size)
        return {
            'decor': load_images('tiles/decor', scale=IMGscale),
            'grass': load_images('tiles/grass', scale=IMGscale),
            'stone': load_images('tiles/stone', scale=IMGscale),
            'large_decor': load_images('tiles/large_decor', scale=IMGscale),
            'spawn': [load_image('entities/player/idle/00.png', scale=IMGscale)],  
        }
    
    def deleteGridBlock(self, tile_pos):
        tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
        if tile_loc in self.tilemap.tilemap:
            del self.tilemap.tilemap[tile_loc]

    def placeGridBlock(self, tile_pos, tile_type):
        self.deleteGridBlock(tile_pos)
        self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': tile_type, 'variant': self.tile_variant, 'pos': tile_pos}

        if tile_type == 'spawn':
            self.tilemap.tilemap = {k: v for k, v in self.tilemap.tilemap.items() if v['type'] != 'spawn'}
        
        self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {
            'type': tile_type,
            'variant': self.tile_variant,
            'pos': tile_pos
        }
        
    def run(self):
        while True:
            self.display.blit(self.bgIMG, (0, 0))
            
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 5
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 5
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)
            
            mpos = pygame.mouse.get_pos()
            # Adjust mouse position for the display surface
            adjusted_mpos = (
                mpos[0] * (DISPLAY_WIDTH, DISPLAY_HEIGHT)[0] // (SCREEN_WIDTH, SCREEN_HEIGHT)[0], 
                mpos[1] * (DISPLAY_WIDTH, DISPLAY_HEIGHT)[1] // (SCREEN_WIDTH, SCREEN_HEIGHT)[1]
            )
            
            tile_pos = (
                int((adjusted_mpos[0] + self.scroll[0]) // self.tilemap.tile_size), 
                int((adjusted_mpos[1] + self.scroll[1]) // self.tilemap.tile_size)
            )
            
            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, adjusted_mpos)
            
            if self.clicking and self.ongrid:
                tile_type = self.tile_list[self.tile_group]
                if tile_type == 'spawn':
                    # Remove any existing spawn points first
                    self.tilemap.tilemap = {k: v for k, v in self.tilemap.tilemap.items() if v['type'] != 'spawn'}
                    # Place new spawn point
                    self.placeGridBlock(tile_pos, 'spawn')
                else:
                    self.placeGridBlock(tile_pos, tile_type)

            if self.right_clicking:
                self.deleteGridBlock(tile_pos)
                    
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(
                        tile['pos'][0] * self.tilemap.tile_size - self.scroll[0], 
                        tile['pos'][1] * self.tilemap.tile_size - self.scroll[1], 
                        tile_img.get_width(), 
                        tile_img.get_height()
                    )
                    if tile_r.collidepoint(adjusted_mpos):
                        self.tilemap.offgrid_tiles.remove(tile)
            
            # Display current tile in top-left corner
            self.display.blit(current_tile_img, (5, 5))
            
            # Scale display to screen
            scaled_display = pygame.transform.scale(self.display, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(scaled_display, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            tile_type = self.tile_list[self.tile_group]
                            # if (tile_type not in PHYSICS_TILES and tile_type not in INTERACTIVE_TILES):
                            #     tile_pos = (
                            #         (adjusted_mpos[0] + self.scroll[0]) / self.tilemap.tile_size, 
                            #         (adjusted_mpos[1] + self.scroll[1]) / self.tilemap.tile_size
                            #     )
                            #     self.tilemap.offgrid_tiles.append({
                            #         'type': self.tile_list[self.tile_group], 
                            #         'variant': self.tile_variant, 
                            #         'pos': tile_pos
                            #     })
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
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
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.save('map.json')
                    if event.key in {pygame.K_LSHIFT, pygame.K_RSHIFT}:
                        self.shift = True
                    if event.key == pygame.K_UP:
                        if self.zoom < 20:
                            self.zoom += 1
                            self.zoom = int(self.zoom)
                            self.tilemap.tile_size = int(TILE_SIZE * self.zoom // 10)
                            self.assets = self.reload_assets()
                    if event.key == pygame.K_DOWN:
                        if self.zoom > 1:
                            self.zoom -= 1
                            self.zoom = int(self.zoom)
                            self.tilemap.tile_size = int(TILE_SIZE * self.zoom // 10)
                            self.assets = self.reload_assets()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key in {pygame.K_LSHIFT, pygame.K_RSHIFT}:
                        self.shift = False
            
            pygame.display.update()
            self.clock.tick(FPS)

Editor().run()