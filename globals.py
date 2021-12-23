import sys, os

class Config():
    def __init__(self):
        self.W = 0
        self.H = 0
        self.PATH = os.path.join(sys.path[0], 'dict')  # Путь к каталогу со словарями

    def set_w_h(self, w, h):
        self.W = w
        self.H = h

cn = Config()