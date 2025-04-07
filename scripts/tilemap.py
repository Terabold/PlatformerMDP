import json

import pygame
from Constants import AUTOTILE_TYPES, AUTOTILE_MAP, NEIGHBOR_OFFSETS, PHYSICS_TILES


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
        
        # Convert dict keys to a list before iteration to avoid RuntimeError
        tilemap_keys = list(self.tilemap.keys())
        for loc in tilemap_keys:
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                match = tile.copy()
                match['pos'] = match['pos'].copy()
                match['pos'][0] *= self.tile_size
                match['pos'][1] *= self.tile_size
                matches.append(match)
                if not keep:
                    del self.tilemap[loc]
        
        return matches
    
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()
        
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
        
        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
        
    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
    
    def spike_check(self, entity_rect):
        tile_x1 = int(entity_rect.left // self.tile_size)
        tile_y1 = int(entity_rect.top // self.tile_size)
        tile_x2 = int(entity_rect.right // self.tile_size)
        tile_y2 = int(entity_rect.bottom // self.tile_size)
        
        for x in range(tile_x1, tile_x2 + 1):
            for y in range(tile_y1, tile_y2 + 1):
                tile_loc = f"{x};{y}"
                if tile_loc in self.tilemap:
                    if self.tilemap[tile_loc]['type'] == 'spikes':
                        spike_rect = pygame.Rect(
                            self.tilemap[tile_loc]['pos'][0] * self.tile_size,
                            self.tilemap[tile_loc]['pos'][1] * self.tile_size,
                            self.tile_size, self.tile_size
                        )
                        if entity_rect.colliderect(spike_rect):
                            return True
        return False
    
    def finishline_check(self, entity_rect):
        tile_x1 = int(entity_rect.left // self.tile_size)
        tile_y1 = int(entity_rect.top // self.tile_size)
        tile_x2 = int(entity_rect.right // self.tile_size)
        tile_y2 = int(entity_rect.bottom // self.tile_size)
        
        for x in range(tile_x1, tile_x2 + 1):
            for y in range(tile_y1, tile_y2 + 1):
                tile_loc = f"{x};{y}"
                if tile_loc in self.tilemap:
                    if self.tilemap[tile_loc]['type'] == 'finish':
                        finish_rect = pygame.Rect(
                            self.tilemap[tile_loc]['pos'][0] * self.tile_size,
                            self.tilemap[tile_loc]['pos'][1] * self.tile_size,
                            self.tile_size, self.tile_size
                        )
                        if entity_rect.colliderect(finish_rect):
                            return True
        return False
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def render(self, surf, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))