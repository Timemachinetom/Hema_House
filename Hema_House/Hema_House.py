import pygame
import sys
import os
import time
from fencer import Fencer
from game_manager import GameManager
from ai_controller import AIController
from menu_system import MenuSystem


# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 30
MOVE_STEP = 30  # pixels to move per arrow key
ANIMATION_DELAY = 5  # Adjust for animation speed
pause_frames = 30
hit_registered = False
reset_position = (10, 250)
enemy_reset_position = (WINDOW_WIDTH - 250 - 10, 250)
is_paused = False


pygame.init()
pygame.font.init()
pygame.mixer.init()
font = pygame.font.SysFont(None, 28)  # You can change size or font as desired
score_font = pygame.font.SysFont(None, 40)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("HEMA House")
clock = pygame.time.Clock()

background = pygame.image.load("background.jpeg") 
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

menu = MenuSystem(screen, font, background)



player = Fencer(
    mid_sheet=r"Sprites\Player\Mid.png",
    high_sheet=r"Sprites\Player\High.png",
    low_sheet=r"Sprites\Player\Low.png",
    transition_sheet="Sprites/Player/Transitions.png",
    position=(10, 250),
    cut_direction=1
)

enemy = Fencer(
    mid_sheet=r"Sprites\Opp\Mid.png",
    high_sheet=r"Sprites\Opp\High.png",
    low_sheet=r"Sprites\Opp\Low.png",
    transition_sheet="Sprites/Opp/Transitions.png",
    position=(WINDOW_WIDTH - 250 - 10, 250),
    cut_direction=-1
)


player.opp = enemy
enemy.opp = player

game_manager = GameManager(
    player=player,
    enemy=enemy,
    reset_position=(10, 250),
    enemy_reset_position=(WINDOW_WIDTH - 250 - 10, 250)
)


ai_controller = AIController(fencer=enemy, opponent=player)

# Main loop
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # If we're in the menu, send input to the menu
        if menu.state in ("menu", "how_to_play"):
            menu.handle_event(event)
            continue
        if game_manager.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            menu.state = 'menu'
            pygame.event.clear(pygame.KEYDOWN)
            game_manager.reset_game()

        elif menu.in_game():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    is_paused = not is_paused
                    continue  # Skip further input if toggling pause
                if event.key == pygame.K_SPACE:
                    player.cut()
                elif event.key == pygame.K_a:
                    player.start_move(direction=-1)
                elif event.key == pygame.K_d:
                    player.start_move(direction=1)
                elif event.key == pygame.K_w:
                    player.change_guard(-1)
                elif event.key == pygame.K_s:
                    player.change_guard(1)

    if not menu.in_game():
        menu.update()
    if menu.in_game():
        screen.blit(background, (0, 0))

        if not game_manager.game_over and not is_paused:
            ai_controller.update()
            game_manager.update()

        enemy.draw(screen)
        player.draw(screen)
        player_score_text = score_font.render(f"{game_manager.player_score}", True, (0, 255, 0))
        screen.blit(player_score_text, (20, 20))
        enemy_score_text = score_font.render(f"{game_manager.enemy_score}", True, (255, 0, 0))  # Red
        screen.blit(enemy_score_text, (WINDOW_WIDTH - enemy_score_text.get_width() - 20, 20))
        if is_paused:
            pause_text = "Paused"
            menu.draw_text_with_outline(pause_text, (WINDOW_WIDTH - menu.font.size(pause_text)[0]) // 2, 200, text_color=(0, 0, 0))

        if game_manager.game_over:
            # Draw semi-transparent white overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((255, 255, 255))
            screen.blit(overlay, (0, 0))

            # Victory or Defeat message
            message = "Victory!" if game_manager.winner == 'player' else "Defeat!"
            prompt = "Press SPACE to return to Menu"
            

            # Use menu's draw_text_with_outline
            menu.draw_text_with_outline(message, (WINDOW_WIDTH - menu.font.size(message)[0]) // 2, 200, text_color=(0, 0, 0))
            menu.draw_text_with_outline(prompt, (WINDOW_WIDTH - menu.font.size(prompt)[0]) // 2, 300, text_color=(0, 0, 0))


    pygame.display.flip()



pygame.quit()
sys.exit()