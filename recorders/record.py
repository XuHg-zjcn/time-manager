from my_libs.my_process import Base


class Record(Base):
    def before(self):
        pass

    def once(self, obj):
        # write obj, please add your code.
        pass

    def after(self):
        pass
