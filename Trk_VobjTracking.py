import numpy as np
from enum import Enum
from Trk_PerspectiveCamera import PerspectiveCamera


####################################
######### Sub Functions ############
####################################

def bound(value, low, high):
    return max(low, min(high, value))


####################################
######### Class Definition #########
####################################

class ObjectClass(Enum):
    BUS         = 0
    TRUCK       = 1
    LONG_TRUCK  = 2
    CAR         = 3
    MOTORCYCLE  = 4
    PEDESTRIAN  = 5
    OTHERS      = 6
    UNKNOWN     = 7


class MovState(Enum):
    STOP    = 0
    MOVING  = 1
    UNKNOWN = 2


class MovDir(Enum):
    ONCOMING    = 0
    PRECEDING   = 1
    UNKNOWN     = 2


class BoundingBox:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
    

class VisionObject:
    
    def __init__(self, idx = -1, bbox = [], class_id = ObjectClass.UNKNOWN, confidence = 0.0, 
                 alive_age = 0, mov_state = MovState.UNKNOWN, mov_dir = MovDir.UNKNOWN, mov_score = 0, match_idx = -1):
        
        # Public
        self.idx        = idx
        self.bbox       = bbox
        self.class_id   = class_id
        self.confidence = confidence
        
        self.alive_age  = alive_age
        self.mov_state  = mov_state
        self.mov_dir    = mov_dir
        self.mov_score  = mov_score

        # Private
        self._match_idx = match_idx
        

