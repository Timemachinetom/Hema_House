import random
from fencer import GuardState

class GameManager:
    def __init__(self, player, enemy, reset_position, enemy_reset_position, pause_duration=30):
        self.player = player
        self.enemy = enemy
        self.player_score = 0
        self.enemy_score = 0
        self.reset_position = reset_position
        self.enemy_reset_position = enemy_reset_position
        self.pause_duration = pause_duration
        self.pause_frames = 0
        self.hit_registered = False
        self.game_over = False
        self.winner = None

    def reset_game(self):
        self.player.rect.topleft = self.reset_position
        self.enemy.rect.topleft = self.enemy_reset_position

        self.player_score = 0
        self.enemy_score = 0
        self.pause_frames = 0
        self.hit_registered = False
        self.game_over = False
        self.winner = None

        for fencer in [self.player, self.enemy]:
            fencer.is_cutting = False
            fencer.is_moving = False
            fencer.is_transitioning = False
            fencer.pending_cut_after_transition = False 
            fencer.guard_state = GuardState.MID
            fencer.cut_anim_progress = 0
            fencer.move_progress = 0

    def update(self):
        if self.pause_frames > 0:
            self.pause_frames -= 1

            if self.pause_frames == 0:
                self.reset_positions()
                self.hit_registered = False
        else:
            self.player.update_animation()
            self.enemy.update_animation()
            if (
                self.player.rect.colliderect(self.enemy.rect) and
                not self.player.is_cutting and
                not self.enemy.is_cutting and
                self.player.rect.right == (self.enemy.rect.left -5)
            ):
                random.choice(self.player.tap_sounds).play()
            self.check_hits()

    def check_hits(self):
        if self.hit_registered:
            return

        player_hit_enemy = (
            self.player.can_hit() and
            not self.enemy.is_protected_from(self.player.attack_guard_state) and
            self.player.rect.colliderect(self.enemy.rect)
        )

        enemy_hit_player = (
            self.enemy.can_hit() and
            not self.player.is_protected_from(self.enemy.attack_guard_state) and
            self.enemy.rect.colliderect(self.player.rect)
        )

        if player_hit_enemy and enemy_hit_player:
            self.start_pause()
            self.hit_registered = True
        elif player_hit_enemy:
            self.player_score += 1
            self.start_pause()
            self.hit_registered = True

        elif enemy_hit_player:
            self.enemy_score += 1
            self.start_pause()
            self.hit_registered = True

        if self.player_score >= 5:
            self.game_over = True
            self.winner = "player"
        elif self.enemy_score >= 5:
            self.game_over = True
            self.winner = "enemy"

    def start_pause(self):
        self.pause_frames = self.pause_duration
        self.hit_registered = True

    def reset_positions(self):
        self.player.rect.topleft = self.reset_position
        self.enemy.rect.topleft = self.enemy_reset_position
        # Reset guards to MID
        self.player.guard_state = GuardState.MID
        self.enemy.guard_state = GuardState.MID

        # Ensure no lingering transitions
        self.player.is_transitioning = False
        self.enemy.is_transitioning = False

        # Reset animations to idle frame
        self.player.image = self.player.get_idle_frame()
        self.enemy.image = self.enemy.get_idle_frame()

        for fencer in [self.player, self.enemy]:
            fencer.is_cutting = False
            fencer.is_moving = False
            fencer.is_guarding = True
            fencer.cut_anim_progress = 0
            fencer.move_progress = 0
