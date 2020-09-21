from Menu import *
from Settings import Settings


class MasterWindow:
    def __init__(self):
        self.status = True
        self.settings = Settings('settings.hdf5')
        self.sounds = Sounds()

    def turn_off_master(self):
        self.status = False

    def run(self):
        loop_status = True
        while loop_status:
            resolution = self.settings.get_resolution()
            self.sounds.play_background_music('main')
            Menu(Window(resolution[0], resolution[1], 'Reflex'), MenuItemManager().menus['Main'], self).run_level()
            if not self.status:
                loop_status = False


if __name__ == '__main__':
    MasterWindow().run()
