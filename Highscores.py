import h5py
import numpy as np


class Highscores:
    def __init__(self, file_name):
        self.file_name = file_name
        self.number_of_levels = 3
        try:
            self.file = h5py.File(file_name, 'r+')
        except:
            self.file = h5py.File(file_name, 'w')
            self.create()
            self.file = h5py.File(file_name, 'r+')

    def create(self):
        self.file.close()
        self.file = h5py.File(self.file_name, 'w')

        self.file.create_dataset('Scores', (5, ), maxshape=(5, ), dtype=self.create_dtype(self.number_of_levels))
        for i in range(self.number_of_levels):
            self.file['Scores']['Level ' + str(i + 1)] = [np.inf] * 5

        self.file.close()

    def get_current_level_scores(self, level):
        return list(self.file['Scores']['Level ' + str(level)])

    def save_scores(self, scores, level):
        if len(scores) < 5:
            for _ in range(5 - len(scores)):
                scores.append(np.inf)

        scores.sort()
        if len(scores) > 5:
            scores = scores[: 5]

        self.file['Scores']['Level ' + str(level)] = sorted([scores])

        self.file.close()
        self.file = h5py.File(self.file_name, 'r+')

    @staticmethod
    def create_dtype(number_of_levels):
        dtype_list = []
        for i in range(number_of_levels):
            dtype_list.append(('Level ' + str(i + 1), 'f'))

        return np.dtype(dtype_list)
