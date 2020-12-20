import os
import glob


class collect:
    @classmethod
    def add_to_db(cls, colls, source_path):
        print(cls.__name__)
        colls.add_item(cls.__name__,
                       input('enable:').upper() in {'T', 'TRUE', 'Y', 'YES'},
                       cls.table_name,
                       cls.dbtype,
                       source_path,
                       cls.srcipt)


class firefox(collect):
    table_name = 'browser'
    dbtype = 1001
    srcipt = '../data_collector/browser/firefox_history.py'
    @classmethod
    def add_to_db(cls, colls):
        paths = glob.glob(os.path.join(os.environ['HOME'], '.mozilla/firefox/*.default-release/places.sqlite'))
        if len(paths) == 0:
            print('no found')
        elif len(paths) == 1:
            source_path = paths[0]
        else:
            inp = input('请选择:' + '\n'.join(paths) + '\n')
            source_path = paths[int(inp)]
        super().add_to_db(colls, source_path)


lst = [firefox]

def input_chooise():
    inp = input('请输入预设编号，可以同时输入多个，用逗号隔开\n'
                '0: firefox(linux)\n'
                '1: chrome(linux)\n')  # TODO: gen print form lst
    return int(inp)


def add_default(i, colls):
    lst[i].add_to_db(colls)