class VobjTracking:
    
    ## Configuration

    # vision object
    NUM_OBJ_MAX = 256
    

    # Object tracking
    OBJECT_NON_MAX_SUPPRESS_IOU_THRE = 0.8

    # Moving state estimation
    MOVING_STATE_EST_MIN_AGE         = 1
    MOVING_STATE_EST_IMGYDIF_MARGIN  = 0
    MOVING_STATE_EST_SCORE_MOVING    = 2
    MOVING_STATE_EST_SCORE_THRESHOLD = 2
    MOVING_STATE_EST_PANALTY_STOP    = 1

    # Object size approximation
    OBJ_LEN_INIT_BUS                 = 10.0
    OBJ_WID_INIT_BUS                 = 2.5
    OBJ_LEN_INIT_TRUCK               = 5.5
    OBJ_WID_INIT_TRUCK               = 1.6
    OBJ_LEN_INIT_LONG_TRUCK          = 10.0
    OBJ_WID_INIT_LONG_TRUCK          = 2.3
    OBJ_LEN_INIT_CAR                 = 3.5
    OBJ_WID_INIT_CAR                 = 1.6
    OBJ_LEN_INIT_MOTORCYCLE          = 1.5
    OBJ_WID_INIT_MOTORCYCLE          = 1.0
    OBJ_LEN_INIT_PEDESTRIAN          = 0.5
    OBJ_WID_INIT_PEDESTRIAN          = 0.5


    # aux
    _SMALL_VALUE                     = 1e-17


    def __init__(self, image_size, 
                       intrinsic_parameter, 
                       distortion_coefficient, 
                       extrinsic_euler_angle, 
                       extrinsic_translation):

        # Vision object initialization
        self.obj = [ VisionObject() for i in range(self.NUM_OBJ_MAX)]
        
        # Define camera parameter
        self.init_camera_parameter(image_size, 
                                   intrinsic_parameter, 
                                   distortion_coefficient, 
                                   extrinsic_euler_angle, 
                                   extrinsic_translation)
        

    def init_camera_parameter(self, image_size, 
                                    intrinsic_parameter, 
                                    distortion_coefficient, 
                                    extrinsic_euler_angle, 
                                    extrinsic_translation):

        self.cmr_model = PerspectiveCamera(image_size, 
                                           intrinsic_parameter, 
                                           distortion_coefficient, 
                                           extrinsic_euler_angle, 
                                           extrinsic_translation)


    def init_frame(self):

        # initialize match index
        for i in range(len(self.obj)):
            if self.obj[i].idx is not -1:
                self.obj[i]._match_idx = -1


    def tracking(self, obj_in_dict):

        # Frame initializatoin
        self.init_frame()

        # Input data passing
        obj_in = self._input_passing(obj_in_dict)

        # Object association
        self._association(obj_in)

        # Data passing
        for i_obj in range(len(obj_in)):

            j_obj = obj_in[i_obj]._match_idx
            if j_obj is not -1:
                # update object
                self._update(self.obj[j_obj], obj_in[i_obj])

            else:
                # Create new obj
                self._create(obj_in[i_obj])

        # Object merge
        self._merge()

        # Not matched object deletion 
        for i_obj in range(self.NUM_OBJ_MAX):

            if (self.obj[i_obj].idx is not -1) and (self.obj[i_obj]._match_idx is -1):
                self.obj[i_obj].__init__()


        print('tracking done')


    def _input_passing(self, obj_in):

        x_boundary_margin = self.cmr_model.image_size[0] * 0.01
        y_boundary_margin = self.cmr_model.image_size[1] * 0.01

        obj_out = []
        for i_obj in range(len(obj_in)):

            # Check validity
            if obj_in[i_obj]['confidence'] == 0:
                break
            
            bbox_in = BoundingBox(obj_in[i_obj]['x_location'],
                                  obj_in[i_obj]['y_location'],
                                  obj_in[i_obj]['width'],
                                  obj_in[i_obj]['height'])

            # Clamping bounding box value to fix corrupted value
            bbox_in.x = bound(bbox_in.x, 0, self.cmr_model.image_size[0] - 1)
            bbox_in.y = bound(bbox_in.y, 0, self.cmr_model.image_size[1] - 1)
            bbox_in.w = min(bbox_in.x + bbox_in.w - 1, self.cmr_model.image_size[0] - 1) - bbox_in.x + 1
            bbox_in.h = min(bbox_in.y + bbox_in.h - 1, self.cmr_model.image_size[1] - 1) - bbox_in.y + 1

            # Check boundary condition
            if (bbox_in.x < x_boundary_margin                                       # left
            or self.cmr_model.image_size[0] - (bbox_in.x + bbox_in.w) < x_boundary_margin	    # right
			or self.cmr_model.image_size[1] - (bbox_in.y + bbox_in.h) < y_boundary_margin):	# bottom
                continue

            # Create new object
            obj_out.append(VisionObject(len(obj_out), bbox_in, obj_in[i_obj]['class_id'], obj_in[i_obj]['confidence']))

        return obj_out


    def _association(self, obj_in):

        # matching priority : descending order
        for i_obj in range(len(obj_in)):

            max_iou = 0
            max_iou_idx = -1
            for j_obj in range(self.NUM_OBJ_MAX):
                if (self.obj[j_obj].idx is not -1) and (self.obj[j_obj]._match_idx is -1):

                    iou = self._calc_iou(obj_in[i_obj].bbox, self.obj[j_obj].bbox)
                    if iou > max_iou:
                        max_iou     = iou
                        max_iou_idx = j_obj

            if max_iou_idx is not -1:
                obj_in[i_obj]._match_idx    = max_iou_idx
                self.obj[j_obj]._match_idx  = i_obj
            else:
                obj_in[i_obj]._match_idx    = -1


    def _calc_iou(self, bbox1, bbox2):

        x_lef = max(bbox1.x, bbox2.x)
        y_top = max(bbox1.y, bbox2.y)
        x_rig = min(bbox1.x + bbox1.w - 1, bbox2.x + bbox2.w - 1)
        y_bot = min(bbox1.y + bbox1.h - 1, bbox2.y + bbox2.h - 1)

        if (x_rig < x_lef) or (y_bot < y_top):
            return 0.0

        # The intersection of two axis - aligned bounding boxes is always an axis - aligned bounding box
        intersection_area = (x_rig - x_lef) * (y_bot - y_top)

        # Compute the intersection over union by taking the intersection area and dividing it by the sum of prediction + ground-truth areas - the interesection area
        iou = intersection_area / ((bbox1.w * bbox1.h) + (bbox2.w * bbox2.h) - intersection_area + self._SMALL_VALUE)

        return iou


    def _update(self, obj_trk, obj_in):

        # Previous data buffering
        obj_trk.bbox_prev   = obj_trk.bbox

        # Data overwriting
        obj_trk.class_id    = obj_in.class_id
        obj_trk.confidence  = obj_in.confidence
        obj_trk.bbox        = obj_in.bbox

        # Data update
        obj_trk.alive_age   += 1
        obj_trk._match_idx  = obj_in.idx

        # Pose estimation
        self._pose_estimation(obj_trk)


    def _create(self, obj_in):

        for i_obj in range(self.NUM_OBJ_MAX):

            if self.obj[i_obj].idx is -1:

                self.obj[i_obj].idx         = i_obj
                self.obj[i_obj]._match_idx  = obj_in.idx

                self._update(self.obj[i_obj], obj_in)

                break
        

    def _merge(self):
        
        # Object merging
        for i_obj in range(len(self.obj)):

            if self.obj[i_obj].idx is not -1:

                pos_x_i = self.obj[i_obj].pos_x
                pos_y_i = self.obj[i_obj].pos_y
                len_i   = self.obj[i_obj].len
                wid_i   = self.obj[i_obj].wid
                age_i   = self.obj[i_obj].alive_age
                bbox_i  = self.obj[i_obj].bbox

                for j_obj in range(i_obj + 1, len(self.obj)):

                    if self.obj[j_obj].idx is not -1:
                        
                        pos_x_j = self.obj[j_obj].pos_x
                        pos_y_j = self.obj[j_obj].pos_y
                        len_j   = self.obj[j_obj].len
                        wid_j   = self.obj[j_obj].wid
                        age_j   = self.obj[j_obj].alive_age
                        bbox_j  = self.obj[j_obj].bbox

                        if (abs(pos_x_i - pos_x_j) < (len_i + len_j) * 0.5
                        and abs(pos_y_i - pos_y_j) < (wid_i + wid_j) * 0.5):

                            # merge to older object
                            if age_i >= age_j:
                                self.obj[i_obj].pos_x = pos_x_j
                                self.obj[i_obj].pos_y = pos_y_j
                                self.obj[i_obj].bbox  = self._merge_bbox(bbox_i, bbox_j)
                                self.obj[j_obj].__init__()
                            else:
                                self.obj[j_obj].pos_x = pos_x_i
                                self.obj[j_obj].pos_y = pos_y_i
                                self.obj[j_obj].bbox  = self._merge_bbox(bbox_i, bbox_j)
                                self.obj[i_obj].__init__()


    def _merge_bbox(self, bbox1, bbox2):

        x = min(bbox1.x, bbox2.x)
        y = min(bbox1.y, bbox2.y)
        w = max(bbox1.x + bbox1.w, bbox2.x + bbox2.w) - x + 1
        h = max(bbox1.y + bbox1.h, bbox2.y + bbox2.h) - y + 1

        return BoundingBox(x, y, w, h)


    def _pose_estimation(self, obj):
        
	    # Object orientation estimation
        if obj.alive_age > self.MOVING_STATE_EST_MIN_AGE:
            self._moving_state_estimation(obj)
            
        # Object size approximation
        self._set_object_size_from_class(obj)

        # Object position estimation
        self._set_object_position_from_bbox(obj);

          
    def _moving_state_estimation(self, obj):

        ypos_curr = obj.bbox.y - obj.bbox.h * 0.5
        ypos_prev = obj.bbox_prev.y - obj.bbox_prev.h * 0.5

        if ypos_prev - ypos_curr > self.MOVING_STATE_EST_IMGYDIF_MARGIN:
            # preceding
            obj.mov_score = min(obj.mov_score + self.MOVING_STATE_EST_SCORE_MOVING, self.MOVING_STATE_EST_SCORE_THRESHOLD)

        elif ypos_curr - ypos_prev > self.MOVING_STATE_EST_IMGYDIF_MARGIN:
            # oncoming
            obj.mov_score = max(obj.mov_score - self.MOVING_STATE_EST_SCORE_MOVING, self.MOVING_STATE_EST_SCORE_THRESHOLD * (-1))

        else:
            # stop
            if obj.mov_score > 0:
                obj.mov_score -= self.MOVING_STATE_EST_PANALTY_STOP
            elif obj.mov_score < 0:
                obj.mov_score += self.MOVING_STATE_EST_PANALTY_STOP

        if obj.mov_score > 0:
            obj.mov_state        = MovState.MOVING
            obj.mov_dir          = MovDir.PRECEDING
        elif obj.mov_score < 0:
            obj.mov_state        = MovState.MOVING
            obj.mov_dir          = MovDir.ONCOMING
        else:
            obj.mov_state       = MovState.STOP
            
            
    def _set_object_size_from_class(self, obj):

        if obj.class_id == ObjectClass.BUS:
            obj.len = self.OBJ_LEN_INIT_BUS
            obj.wid = self.OBJ_WID_INIT_BUS

        elif obj.class_id == ObjectClass.TRUCK:
            obj.len = self.OBJ_LEN_INIT_TRUCK
            obj.wid = self.OBJ_WID_INIT_TRUCK

        elif obj.class_id == ObjectClass.LONG_TRUCK:
            obj.len = self.OBJ_LEN_INIT_LONG_TRUCK
            obj.wid = self.OBJ_WID_INIT_LONG_TRUCK

        elif obj.class_id == ObjectClass.CAR:
            obj.len = self.OBJ_LEN_INIT_CAR
            obj.wid = self.OBJ_WID_INIT_CAR

        elif obj.class_id == ObjectClass.MOTORCYCLE:
            obj.len = self.OBJ_LEN_INIT_MOTORCYCLE
            obj.wid = self.OBJ_WID_INIT_MOTORCYCLE

        elif obj.class_id == ObjectClass.PEDESTRIAN:
            obj.len = self.OBJ_LEN_INIT_PEDESTRIAN
            obj.wid = self.OBJ_WID_INIT_PEDESTRIAN

        else:
            obj.len = self.OBJ_LEN_INIT_CAR
            obj.wid = self.OBJ_WID_INIT_CAR

              
    def _set_object_position_from_bbox(self, obj):

        # Position calculation
        img_bot_1 = np.array([obj.bbox.x,                   obj.bbox.y + obj.bbox.h - 1])
        img_bot_2 = np.array([obj.bbox.x + obj.bbox.w - 1,  obj.bbox.y + obj.bbox.h - 1])
        
        wld_bot_1 = self.cmr_model.img2wld(img_bot_1)
        wld_bot_2 = self.cmr_model.img2wld(img_bot_2)
        
        img_pos_center_x = self.cmr_model._cx
        if img_bot_2[0] < img_pos_center_x:
            # Ground point: right bottom corner
            obj.pos_x = wld_bot_2[0] + obj.len * 0.5
            obj.pos_y = wld_bot_2[1] + obj.wid * 0.5

        elif img_bot_1[0] > img_pos_center_x:
            # Ground point: left bottom corner
            obj.pos_x = wld_bot_1[0] + obj.len * 0.5
            obj.pos_y = wld_bot_1[1] - obj.wid * 0.5

        else:
            # Ground point: middle of bottom corners
            obj.pos_x = (wld_bot_1[0] + wld_bot_2[0]) * 0.5 + obj.len * 0.5
            obj.pos_y = (wld_bot_1[1] + wld_bot_2[1]) * 0.5
