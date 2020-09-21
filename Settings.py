import h5py
import numpy as np


class Settings:
    def __init__(self, file_name):
        self.file_name = file_name
        try:
            self.file = h5py.File(file_name, 'r+')
        except:
            self.file = h5py.File(file_name, 'w')
            self.create()
            self.file = h5py.File(file_name, 'r+')

    def create(self):
        self.file.close()
        self.file = h5py.File(self.file_name, 'w')

        self.file.create_dataset('Resolution', (1, 1), maxshape=(1, 1), dtype=np.dtype([('Window width', 'i'), ('Window height', 'i')]))
        self.file['Resolution']['Window width'] = 640
        self.file['Resolution']['Window height'] = 480

        self.file.close()

    def change_resolution(self, new_resolution):
        self.file['Resolution']['Window width'] = new_resolution[0]
        self.file['Resolution']['Window height'] = new_resolution[1]

    def get_resolution(self):
        return self.file['Resolution']['Window width'][0, 0], self.file['Resolution']['Window height'][0, 0]
