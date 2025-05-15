import random
from fencer import GuardState

class AIController:
    def __init__(self, fencer, opponent, step_distance=30):
        self.fencer = fencer
        self.opponent = opponent
        self.step_distance = step_distance
        self.action_timer = 15  # Frames until next decision
        self.cooldown = 15     # Time between actions (in frames)

    def update(self):
        # Only act if not paused or in the middle of a cut
        if self.fencer.is_cutting or self.fencer.is_moving:
            return

        self.action_timer -= 1
        if self.action_timer <= 0:
            self.choose_action()
            self.action_timer = self.cooldown

    def choose_action(self):
        distance = abs(self.fencer.rect.left - self.opponent.rect.right)

        if distance > 8 * self.step_distance:
            # Move closer to the player
            direction = -1 if self.fencer.rect.left > self.opponent.rect.right else 1
            self.fencer.start_move(direction)
        else:
            # Choose a random action when in range
            action = random.choice([
                "step_forward",
                "step_backward",
                "cut",
                "adjust_guard",
                "change_guard_and_hold",
                "change_guard_and_cut"
            ])

            if action == "step_forward":
                if distance > 1:
                    self.fencer.start_move(1 if self.fencer.cut_direction == -1 else -1)
                else:
                    return
            elif action == "step_backward":
                self.fencer.start_move(-1 if self.fencer.cut_direction == -1 else 1)
            elif action == "cut":
                self.fencer.cut()
            elif action == "adjust_guard":
                self.adjust_guard_toward_player()
            elif action == "change_guard_and_hold":
                self.random_guard()
            elif action == "change_guard_and_cut":
                self.random_guard(cut_after=True)

    def adjust_guard_toward_player(self):
        def adjust_guard_toward_player(self):
            target_guard = self.opponent.guard_state
            if self.fencer.guard_state == target_guard:
                return  # Already matching
            elif self.fencer.guard_state.value < target_guard.value:
                self.fencer.change_guard(1)  # Move guard down towards opponent's
            else:
                self.fencer.change_guard(-1)  # Move guard up towards opponent's

    def random_guard(self, cut_after=False):
        target_guard = random.choice(list(GuardState))
        if self.fencer.guard_state == target_guard:
            if cut_after:
                self.fencer.cut()
            return  # Already in desired guard
        elif self.fencer.guard_state.value < target_guard.value:
            self.fencer.change_guard(1, cut_after=cut_after)
        else:
            self.fencer.change_guard(-1, cut_after=cut_after)




