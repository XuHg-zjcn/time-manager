from my_libs.my_process import Base


class Checker(Base):
    def before(self):
        pass

    def once(self, obj):
        return None

    def after(self):
        pass
