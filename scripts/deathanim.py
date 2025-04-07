
import pygame


def reveal_effect(display, center_pos, radius, mode='expand'):

    width, height = display.get_size()
    transition_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    
    if mode == 'black':
        # Full black screen
        transition_surf.fill((0, 0, 0, 255))
    else:
        # Start with black
        transition_surf.fill((0, 0, 0, 255))
        
        # Draw a transparent hole (circle)
        if radius > 0:
            pygame.draw.circle(transition_surf, (0, 0, 0, 0), center_pos, radius)
    
    display.blit(transition_surf, (0, 0))


