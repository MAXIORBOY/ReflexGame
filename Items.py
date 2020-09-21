import pygame
import os
import numpy as np
from Highscores import Highscores


class Backgrounds:
    def __init__(self):
        self.background_main = pygame.image.load('backgrounds/main.jpg')
        self.background_levels = pygame.image.load('backgrounds/levels.jpg')


class Grid:
    def __init__(self, window_width, window_height, sprite_dimension):
        self.window_width = window_width
        self.window_height = window_height
        self.sprite_dimension = sprite_dimension
        self.grid = []
        self.create_grid()

    def create_grid(self):
        for i in range(int(self.window_width / self.sprite_dimension)):
            for j in range(int(self.window_height / self.sprite_dimension)):
                self.grid.append((i * self.sprite_dimension, j * self.sprite_dimension))


class Sounds:
    def __init__(self):
        self.correct_sound = pygame.mixer.Sound('sounds/correct.wav')
        self.wrong_sound = pygame.mixer.Sound('sounds/wrong.wav')
        self.miss_sound = pygame.mixer.Sound('sounds/miss.wav')

    @ staticmethod
    def play_background_music(kind):
        pygame.mixer.music.stop()
        pygame.mixer.music.set_volume(0.6)
        if kind == 'main':
            pygame.mixer.music.load('sounds/background_main.mp3')
            pygame.mixer.music.play(-1)
        elif kind == 'level':
            pygame.mixer.music.load('sounds/level.mp3')
            pygame.mixer.music.play(1)


class Sprites:
    def __init__(self):
        self.sprites = {'apple': pygame.image.load('sprites/apple.png'),
                        'bananas': pygame.image.load('sprites/bananas.png'),
                        'grapes': pygame.image.load('sprites/grapes.png'),
                        'lemon': pygame.image.load('sprites/lemon.png'),
                        'orange': pygame.image.load('sprites/orange.png'),
                        'peach': pygame.image.load('sprites/peach.png'),
                        'pear': pygame.image.load('sprites/pear.png'),
                        'pineapple': pygame.image.load('sprites/pineapple.png'),
                        'plum': pygame.image.load('sprites/plum.png'),
                        'watermelon': pygame.image.load('sprites/watermelon.png')}
        self.available_sprites = list(self.sprites.keys())
        self.sprite_dimension = 80


class Text:
    def __init__(self, window_width, window_height, color, text, font, x_pos_mod=1.0, y_pos_mod=1.0):
        self.window_width = window_width
        self.window_height = window_height
        self.color = color
        self.text = text
        self.font = font
        self.x_pos_mod = x_pos_mod
        self.y_pos_mod = y_pos_mod
        self.text_width, self.text_height = (0, 0)
        self.x = 0
        self.y = 0
        self.calculate_text_position()

    def calculate_text_position(self):
        self.text_width, self.text_height = self.font.size(self.text)
        self.x = int(self.x_pos_mod * (self.window_width / 2 - self.text_width / 2))
        self.y = int(self.y_pos_mod * (self.window_height / 2 - self.text_height / 2))

    def modify_text(self, new_text):
        self.text = new_text
        self.calculate_text_position()

    def draw(self, window):
        window.blit(self.font.render(self.text, True, self.color), (self.x, self.y))


class Button:
    def __init__(self, window_width, window_height, color, over_color, width, height, text, value, x_pos_mod=1.0, y_pos_mod=1.0):
        self.window_width = window_width
        self.window_height = window_height
        self.color = color
        self.over_color = over_color
        self.current_color = color
        self.width = width
        self.height = height
        self.text = text
        self.value = value
        self.x_pos_mod = x_pos_mod
        self.y_pos_mod = y_pos_mod
        self.x = 0
        self.y = 0
        self.calculate_position()

    def calculate_position(self):
        self.x = int(self.x_pos_mod * (self.window_width / 2 - self.width / 2))
        self.y = int(self.y_pos_mod * (self.window_height / 2 - self.height / 2))

    def draw(self, window):
        pygame.draw.rect(window, self.current_color, (self.x, self.y, self.width, self.height), 0)
        tx = self.text.font.render(self.text.text, True, (0, 0, 0))

        self.text.x, self.text.y = int(self.x + (self.width / 2 - tx.get_width() / 2)), int(self.y + (self.height / 2 - tx.get_height() / 2))
        self.text.draw(window)

    def is_mouse_over(self, mouse_pos):
        if self.x < mouse_pos[0] < self.x + self.width:
            if self.y < mouse_pos[1] < self.y + self.height:
                self.current_color = self.over_color
                return True

        self.current_color = self.color
        return False


