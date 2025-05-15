import pygame
from enum import Enum

class GuardState(Enum):
    HIGH = 1
    MID = 2
    LOW = 3

class Fencer(pygame.sprite.Sprite):
    def __init__(self, mid_sheet, high_sheet, low_sheet, transition_sheet, position, cut_direction=1, ANIMATION_DELAY=5, opp=None):
        super().__init__()
        self.frame_width = 250
        self.frame_height = 300
        self.spacing = 20
        self.WINDOW_WIDTH = 800
        self.ANIMATION_DELAY = ANIMATION_DELAY

        self.mid_sheet = pygame.image.load(mid_sheet).convert_alpha()
        self.high_sheet = pygame.image.load(high_sheet).convert_alpha()
        self.low_sheet = pygame.image.load(low_sheet).convert_alpha()

        self.opp = opp

        # State
        self.guard_state = GuardState.MID
        self.attack_guard_state = GuardState.MID
        self.is_cutting = False
        self.is_moving = False
        self.is_transitioning = False

        # Movement
        self.move_direction = 0
        self.move_progress = 0
        self.total_move_frames = 10
        self.move_distance = 30

        #Transitions
        self.transition_direction = 0  # -1 for up (to High), 1 for down (to Low), reverse for back to Mid
        self.transition_progress = 0
        self.total_transition_frames = 6

        # Cuts
        self.cut_distance = int(1.5 * self.move_distance)
        self.cut_direction = cut_direction
        self.cut_total_frames = 24
        self.cut_anim_progress = 0
        self.pending_cut_after_transition = False

        # Pushback
        self.pushback_active = False
        self.pushback_progress = 0
        self.total_pushback_frames = 7
        self.pushback_per_frame = self.cut_distance // self.total_pushback_frames

        # Animations
        self.mid_walk_frames = self.load_frames(self.mid_sheet, y=400, count=5)
        self.high_walk_frames = self.load_frames(self.high_sheet, y=400, count=5)
        self.low_walk_frames = self.load_frames(self.low_sheet, y=400, count=5)

        self.mid_cut_frames = self.load_frames(self.mid_sheet, y=0, count=8)
        self.high_cut_frames = self.load_frames(self.high_sheet, y=0, count=8)
        self.low_cut_frames = self.load_frames(self.low_sheet, y=0, count=8)

        self.transition_sheet = pygame.image.load(transition_sheet).convert_alpha()

        self.mid_to_high_frames = self.load_frames(self.transition_sheet, y=0, count=3)
        self.mid_to_low_frames = self.load_frames(self.transition_sheet, y=400, count=3)

        # Audio
        self.cut_sound = pygame.mixer.Sound("Audio/Cut.mp3")
        self.tap_sounds = [
            pygame.mixer.Sound("Audio/Tap_1.mp3"),
            pygame.mixer.Sound("Audio/Tap_2.mp3"),
            pygame.mixer.Sound("Audio/Tap_3.mp3")
]

        # Initial image and position
        self.frame_index = 0
        self.image = self.mid_walk_frames[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = position

    def load_frames(self, sheet, y, count):
        frames = []
        for i in range(count):
            x = i * (self.frame_width + self.spacing)
            rect = pygame.Rect(x, y, self.frame_width, self.frame_height)
            frames.append(sheet.subsurface(rect))
        return frames

    def start_move(self, direction):
        if not self.is_cutting and not self.is_moving:
            self.is_moving = True
            self.move_direction = direction
            self.move_progress = 0
            self.frame_index = 0

    def move_x(self, delta):
        new_x = self.rect.x + delta
        if self.opp and not self.is_cutting and not self.pushback_active:
            if delta > 0:
                if self.rect.right <= self.opp.rect.left and new_x + self.frame_width > self.opp.rect.left:
                    new_x = self.opp.rect.left - self.frame_width
            elif delta < 0:
                if self.rect.left >= self.opp.rect.right and new_x < self.opp.rect.right:
                    new_x = self.opp.rect.right
        new_x = max(10, min(self.WINDOW_WIDTH - self.frame_width - 10, new_x))
        self.rect.x = new_x

    def change_guard(self, direction, cut_after=False):
        if self.is_cutting or self.is_moving or self.is_transitioning:
            return  # Don't allow while busy

        if self.guard_state == GuardState.MID:
            if direction == -1:
                self.is_transitioning = True
                self.transition_direction = -1  # Mid to High
            elif direction == 1:
                self.is_transitioning = True
                self.transition_direction = 1  # Mid to Low
        elif self.guard_state == GuardState.HIGH and direction == 1:
            self.is_transitioning = True
            self.transition_direction = 1  # High to Mid
        elif self.guard_state == GuardState.LOW and direction == -1:
            self.is_transitioning = True
            self.transition_direction = -1  # Low to Mid

        self.transition_progress = 0
        self.pending_cut_after_transition = cut_after

    def cut(self):
        if not self.is_cutting:
            self.is_cutting = True
            self.cut_anim_progress = 0
            self.frame_index = 0
            self.attack_guard_state = self.guard_state

    def can_hit(self):
        return self.is_cutting and self.frame_index in (5, 6)

    def is_protected_from(self, incoming_cut_guard):
        if self.is_cutting:
            if not (5 <= self.frame_index <= 6):
                return False  # vulnerable
        if self.guard_state == GuardState.MID:
            return True
        elif self.guard_state == GuardState.HIGH:
            return incoming_cut_guard in (GuardState.HIGH, GuardState.MID)
        elif self.guard_state == GuardState.LOW:
            return incoming_cut_guard in (GuardState.MID, GuardState.LOW)
        return False

    def update_animation(self):

        if self.is_transitioning:
            if self.transition_direction == -1:
                # Up (Mid to High or Low to Mid reverse)
                frames = self.mid_to_high_frames if self.guard_state == GuardState.MID else list(reversed(self.mid_to_high_frames))
            else:
                # Down (Mid to Low or High to Mid reverse)
                frames = self.mid_to_low_frames if self.guard_state == GuardState.MID else list(reversed(self.mid_to_low_frames))

            frame_index = (self.transition_progress * len(frames)) // self.total_transition_frames
            frame_index = min(frame_index, len(frames) - 1)
            self.image = frames[frame_index]

            self.transition_progress += 1
            if self.transition_progress >= self.total_transition_frames:
                self.is_transitioning = False
                # Update guard state after transition completes
                if self.guard_state == GuardState.MID:
                    self.guard_state = GuardState.HIGH if self.transition_direction == -1 else GuardState.LOW
                else:
                    self.guard_state = GuardState.MID

                if self.pending_cut_after_transition:
                    self.pending_cut_after_transition = False
                    self.cut()

            return  # Don't update movement or idle frames during transition
        # Cutting state
        if self.is_cutting:
            if self.attack_guard_state == GuardState.MID:
                cut_frames = self.mid_cut_frames
            elif self.attack_guard_state == GuardState.HIGH:
                cut_frames = self.high_cut_frames
            elif self.attack_guard_state == GuardState.LOW:
                cut_frames = self.low_cut_frames

            if self.cut_anim_progress < (self.cut_total_frames - 4):
                frame_index = (self.cut_anim_progress * len(cut_frames)) // (self.cut_total_frames - 4)
            else:
                frame_index = len(cut_frames) - 1  # cooldown hold

            frame_index = min(frame_index, len(cut_frames) - 1)
            self.frame_index = frame_index
            self.image = cut_frames[frame_index]

            lunge_step = self.cut_distance // 7
            pushback_step = self.cut_distance // self.total_pushback_frames

            if (
                self.opp and
                self.rect.colliderect(self.opp.rect) and
                self.opp.is_protected_from(self.attack_guard_state) and
                not self.pushback_active and
                frame_index < 7
            ):
                self.pushback_active = True
                self.pushback_progress = 0
                self.cut_sound.play()

            if self.pushback_active:
                self.move_x(-self.cut_direction * pushback_step)
                self.pushback_progress += 1
                if self.pushback_progress >= self.total_pushback_frames:
                    self.pushback_active = False
            elif frame_index < 7:
                self.move_x(lunge_step * self.cut_direction)

            self.cut_anim_progress += 1
            if self.cut_anim_progress >= self.cut_total_frames:
                self.is_cutting = False
                self.frame_index = 0
                self.image = self.get_idle_frame()

        # Moving state
        elif self.is_moving:
            frame_index = (self.move_progress * 5) // self.total_move_frames
            frame_index = min(frame_index, 4)

            walk_frames = self.get_walk_frames()
            self.image = walk_frames[frame_index]

            step = self.move_distance // self.total_move_frames
            self.move_x(step * self.move_direction)

            self.move_progress += 1
            if self.move_progress >= self.total_move_frames:
                self.is_moving = False
                self.frame_index = 0
                self.image = walk_frames[0]

        # Idle state
        else:
            self.image = self.get_idle_frame()

    def get_walk_frames(self):
        if self.guard_state == GuardState.MID:
            return self.mid_walk_frames
        elif self.guard_state == GuardState.HIGH:
            return self.high_walk_frames
        elif self.guard_state == GuardState.LOW:
            return self.low_walk_frames
        return self.mid_walk_frames  # fallback

    def get_idle_frame(self):
        return self.get_walk_frames()[0]

    def draw(self, surface):
        surface.blit(self.image, self.rect)
