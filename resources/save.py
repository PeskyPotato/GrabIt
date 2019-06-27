import os

class Save:
    def __init__(self, base_dir, by_sub):
        self.base_dir = base_dir
        self.by_sub = by_sub
    
    def get_dir(self, author, sub):
        if self.by_sub:
            folder = os.path.join(self.base_dir, author, sub)
        else:
            folder = os.path.join(self.base_dir, sub, author)
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder