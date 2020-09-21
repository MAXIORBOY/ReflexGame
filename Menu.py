from Items import *
from Level1 import Level1
from Level2 import Level2
from Level3 import Level3
from Highscores import Highscores
from Settings import Settings

pygame.init()


class MenuItemManager:
    def __init__(self):
        self.highscores = Highscores('scores.hdf5')
        self.highscores_texts = []
        self.highscores_position_dictionary = {}
        self.create_highscores_texts_and_positions()
        self.menus = {'Main': ('Main', 'Reflex Game', ['New Game', 'Highscores', 'Resolutions', 'Exit'], None, None, {3: (1.0, 1.9)}),
                      'Highscores': ('Highscores', 'Highscores', ['Back'], self.highscores_texts, self.highscores_position_dictionary, {0: (1.0, 1.9)}),
                      'Resolution': ('Resolution', 'Resolution', ['1280 x 720', '800 x 600', '640 x 480', 'Back'], None, None, {3: (1.0, 1.9)}),
                      'Levels': ('Levels', 'Select the level', ['Simple Math', 'Color Hunter', 'Fruit Clicker', 'Back'], None, None, {3: (1.0, 1.9)})}

    def create_highscores_texts_and_positions(self):
        hs_scores = []
        for i in range(self.highscores.number_of_levels):
            self.highscores_texts.append('Level ' + str(i + 1))

        positions_x = [2 / (self.highscores.number_of_levels + 1)] * self.highscores.number_of_levels
        for i in range(len(positions_x)):
            positions_x[i] *= (i + 1)

        for i in range(self.highscores.number_of_levels):
            self.highscores_position_dictionary[i] = (positions_x[i], 0.3)

        for i in range(self.highscores.number_of_levels):
            hs_level = list(self.highscores.get_current_level_scores(i + 1))
            for j in range(len(hs_level)):
                if hs_level[j] != np.inf:
                    hs_level[j] = str(hs_level[j])
                else:
                    hs_level[j] = '-----'

            hs_scores.append(hs_level)

        for i in range(len(hs_scores)):
            pos_x = positions_x[i]
            for j in range(len(hs_scores[i])):
                pos_y = 0.45 + (0.15 * j)
                self.highscores_texts.append(str(j + 1) + '. ' + hs_scores[i][j])
                self.highscores_position_dictionary[3 + 5 * i + j] = (pos_x, pos_y)


class Switchboard:
    def __init__(self, root, window_name, action_index, master_window):
        self.root = root
        self.window_name = window_name
        self.action_index = action_index
        self.master_window = master_window
        self.settings = Settings('settings.hdf5')

    def switch(self):
        if self.window_name == 'Main':
            if self.action_index == 1:
                Menu(self.root, MenuItemManager().menus['Levels'], self.master_window).run_level()
            elif self.action_index == 2:
                Menu(self.root, MenuItemManager().menus['Highscores'], self.master_window).run_level()
            elif self.action_index == 3:
                Menu(self.root, MenuItemManager().menus['Resolution'], self.master_window).run_level()
            elif self.action_index == 4:
                self.master_window.turn_off_master()
                Menu(self.root, MenuItemManager().menus['Main'], self.master_window, status=False).run_level()

        elif self.window_name == 'Highscores':
            if self.action_index == 1:
                Menu(self.root, MenuItemManager().menus['Main'], self.master_window).run_level()

        elif self.window_name == 'Resolution':
            resolutions = [(1280, 720), (800, 600), (640, 480)]
            if self.action_index == 1:
                self.settings.change_resolution(resolutions[0])
                self.root.change_resolution(resolutions[0])
                Menu(self.root, MenuItemManager().menus['Resolution'], self.master_window).run_level()
            elif self.action_index == 2:
                self.settings.change_resolution(resolutions[1])
                self.root.change_resolution(resolutions[1])
                Menu(self.root, MenuItemManager().menus['Resolution'], self.master_window).run_level()
            elif self.action_index == 3:
                self.settings.change_resolution(resolutions[2])
                self.root.change_resolution(resolutions[2])
                Menu(self.root, MenuItemManager().menus['Resolution'], self.master_window).run_level()
            elif self.action_index == 4:
                Menu(self.root, MenuItemManager().menus['Main'], self.master_window).run_level()

        elif self.window_name == 'Levels':
            if self.action_index == 1:
                self.master_window.sounds.play_background_music('level')
                Level1(self.root, self.master_window).run_level()
            elif self.action_index == 2:
                self.master_window.sounds.play_background_music('level')
                Level2(self.root, self.master_window).run_level()
            elif self.action_index == 3:
                self.master_window.sounds.play_background_music('level')
                Level3(self.root, self.master_window).run_level()
            elif self.action_index == 4:
                Menu(self.root, MenuItemManager().menus['Main'], self.master_window).run_level()


class Menu:
    def __init__(self, root, menus_obj, master_window, status=True, new_resolution=None):
        self.root = root
        if new_resolution is not None:
            self.root.change_resolution(new_resolution)
        self.window_name, self.title, self.available_options, self.additional_texts, self.add_texts_positioning, self.buttons_positioning = menus_obj
        self.master_window = master_window
        self.status = status
        if self.additional_texts is None:
            self.additional_texts = []
        if self.add_texts_positioning is None:
            self.add_texts_positioning = {}
        if self.buttons_positioning is None:
            self.buttons_positioning = {}
        self.sounds = Sounds()
        self.backgrounds = Backgrounds()
        self.texts = []
        self.buttons = []
        self.create_text()
        self.create_buttons()
        self.action_index = None

    def create_text(self):
        self.texts.append(Text(window_width=self.root.window_width, window_height=self.root.window_height, color=(0, 0, 0), text=self.title, font=FontCreator('Arial Black', 40).create_font(), y_pos_mod=0.05))
        for i in range(len(self.additional_texts)):
            x_mod, y_mod = self.add_texts_positioning.get(i, (1.0, 0.15 * (i + 1)))
            self.texts.append(Text(window_width=self.root.window_width, window_height=self.root.window_height, color=(0, 0, 0), text=self.additional_texts[i], font=FontCreator('Comic Sans MS', 25).create_font(), x_pos_mod=x_mod, y_pos_mod=y_mod))

    def create_buttons(self):
        for i in range(len(self.available_options)):
            x_mod, y_mod = self.buttons_positioning.get(i, (1.0, 0.35 * (i + 1)))
            self.buttons.append(Button(window_width=self.root.window_width, window_height=self.root.window_height, color=(255, 128, 0), over_color=(235, 108, 0), width=175, height=37, text=Text(window_width=165, window_height=30, color=(0, 0, 0), text=self.available_options[i], font=FontCreator('Comic Sans MS', 25).create_font()), value=i + 1, x_pos_mod=x_mod, y_pos_mod=y_mod))

    def draw(self):
        self.root.window.blit(self.backgrounds.background_main, (0, 0))
        for text in self.texts:
            text.draw(self.root.window)
        for button in self.buttons:
            button.draw(self.root.window)

        pygame.display.update()

    def run_level(self):
        loop_status = self.status
        while loop_status:
            self.draw()
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.is_mouse_over(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN:
                        self.action_index = button.value
                        loop_status = False
                if event.type == pygame.QUIT:
                    self.master_window.turn_off_master()
                    self.status = False
                    loop_status = False

        if self.action_index is not None:
            Switchboard(self.root, self.window_name, self.action_index, self.master_window).switch()