class FontCreator:
    def __init__(self, font_name, font_size):
        self.font_name = font_name
        self.font_size = font_size

    def create_font(self):
        return pygame.font.SysFont(self.font_name, self.font_size)


class TimeMeasures:
    def __init__(self, strike_time_penalty=3):
        self.reaction_time = 0
        self.average_time = 0
        self.min_reaction_time = np.inf
        self.max_reaction_time = 0
        self.final_time = 0
        self.round_times = {}
        self.strikes = 0
        self.strike_time_penalty_s, self.strike_time_penalty_ms = strike_time_penalty, strike_time_penalty * 1000

    def build_total_and_average_time(self):
        non_negative_values = 0
        for reaction_time in list(self.round_times.values()):
            if reaction_time > 0:
                self.reaction_time += reaction_time
                non_negative_values += 1

        if non_negative_values:
            self.average_time = self.reaction_time / non_negative_values

    def build_min_max(self):
        for reaction_time in list(self.round_times.values()):
            if self.min_reaction_time > reaction_time > 0:
                self.min_reaction_time = reaction_time
            if self.max_reaction_time < reaction_time and reaction_time > 0:
                self.max_reaction_time = reaction_time

    def build_final_time(self):
        self.final_time = self.strike_time_penalty_ms * self.strikes + self.reaction_time

    def round_and_convert_to_seconds(self):
        self.reaction_time = round(self.reaction_time / 1000, 3)
        self.average_time = round(self.average_time / 1000, 3)
        self.min_reaction_time = round(self.min_reaction_time / 1000, 3)
        self.max_reaction_time = round(self.max_reaction_time / 1000, 3)
        self.final_time = round(self.final_time / 1000, 3)

        for key in list(self.round_times.keys()):
            if self.round_times[key] > 0:
                self.round_times[key] = round(self.round_times[key] / 1000, 3)

    def end_level_update(self):
        self.build_total_and_average_time()
        self.build_min_max()
        self.build_final_time()
        self.round_and_convert_to_seconds()


class Window:
    def __init__(self, window_width, window_height, window_title):
        self.window_width = window_width
        self.window_height = window_height
        self.window_fill_color = (255, 255, 255)
        self.screen_width, self.screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.window = None
        pygame.display.set_caption(window_title)
        self.prepare_window()

    def prepare_window(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0.7 * (self.screen_width - self.window_width) / 2, 0.7 * (self.screen_height - self.window_height) / 2)
        self.window = pygame.display.set_mode((self.window_width, self.window_height))

    def change_resolution(self, new_resolution):
        self.window_width, self.window_height = new_resolution
        self.prepare_window()


class Description:
    def __init__(self, root, description_text_strings):
        self.root = root
        self.text_description_strings = description_text_strings
        self.countdown_string = 'Level starts in: '
        self.backgrounds = Backgrounds()
        self.texts = []
        self.create_texts()
        self.status = True

    def create_texts(self):
        for i in range(len(self.text_description_strings)):
            self.texts.append(Text(window_width=self.root.window_width, window_height=self.root.window_height, color=(0, 0, 0), text=self.text_description_strings[i], font=FontCreator('Comic Sans MS', 22).create_font(), y_pos_mod=0.2 * (i + 1)))
        self.texts.append(Text(window_width=self.root.window_width, window_height=self.root.window_height, color=(0, 0, 0), text=self.countdown_string, font=FontCreator('Comic Sans MS', 20).create_font()))

    def draw(self):
        self.root.window.blit(self.backgrounds.background_levels, (0, 0))
        for text in self.texts:
            text.draw(self.root.window)
        pygame.display.update()

    def description_window(self):
        for i in range(5, 0, -1):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.status = False
            if not self.status:
                break
            self.texts[-1].modify_text(self.countdown_string + str(i))
            self.draw()
            pygame.time.delay(1000)


