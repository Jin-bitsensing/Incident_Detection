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
    NUM_VOBJ_MAX = 256
    
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


    def __init__(self):
        # Vision object initialization
        self.obj = [ VisionObject() for i in range(self.NUM_VOBJ_MAX)]
        
        # Define camera parameter
        self.init_camera_parameter()
        

    def init_frame(self):
        # initialize match index
        for i in range(len(self.obj)):
            if self.obj[i].idx is not -1:
                self.obj[i]._match_idx = -1


    def tracking(self, obj_in):
        # input data passing
        self.input_passing(obj_in)
        print('tracking done')


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

        # Store output
        self.obj_nms = obj_nms

        return
        
