import random
from Items import *

pygame.init()


class Equations:
    def __init__(self, equations_number=5):
        self.equations = []
        self.equation_show_time = 2000
        self.min_interval_time = 500
        self.max_interval_time = 1500
        self.equations_correctness = []
        self.times = []

        for _ in range(equations_number):
            self.create_equation()

        self.create_time_scenario()
        self.current_index = 0

    def create_equation(self):
        first_number, second_number, sign = random.randint(1, 100), random.randint(1, 100), random.choice(['+', '-'])
        self.equations_correctness.append(random.choice([False, True]))

        if sign == '-':
            if first_number < second_number:
                first_number, second_number = second_number, first_number
            result = first_number - second_number

        else:
            result = first_number + second_number

        if not self.equations_correctness[-1]:
            mods_list = list(range(-9, 0))
            mods_list.extend(list(range(1, 10)))
            result += random.choice(mods_list)

        self.equations.append(str(first_number) + ' ' + sign + ' ' + str(second_number) + ' ' + ' = ' + str(result))

    def create_time_scenario(self):
        total_time = 0
        for i in range(2 * len(self.equations)):
            if i % 2 == 0:
                total_time += int(random.random() * (self.max_interval_time - self.min_interval_time) + self.min_interval_time)
            else:
                total_time += self.equation_show_time

            self.times.append(total_time)

    def get_current_round_index(self, clock_time):
        index = self.current_index
        while self.times[index] < clock_time:
            if index + 1 < len(self.times):
                index += 1
            else:
                break

        self.current_index = index


class Level1:
    def __init__(self, root, master_window):
        self.root = root
        self.master_window = master_window
        self.sounds = Sounds()
        self.equations = Equations()
        self.description = Description(self.root, ['Determine whether the given equation is correct or wrong.'])
        self.time_measures = TimeMeasures()
        self.results = Results(self.root, 1)
        self.backgrounds = Backgrounds()
        self.buttons = []
        self.texts_main = {}
        self.names = ['Stage ']
        self.status = True
        self.buttons_pressed = [False] * len(self.equations.equations)
        self.current_round = -1
        self.create_buttons()
        self.create_texts()

    def create_buttons(self):
        self.buttons.append(Button(window_width=self.root.window_width, window_height=self.root.window_height, color=(0, 255, 0), over_color=(0, 200, 0), width=150, height=45, text=Text(window_width=150, window_height=45, color=(0, 0, 0), text='CORRECT', font=FontCreator('Comic Sans MS', 30).create_font()), value=True, x_pos_mod=0.65))
        self.buttons.append(Button(window_width=self.root.window_width, window_height=self.root.window_height, color=(255, 0, 0), over_color=(200, 0, 0), width=150, height=45, text=Text(window_width=150, window_height=45, color=(0, 0, 0), text='WRONG', font=FontCreator('Comic Sans MS', 30).create_font()), value=False, x_pos_mod=1.35))

    def create_texts(self):
        self.texts_main['equation'] = Text(window_width=self.root.window_width, window_height=self.root.window_height, color=(0, 0, 0), text='', font=FontCreator('Comic Sans MS', 40).create_font(), y_pos_mod=0.5)

    def main_window_draw(self):
        self.root.window.blit(self.backgrounds.background_levels, (0, 0))
        if self.current_round % 2 == 1:
            for button in self.buttons:
                button.draw(self.root.window)
            for key in list(self.texts_main.keys()):
                self.texts_main[key].draw(self.root.window)
        pygame.display.update()

    def calculate_misses(self):
        if self.current_round > 0:
            if self.current_round % 2 == 1 and not self.buttons_pressed[int(self.current_round / 2)]:
                self.sounds.miss_sound.play()
                self.time_measures.round_times[int(self.current_round / 2)] = -1
                self.time_measures.strikes += 1

    def main_loop(self):
        loop_status = True
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < self.equations.times[-1] and loop_status:
            self.equations.get_current_round_index(pygame.time.get_ticks() - start)
            if self.current_round != self.equations.current_index:
                self.calculate_misses()
                self.current_round = self.equations.current_index
            self.texts_main['equation'].modify_text(str(self.equations.equations[int(self.current_round / 2)]))
            self.main_window_draw()
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.is_mouse_over(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN and not self.buttons_pressed[int(self.current_round / 2)]:
                        stop = pygame.time.get_ticks()
                        self.buttons_pressed[int(self.current_round / 2)] = True
                        if self.equations.equations_correctness[int(self.current_round / 2)] == button.value:
                            self.sounds.correct_sound.play()
                            self.time_measures.round_times[int(self.current_round / 2)] = (stop - start) - self.equations.times[self.current_round - 1]
                        else:
                            self.time_measures.strikes += 1
                            self.sounds.wrong_sound.play()

                if event.type == pygame.QUIT:
                    loop_status = False
                    self.status = False

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
