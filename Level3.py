import random
from Items import *

pygame.init()


class TerroristsAndCivilians:
    def __init__(self, window_width, window_height):
        self.targets = Sprites()
        self.grid = Grid(window_width, window_height, self.targets.sprite_dimension)
        self.terrorist, self.civilian = self.pick_fruit()
        self.current_index = 0
        self.min_number_terrorists = 1
        self.max_number_terrorists = 3
        self.min_number_civilians = 0
        self.max_number_civilians = 3
        self.pre_defined_rounds = []
        self.build_pre_defined_rounds()
        self.min_interval = 500
        self.max_interval = 1500
        self.round_time = 2000
        self.round_intervals = []
        self.build_round_intervals()
        self.rounds = {}
        self.build_rounds()
        self.fruit_determiner = {'apple': 'every', 'bananas': 'all', 'grapes': 'all', 'lemon': 'every', 'orange': 'every', 'peach': 'every', 'pineapple': 'every', 'plum': 'every', 'watermelon': 'every'}

    def pick_fruit(self):
        samples = random.sample(self.targets.available_sprites, k=2)
        return samples[0], samples[1]

    def build_pre_defined_rounds(self):
        for i in range(self.min_number_terrorists, self.max_number_terrorists + 1):
            for j in range(self.min_number_civilians, self.max_number_civilians + 1):
                self.pre_defined_rounds.append((i, j))

        random.shuffle(self.pre_defined_rounds)

    def build_round_intervals(self):
        for _ in range(len(self.pre_defined_rounds)):
            self.round_intervals.append(int(random.random() * (self.max_interval - self.min_interval) + self.min_interval))

    def build_rounds(self):
        def split_list(list_to_split, len_first_part):
            return [list_to_split[:len_first_part], list_to_split[len_first_part:]]

        total_time = 0
        times = []
        grids = []
        for i in range(len(self.round_intervals)):
            total_time += self.round_intervals[i]
            times.append(total_time)
            grids.append([[], []])

            total_time += self.round_time
            times.append(total_time)
            grids.append(split_list(random.sample(self.grid.grid, k=sum(self.pre_defined_rounds[i])), self.pre_defined_rounds[i][0]))

        self.rounds['times'] = times
        self.rounds['grids'] = grids

    def get_current_sprites_placement(self, clock_time):
        index = self.current_index
        while self.rounds['times'][index] < clock_time:
            if index + 1 < len(self.rounds['times']):
                index += 1
            else:
                break

        self.current_index = index
        return self.rounds['grids'][index]


class Fruit:
    def __init__(self, sprite, kind, position, dimension):
        self.sprite = sprite
        self.kind = kind
        self.x, self.y = position
        self.dimension = dimension

    def is_mouse_over(self, mouse_pos):
        if self.x < mouse_pos[0] < self.x + self.dimension:
            if self.y < mouse_pos[1] < self.y + self.dimension:
                return True

        return False


class Level3:
    def __init__(self, root, master_window):
        self.root = root
        self.master_window = master_window
        self.sounds = Sounds()
        self.terrorist_and_civilians = TerroristsAndCivilians(self.root.window_width, self.root.window_height)
        self.description = Description(self.root, ['Click at ' + self.terrorist_and_civilians.fruit_determiner[self.terrorist_and_civilians.terrorist] + ' ' + self.terrorist_and_civilians.terrorist, 'Do not click at any ' + self.terrorist_and_civilians.civilian])
        self.time_measures = TimeMeasures()
        self.results = Results(self.root, 3)
        self.backgrounds = Backgrounds()
        self.current_sprites = []
        self.current_round = -1
        self.status = True

    def prepare_round(self):
        self.current_sprites = []
        grids = self.terrorist_and_civilians.rounds['grids'][self.terrorist_and_civilians.current_index][0]
        for i in range(len(grids)):
            self.current_sprites.append(Fruit(self.terrorist_and_civilians.targets.sprites[self.terrorist_and_civilians.terrorist], 'terrorist', grids[i], self.terrorist_and_civilians.targets.sprite_dimension))

        grids = self.terrorist_and_civilians.rounds['grids'][self.terrorist_and_civilians.current_index][1]
        for i in range(len(grids)):
            self.current_sprites.append(Fruit(self.terrorist_and_civilians.targets.sprites[self.terrorist_and_civilians.civilian], 'civilian', grids[i], self.terrorist_and_civilians.targets.sprite_dimension))

    def draw_round(self):
        self.root.window.blit(self.backgrounds.background_levels, (0, 0))
        for fruit in self.current_sprites:
            self.root.window.blit(fruit.sprite, (fruit.x, fruit.y))

        pygame.display.update()

    def calculate_misses(self):
        misses = 0
        for sprite in self.current_sprites:
            if sprite.kind == 'terrorist':
                self.time_measures.strikes += 1
                misses += 1

        if misses:
            self.sounds.miss_sound.play()
            if misses == len(self.terrorist_and_civilians.rounds['grids'][self.current_round][0]):
                self.time_measures.round_times[self.current_round] = -1

    def main_loop(self):
        loop_status = True
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < self.terrorist_and_civilians.rounds['times'][-1] and loop_status:
            self.terrorist_and_civilians.get_current_sprites_placement(pygame.time.get_ticks() - start)
            if self.current_round != self.terrorist_and_civilians.current_index:
                self.calculate_misses()
                self.current_round = self.terrorist_and_civilians.current_index
                self.prepare_round()
            self.draw_round()
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                for current_sprite in self.current_sprites:
                    if current_sprite.is_mouse_over(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN:
                        self.current_sprites.remove(current_sprite)
                        if current_sprite.kind == 'terrorist':
                            stop = pygame.time.get_ticks()
                            self.sounds.correct_sound.play()
                            self.time_measures.round_times[self.current_round] = stop - start - self.terrorist_and_civilians.rounds['times'][self.current_round - 1]
                        else:
                            self.sounds.wrong_sound.play()
                            self.time_measures.strikes += 1
                if event.type == pygame.QUIT:
                    self.status = False
                    loop_status = False

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