class Results:
    def __init__(self, root, level_number):
        self.root = root
        self.texts, self.buttons = {}, []
        self.names = ['Total react. time: ', 'Avg. react. time: ', 'Min. react. time: ', 'Max. react. time: ', 'Strikes: ', 'Final react. time: ']
        self.level_number = level_number
        self.highscores = Highscores('scores.hdf5')
        self.status = True
        self.backgrounds = Backgrounds()
        self.create_texts()
        self.create_buttons()

    def create_texts(self):
        keys = ['total_time', 'avg_time', 'max_time', 'min_time', 'strikes', 'final_time']
        for i in range(len(keys)):
            self.texts[keys[i]] = Text(window_width=self.root.window_width, window_height=self.root.window_height, color=(0, 0, 0), text=' ', font=FontCreator('Comic Sans MS', 25).create_font(), x_pos_mod=0.05, y_pos_mod=0.2 * (i + 1))

    def create_buttons(self):
        self.buttons.append(Button(window_width=self.root.window_width, window_height=self.root.window_height, color=(204, 153, 102), over_color=(191, 128, 64), width=125, height=35, text=Text(window_width=self.root.window_width, window_height=self.root.window_height, color=(0, 0, 0), text='FINISH', font=FontCreator('Comic Sans MS', 25).create_font()), value=None, y_pos_mod=1.8))

    def draw(self):
        self.root.window.blit(self.backgrounds.background_levels, (0, 0))
        for key in list(self.texts.keys()):
            self.texts[key].draw(self.root.window)
        for button in self.buttons:
            button.draw(self.root.window)
        pygame.display.update()

    def result_window(self, time_measures):
        self.highscores.save_scores(self.highscores.get_current_level_scores(self.level_number) + [time_measures.final_time], self.level_number)

        def get_current_score_index():
            index = None
            best_scores = self.highscores.get_current_level_scores(self.level_number)
            if np.float32(time_measures.final_time) in best_scores:
                index = best_scores.index(np.float32(time_measures.final_time))

            return index

        current_score_index = get_current_score_index()
        loop_status = True
        if time_measures.reaction_time:
            self.texts['total_time'].modify_text(self.names[0] + str(time_measures.reaction_time) + ' sec.')
            self.texts['avg_time'].modify_text(self.names[1] + str(time_measures.average_time) + ' sec.')
            self.texts['min_time'].modify_text(self.names[2] + str(time_measures.min_reaction_time) + ' sec.')
            self.texts['max_time'].modify_text(self.names[3] + str(time_measures.max_reaction_time) + ' sec.')
        else:
            self.texts['total_time'].modify_text(self.names[0] + '-----')
            self.texts['avg_time'].modify_text(self.names[1] + '-----')
            self.texts['min_time'].modify_text(self.names[2] + '-----')
            self.texts['max_time'].modify_text(self.names[3] + '-----')

        if time_measures.strikes:
            self.texts['strikes'].modify_text(self.names[4] + str(time_measures.strikes) + ' (+' + str(time_measures.strikes * time_measures.strike_time_penalty_s) + ' sec. penalty)')
        else:
            self.texts['strikes'].modify_text(self.names[4] + str(time_measures.strikes))

        if current_score_index is not None:
            self.texts['final_time'].modify_text(self.names[5] + str(time_measures.final_time) + ' sec.' + ' (#' + str(current_score_index + 1) + ' Result)')
        else:
            self.texts['final_time'].modify_text(self.names[5] + str(time_measures.final_time) + ' sec.')

        while loop_status:
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.is_mouse_over(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN:
                        loop_status = False
                if event.type == pygame.QUIT:
                    self.status = False
                    loop_status = False

            self.draw()
