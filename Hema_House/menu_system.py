import pygame

class MenuSystem:
    def __init__(self, screen, font, background):
        self.screen = screen
        self.font = font
        self.background = background
        self.options = ["Start", "How to Play"]
        self.selected_index = 0
        self.logo = pygame.image.load("logo.png").convert_alpha()
        self.logo = pygame.transform.scale(self.logo, (300, 150))  # Resize as needed
        self.state = "menu"  # Can be 'menu', 'how_to_play', or 'game'

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key in (pygame.K_w, pygame.K_UP):
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    selected = self.options[self.selected_index]
                    if selected == "Start":
                        pygame.event.clear(pygame.KEYDOWN)
                        self.state = "game"
                        return
                    elif selected == "How to Play":
                        pygame.event.clear(pygame.KEYDOWN)
                        self.state = "how_to_play"

            elif self.state == "how_to_play":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.state = "game"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"

    def draw_text_with_outline(self, text, x, y, text_color, outline_color=(255, 255, 255), thickness=1):
        rendered = self.font.render(text, True, text_color)
        outline = self.font.render(text, True, outline_color)

        for dx in [-thickness, 0, thickness]:
            for dy in [-thickness, 0, thickness]:
                if dx != 0 or dy != 0:
                    self.screen.blit(outline, (x + dx, y + dy))
        self.screen.blit(rendered, (x, y))

    def draw_menu(self):
        self.screen.blit(self.background,(0, 0))
        self.screen.blit(self.logo, ((800 - self.logo.get_width()) // 2, 50))

        for idx, option in enumerate(self.options):
            text = self.font.render(option, True, (0, 0, 0))
            x = (800 - text.get_width()) // 2
            y = 250 + idx * 60

            # Draw white outline + black text
            self.draw_text_with_outline(option, x, y, text_color=(0, 0, 0))

            # Yellow box to left of selected option
            if idx == self.selected_index:
                pygame.draw.rect(self.screen, (255, 255, 0), (x - 40, y, 20, text.get_height()))

    def draw_how_to_play(self):
        self.screen.blit(self.background,(0, 0))
        lines = [
            "Controls:",
            "- A/D Move", 
            "- W/S Change Guard", 
            "- Space: Attack",
            "",
            "",
            "",
            "",
            "",
            "",
            "Guards:",
            "- Each fencer has 3 guards: High, Middle, Low",
            "- A guard blocks attacks at its level and any adjacent levels",
            "- Example: Middle Guard blocks High and Low attacks,", 
            "                     High Guard only blocks High and Middle Attacks",
            "- Attacks are only vulnerable at the beginning and end of the swing",
            "",
            "Press Space to begin. Press ESC to return to the Menu"
        ]
        for i, line in enumerate(lines):
            self.draw_text_with_outline(line, 50, 50 + i * 30, text_color=(0, 0, 0))

    def update(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "how_to_play":
            self.draw_how_to_play()

    def in_game(self):
        return self.state == "game"




