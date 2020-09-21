import random
from Items import *

pygame.init()


class Screens:
    def __init__(self, rounds=5):
        self.rounds = rounds
        self.min_fake_screens = 1
        self.max_fake_screens = 6
        self.focus_screen_display_time = 1000
        self.min_fake_screen_display_time = 500
        self.max_fake_screen_display_time = 1500
        self.colors_dict = self.get_possible_colors()
        self.focus_color = random.choice(list(self.colors_dict.keys()))
        self.screens_dict = {}
        self.current_screen_index = 0
        self.focus_color_indexes = []
        self.generate_screens()
        self.create_focus_color_indexes_list()

    @staticmethod
    def get_possible_colors():
        return {'green': (0, 255, 0), 'yellow': (255, 255, 0), 'red': (255, 0, 0), 'orange': (255, 128, 0), 'blue': (0, 0, 255), 'purple': (153, 51, 255), 'brown': (115, 77, 38), 'gray': (153, 153, 153), 'black': (0, 0, 0), 'white': (255, 255, 255)}

    def generate_screens(self):
        screens_colors = []
        screens_times = []
        total_time = 0

        for i in range(self.rounds):
            fake_screens_number = random.randint(self.min_fake_screens, self.max_fake_screens)
            fake_screen_possible_colors = list(self.colors_dict.keys())
            fake_screen_possible_colors.remove(self.focus_color)
            for _ in range(fake_screens_number):
                screens_colors.append(random.choice(fake_screen_possible_colors))
                total_time += int(random.random() * (self.max_fake_screen_display_time - self.min_fake_screen_display_time) + self.min_fake_screen_display_time)
                screens_times.append(total_time)

            screens_colors.append(self.focus_color)
            total_time += self.focus_screen_display_time
            screens_times.append(total_time)

        self.screens_dict['colors'] = screens_colors
        self.screens_dict['times'] = screens_times

    def get_current_screen_color(self, clock_time):
        index = self.current_screen_index
        while self.screens_dict['times'][index] < clock_time:
            if index + 1 < len(self.screens_dict['times']):
                index += 1
            else:
                break

        self.current_screen_index = index
        return self.screens_dict['colors'][index]

    def create_focus_color_indexes_list(self):
        previous_index = -1
        for i in range(self.rounds):
            self.focus_color_indexes.append(self.screens_dict['colors'].index(self.focus_color, previous_index + 1))
            previous_index = self.focus_color_indexes[-1]


class Level2:
    def __init__(self, root, master_window):
        self.root = root
        self.master_window = master_window
        self.sounds = Sounds()
        self.screens = Screens()
        self.description = Description(self.root, ['Press SPACEBAR (ASAP) whenever the screen turns ' + self.screens.focus_color])
        self.time_measures = TimeMeasures()
        self.results = Results(self.root, 2)
        self.button_pressed = [False] * len(self.screens.screens_dict['colors'])
        self.current_round = -1
        self.status = True

    def calculate_misses(self):
        if self.current_round in self.screens.focus_color_indexes:
            if not self.button_pressed[self.current_round]:
                self.sounds.miss_sound.play()
                self.time_measures.strikes += 1
                self.time_measures.round_times[self.current_round] = -1

    def main_loop(self):
        loop_status = True
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < self.screens.screens_dict['times'][-1] and loop_status:
            self.root.window.fill(self.screens.colors_dict[self.screens.get_current_screen_color(pygame.time.get_ticks() - start)])
            pygame.display.update()
            if self.current_round != self.screens.current_screen_index:
                self.calculate_misses()
                self.current_round = self.screens.current_screen_index
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.status = False
                    loop_status = False
            if pygame.key.get_pressed()[pygame.K_SPACE] and not self.button_pressed[self.screens.current_screen_index]:
                stop = pygame.time.get_ticks()
                self.button_pressed[self.screens.current_screen_index] = True
                if self.screens.screens_dict['colors'][self.screens.current_screen_index] == self.screens.focus_color:
                    self.sounds.correct_sound.play()
                    self.time_measures.round_times[self.screens.current_screen_index] = (stop - start) - self.screens.screens_dict['times'][self.screens.current_screen_index - 1]
                else:
                    self.sounds.wrong_sound.play()
                    self.time_measures.strikes += 1

        self.calculate_misses()

    def run_level(self):
        self.description.description_window()
        if self.description.status:
            self.main_loop()
            if self.status:
                self.time_measures.end_level_update()
                self.results.result_window(self.time_measures)
                if not self.results.status:
                    self.master_window.turn_off_master()
            else:
                self.master_window.turn_off_master()
        else:
            self.master_window.turn_off_master()
