import sqlite3

from my_libs.my_process import ThrRunn
from .record import Record
from commd_line.init_config import conf


class FaceDB(ThrRunn, Record):
    """
    method except __init__ can only call in same thread, else raise Error below:

    sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread.
    The object was created in thread id 140585671317248 and this is thread id 140588434704192.
    """
    def __init__(self,
                 inps,
                 callbacks=None,
                 db_path=conf['init']['db_path'],
                 auto_commit=True):
        ThrRunn.__init__(self, inps, callbacks)
        Record.__init__(self)
        self._db_path = db_path
        self._conn = None
        self.auto_commit = auto_commit

    def before(self):
        self._conn = sqlite3.connect(self._db_path)
        cur = self._conn.cursor()
        sql = ('CREATE TABLE IF NOT exists face_det('
               'id INTEGER PRIMARY KEY AUTOINCREMENT, '
               'cam_id, t_cap, frame_i, x1, y1, w, h, le_x, le_y, re_x, re_y, '
               'n_x, n_y, lm_x, lm_y, rm_x, rm_y, confidence)')
        cur.execute(sql)

    def save_once(self, face):
        cur = self._conn.cursor()
        sql = ('INSERT INTO face_det '
               '(cam_id, t_cap, frame_i, x1, y1, w, h, le_x, le_y, re_x, re_y, '
               'n_x, n_y, lm_x, lm_y, rm_x, rm_y, confidence) '
               'VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)')
        kp = face.res_d['keypoints']
        cur.execute(sql, (face.cam_id, face.t_cap, face.frame_i, *face.res_d['box'],
                          *kp['left_eye'], *kp['right_eye'],
                          *kp['nose'],
                          *kp['mouth_left'], *kp['mouth_right'],
                          face.res_d['confidence']))
        if self.auto_commit:
            self._conn.commit()

    def once(self, obj):
        for face in obj:
            self.save_once(face)

    def after(self):
        self._conn.commit()
