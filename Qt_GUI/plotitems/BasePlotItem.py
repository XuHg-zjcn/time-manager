import pyqtgraph as pg

class BasePlotItem(pg.GraphicsObject):
    def set_swap(self):
            self.rotate(90)
            self.scale(1, -1)

    def update_xy(self):
        raise NotImplementedError()
