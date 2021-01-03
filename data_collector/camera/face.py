import cv2


def points_x(src, div):
    ret = {}
    for k, i in src.items():
        ret[k] = tuple(map(lambda x: div*x, i))
    return ret

def point_x(src, div):
    return tuple(map(lambda x: div*x, src))


class Face:
    def __init__(self, cam_id, t_cap, frame_i, res_d, div):
        self.cam_id = cam_id
        self.t_cap = t_cap
        self.frame_i = frame_i
        self.res_d = res_d
        self.div = div

    def draw_cv(self, frame):
        bounding_box = point_x(self.res_d['box'], self.div)
        keypoints = points_x(self.res_d['keypoints'], self.div)
        cv2.rectangle(frame,
                      (bounding_box[0], bounding_box[1]),
                      (bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]),
                      (0, 155, 255), 2)

        cv2.circle(frame, (keypoints['left_eye']), 2, (0, 155, 255), 2)
        cv2.circle(frame, (keypoints['right_eye']), 2, (0, 155, 255), 2)
        cv2.circle(frame, (keypoints['nose']), 2, (0, 155, 255), 2)
        cv2.circle(frame, (keypoints['mouth_left']), 2, (0, 155, 255), 2)
        cv2.circle(frame, (keypoints['mouth_right']), 2, (0, 155, 255), 2)
