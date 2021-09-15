from enum import Enum

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


class VisionObject:
    
    def __init__(self):
        
        # Public
        self.idx                = -1
        self.class_id           = ObjectClass.UNKNOWN
        self.confidence         = 0.0
        self.alive_age          = 0
        self.moving_state       = MovState.UNKNOWN
        self.moving_direction   = MovDir.UNKNOWN
        self.moving_score       = 0

        # Private
        self._match_idx         = -1


class VobjTracking:
    
    # Configuration
    NUM_VOBJ_MAX = 256

    def __init__(self):
        # Vision object initialization
        self.vobj = [ VisionObject() for i in range(self.NUM_VOBJ_MAX)]


    def tracking(self, scan_idx):
        print('# Scan : %d processing' % scan_idx)
        