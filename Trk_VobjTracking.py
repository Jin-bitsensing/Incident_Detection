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
    
    # camera parameter
    IMAGE_WIDTH                     = 1920
    IMAGE_HEIGHT					= 1080
    CAMERA_INTRINSIC_FX				= 2119.137451					# Focal length in pixels 
    CAMERA_INTRINSIC_FY				= 2120.412109					# Focal length in pixels 
    CAMERA_INTRINSIC_CX				= 925.452271					# Principal point (Optical center) 
    CAMERA_INTRINSIC_CY				= 564.02832					# Principal point (Optical center) 
    CAMERA_INTRINSIC_SKEW			= -11.126279
    CAMERA_INTRINSIC_K1				= -0.560545					# Radial distortion 
    CAMERA_INTRINSIC_K2				= 0.515465					# Radial distortion 
    CAMERA_INTRINSIC_K3				= -0.070978					# Radial distortion 
    CAMERA_INTRINSIC_P1				= -0.001732					# Tangential distortion
    CAMERA_INTRINSIC_P2				= -1.6e-05					# Tangential distortion

    CAMERA_EXTRINSIC_POS_X			= -3.0
    CAMERA_EXTRINSIC_POS_Y			= 0.5
    CAMERA_EXTRINSIC_POS_Z			= 8.0
    CAMERA_EXTRINSIC_ANGLE_YAW		= 3.5
    CAMERA_EXTRINSIC_ANGLE_PITCH	= 21.0
    CAMERA_EXTRINSIC_ANGLE_ROLL		= 1.0

    # Object tracking
    OBJECT_NON_MAX_SUPPRESS_IOU_THRE = 0.8

    # aux
    _SMALL_VALUE                     = 1e-17


    def __init__(self):

        # Vision object initialization
        self.obj = [ VisionObject() for i in range(self.NUM_OBJ_MAX)]
        
        # Define camera parameter
        self.init_camera_parameter()
        

    def init_camera_parameter(self):

        image_size                  = [ self.IMAGE_WIDTH, self.IMAGE_HEIGHT ]
        intrinsic_parameter         = [ self.CAMERA_INTRINSIC_FX, self.CAMERA_INTRINSIC_FY, 
                                        self.CAMERA_INTRINSIC_CX, self.CAMERA_INTRINSIC_CY, 
                                        self.CAMERA_INTRINSIC_SKEW ]	                        # fx, fy, cx, cy, skew
        distortion_coefficient      = [ self.CAMERA_INTRINSIC_K1, self.CAMERA_INTRINSIC_K2, self.CAMERA_INTRINSIC_K3, 
                                        self.CAMERA_INTRINSIC_P1, self.CAMERA_INTRINSIC_P2 ]
        extrinsic_translation       = [ self.CAMERA_EXTRINSIC_POS_X, 
                                        self.CAMERA_EXTRINSIC_POS_Y, 
                                        self.CAMERA_EXTRINSIC_POS_Z ]                           # tx, ty, tz
        installation_angle_offset   = [ self.CAMERA_EXTRINSIC_ANGLE_YAW, 
                                        self.CAMERA_EXTRINSIC_ANGLE_PITCH, 
                                        self.CAMERA_EXTRINSIC_ANGLE_ROLL ]						# rx, ry, rz
        extrinsic_euler_angle       = [ -1 * installation_angle_offset[0], 
                                        -1 * installation_angle_offset[1], 
                                        -1 * installation_angle_offset[2] ]
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

        # frame initializatoin
        self.init_frame()

        # input data passing
        obj_in_nms = self.input_passing(obj_in_dict)

        # object association
        self.object_association(obj_in_nms)



                                
        # Store output
        self.obj_in_nms = obj_in_nms
        print('tracking done')


    def input_passing(self, obj_in):

        x_boundary_margin = self.IMAGE_WIDTH * 0.01
        y_boundary_margin = self.IMAGE_HEIGHT * 0.01

        obj_nms = []
        for i_obj in range(len(obj_in)):

            # Check validity
            if obj_in[i_obj]['confidence'] == 0:
                break
            
            bbox_in = BoundingBox(obj_in[i_obj]['x_location'],
                                  obj_in[i_obj]['y_location'],
                                  obj_in[i_obj]['width'],
                                  obj_in[i_obj]['height'])

            # Clamping bounding box value to fix corrupted value
            bbox_in.x = bound(bbox_in.x, 0, self.IMAGE_WIDTH - 1)
            bbox_in.y = bound(bbox_in.y, 0, self.IMAGE_HEIGHT - 1)
            bbox_in.w = min(bbox_in.x + bbox_in.w - 1, self.IMAGE_WIDTH  - 1) - bbox_in.x + 1
            bbox_in.h = min(bbox_in.y + bbox_in.h - 1, self.IMAGE_HEIGHT - 1) - bbox_in.y + 1

            # Check boundary condition
            if (bbox_in.x < x_boundary_margin                                       # left
            or self.IMAGE_WIDTH  - (bbox_in.x + bbox_in.w) < x_boundary_margin	    # right
			or self.IMAGE_HEIGHT - (bbox_in.y + bbox_in.h) < y_boundary_margin):	# bottom
                continue

            # Non-maximum suppression
            # Find the first overlapped
            idx_overwrite = -1
            flag_weak = 0
            for j_obj in range(len(obj_nms)):

                # Check Intersection of Union
                iou = self._calc_iou(bbox_in, obj_nms[j_obj].bbox)
                if iou > self.OBJECT_NON_MAX_SUPPRESS_IOU_THRE:
                
                    # Check confidence
                    if obj_in[i_obj]['confidence'] > obj_nms[j_obj].confidence:
                        idx_overwrite = j_obj
                    else:
                        flag_weak = 1
                    break
                        
            if flag_weak is 1:
                continue
            if idx_overwrite is -1:
                # Create new object
                obj_nms.append(VisionObject(len(obj_nms), bbox_in, obj_in[i_obj]['class_id'], obj_in[i_obj]['confidence']))
            else:
                # Data overwrite
                obj_nms[idx_max] = VisionObject(idx_max, bbox_in, obj_in[i_obj]['class_id'], obj_in[i_obj]['confidence'])

        return obj_nms


    def object_association(self, obj_in):

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

        # data passing
        for i_obj in range(len(obj_in)):

            j_obj = obj_in[i_obj]._match_idx
            if j_obj is not -1:
                # update object
                self._update(self.obj[j_obj], obj_in[i_obj])

            else:
                # Create new obj
                self._create(obj_in[i_obj])


        # Not matched object deletion 
        for i_obj in range(self.NUM_OBJ_MAX):

            if (self.obj[i_obj].idx is not -1) and (self.obj[i_obj]._match_idx is -1):
                self.obj[i_obj].__init__()


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
        

    def _pose_estimation(self, obj_trk):
        
        # not implemented
        return
