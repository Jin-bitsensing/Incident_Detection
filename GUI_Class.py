# Coordinate Transformation
from TransRect import TransRect
from GUI_SubFunc import *
from GUI_KeyState import *
from GUI_BirdView import *
from GUI_DrawInfo import *
from GUI_DataParsing import *
from Trk_PerspectiveCamera import PerspectiveCamera
import ColorTable as Color
import io
import h5py
import numpy as np
import cv2

pygame.font.init()
pygame.mixer.quit()
back_image = pygame.image.load('./Image/cam_BG.JPG')
TitleFont1 = pygame.font.Font('./font/Typo_SsangmunDongStencil.ttf', 20)
SubTitleFont1 = pygame.font.Font('./font/Typo_SsangmunDongStencil.ttf', 16)


class GUI:
    
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

    CAMERA_EXTRINSIC_POS_X_2		= 0.0
    CAMERA_EXTRINSIC_POS_Y_2		= 1.0
    CAMERA_EXTRINSIC_POS_Z_2		= 8.4
    CAMERA_EXTRINSIC_ANGLE_YAW_2	= 3.5
    CAMERA_EXTRINSIC_ANGLE_PITCH_2	= 21.2
    CAMERA_EXTRINSIC_ANGLE_ROLL_2	= -3.5


    def __init__(self, Win_View_Size, Win_CAM_size, Screen_Size):

        # initialization
        self.WinViewSize = Win_View_Size
        self.WinCAMSize = Win_CAM_size
        self.WinMainSize = Win_View_Size[0]+Win_CAM_size[0], Win_View_Size[1]
        self.ScreenSize = Screen_Size
        self.WinTitle = []

        self.DisplaySurf = pygame.display.set_mode(self.WinMainSize, pygame.RESIZABLE)
        
        self.KeyState = DisplayToolKeyState()
        self.FullScreen = False

        self.ViewPos = []
        self.ViewSize = []
        self.View_Surf = []
        self.TR_View = []

        self.CAM_Pos = []
        self.CAM_Surf = []

        self.Info_Pos = []
        self.Info_Surf = []
        
        self.WinTitle = 'Vision object tracking'


        # configuration
        self.long_range = [0, 150]
        self.lat_range  = [-30, 30]


        # Define camera parameter
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
        scaling_factor              = [self.IMAGE_WIDTH / Win_CAM_size[0], self.IMAGE_HEIGHT / Win_CAM_size[1]]

        self.cmr_model = PerspectiveCamera(image_size, intrinsic_parameter, distortion_coefficient, extrinsic_euler_angle, extrinsic_translation, scaling_factor)

        
        # display
        self.DisplayChange(self.DisplaySurf)

        
    def VideoResizeEvent(self, event, frame_data, frame_idx):
        if not self.FullScreen:
            self.DisplaySurf = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        self.DisplayChange(self.DisplaySurf)
        self.display(self.DisplaySurf, frame_data, frame_idx)



    def DisplayChange(self, screen):

        temp_WinSize = screen.get_size()
        temp_ViewSize = int(temp_WinSize[0]-self.WinCAMSize[0]), temp_WinSize[1]
        R = (1, 0, 0, -1)

        self.ViewPos = []
        self.ViewSize = []
        self.View_Surf = []
        self.TR_View = []
        self.CAM_Pos = []
        self.CAM_Surf = []
        self.Info_Pos = []
        self.Info_Surf = []
        temp_InfoSize = []

        PhysRect = GetTRInput((self.lat_range[0], self.long_range[1]), (self.lat_range[1], self.long_range[0]))
        self.ViewSize.append((temp_ViewSize[0], temp_ViewSize[1]))
        self.ViewPos.append((0, 0))
        self.View_Surf.append(pygame.Surface(self.ViewSize[0]))
        self.TR_View.append(TransRect(PhysRect, (0, 0, self.ViewSize[0][0], self.ViewSize[0][1]), R))

        self.CAM_Pos.append((temp_ViewSize[0], 0))
        self.CAM_Surf.append(pygame.Surface(self.WinCAMSize))

        temp_InfoSize.append((self.WinCAMSize[0], int(temp_WinSize[1] - self.WinCAMSize[1])))
        self.Info_Pos.append((temp_ViewSize[0], self.WinCAMSize[1]))
        self.Info_Surf.append(pygame.Surface(temp_InfoSize[0]))


    def Draw_VisionObject_Image(self, screen, frame_data, img):
        if frame_data is not None:
            VobjInfo = frame_data['AI'].value
        
            for idx in range(len(VobjInfo)):
                VobjDict        = VisionObjectDataParsing(VobjInfo[idx])
                class_id        = VobjDict['class_id']
                confidence      = VobjDict['confidence']
                bbox_x          = VobjDict['x_location']
                bbox_y          = VobjDict['y_location']
                bbox_w          = VobjDict['width']
                bbox_h          = VobjDict['height']
        
                BLACK  = (0,   0,    0)
                RED    = (255, 0,    0)
                YELLOW = (255, 255,  0)
                GREEN  = (0,   255,  0)
                BLUE   = (0,   0,    255)
                WHITE  = (255, 255,  255)
        
                bbox_color = YELLOW
                bbox_thickness = 3
        
                bbox = pygame.Rect(bbox_x, bbox_y, bbox_w, bbox_h)
                pygame.draw.rect(img, bbox_color, bbox, bbox_thickness)

            pygame.draw.rect(self.CAM_Surf[0], Color.white, self.CAM_Surf[0].get_rect(), 2)
            self.CAM_Surf[0].blit(pygame.transform.scale(img, self.WinCAMSize), (0, 0))
            screen.blit(self.CAM_Surf[0], self.CAM_Pos[0])


    def display(self, screen, frame_data, frame_idx):
        pygame.display.set_caption(self.WinTitle)
        # screen.fill(Color.white)


        View_Surf = self.View_Surf
        TR_View = self.TR_View


        View_Surf[0].fill(Color.black)

        # Mouse Action
        if self.KeyState.MouseDrag_on or self.KeyState.MouseLeftUp_on:
            TR_View = self.MouseDragEvent(View_Surf, TR_View)
            self.KeyState.MouseLeftUp_on = False

        # Draw Plane
        pygame.draw.rect(View_Surf[0], Color.white, View_Surf[0].get_rect(), 2)
        DrawGrid(View_Surf[0], TR_View[0], self.KeyState.Key_g)

        # Text
        label = TitleFont1.render(self.WinTitle, 1, Color.white)
        View_Surf[0].blit(label, (40, 20))
        label = TitleFont1.render(('frame: % d' % frame_idx), 1, Color.aqua)
        View_Surf[0].blit(label, (40, 50))


        if not self.KeyState.Key_t:
            label_obj = SubTitleFont1.render('/Trk On', 1, Color.tan)
        else:
            label_obj = SubTitleFont1.render('/Trk Off', 1, Color.tan)
        View_Surf[0].blit(label_obj, (40, 80))

        
        # BirdEye Blit
        if 'Image' in frame_data:
            imagebuffer = frame_data['Image'].value
            fsub = io.BytesIO(imagebuffer)
            img = pygame.image.load(fsub, 'jpg')

        else:
            img = back_image

        self.Draw_VisionObject_Image(screen, frame_data, img)


        # Draw Simulation Data
        if frame_data is not None:
            DrawBirdView(View_Surf[0], TR_View[0], self.KeyState, frame_data, self.cmr_model)

        # BirdEye View Blit
        screen.blit(View_Surf[0], self.ViewPos[0])
        
        # Information Window
        pygame.draw.rect(self.Info_Surf[0], Color.white, self.Info_Surf[0].get_rect(), 2)
        self.Info_Surf[0].blit(pygame.transform.scale(BGImage, self.Info_Surf[0].get_size()), (0, 0))
        if frame_data is not None:
            DrawInfo(self.Info_Surf[0], frame_data)
        screen.blit(self.Info_Surf[0], self.Info_Pos[0])



    def MouseDragEvent(self, View_Surf, TR_View):

        if (abs(self.KeyState.MouseDrag_size[0]) > 20) and (abs(self.KeyState.MouseDrag_size[1]) > 20):
            MouseDrag_rect = self.KeyState.MouseLeftDown_pos[0], self.KeyState.MouseLeftDown_pos[1],\
                             self.KeyState.MouseDrag_size[0], self.KeyState.MouseDrag_size[1]

            SelView, MouseDrag_rect = GetMouseWinPos(MouseDrag_rect, self.ViewPos, self.ViewSize)

            if self.KeyState.MouseDrag_on:
                colorL = (0xFF, 0xAA, 0xAA)
                # pygame.draw.rect(View_Surf[SelView], colorL, MouseDrag_rect, 1)
                for surf in View_Surf:
                    pygame.draw.rect(surf, colorL, MouseDrag_rect, 1)

            if self.KeyState.MouseLeftUp_on:
                if MouseDrag_rect[2] > 0 and MouseDrag_rect[3] > 0:  # (left upper) to (right lower)
                    p1 = TR_View[SelView].getPointD2P((MouseDrag_rect[0], MouseDrag_rect[1]))
                    p2 = TR_View[SelView].getSizeD2P((MouseDrag_rect[2], MouseDrag_rect[3]))
                    # print p1, p2
                    if (abs(p2[0]) > 0.3) and (abs(p2[1]) > 0.3):
                        #TR_View[SelView].UpdateScaleOffset(p1 + p2)
                        for tr_rect in TR_View:
                            tr_rect.UpdateScaleOffset(p1 + p2)
                else:
                    #TR_View[SelView].UpdateScaleOffsetOriginal()
                    for tr_rect in TR_View:
                        tr_rect.UpdateScaleOffsetOriginal()

        return TR_View


    def TargetSelectEvent(self, TR, rect, DataSet, DebugInfo_On = True):

        if DataSet is not None:
            ObjInfo = DataSet['Sim_ObjInfo'].value
            TrkInfo = DataSet['Sim_TrkInfo'].value
            #if DataSet['Sim_TrkletInfo'].value is not None:
            #    TrkletInfo = DataSet['Sim_TrkletInfo'].value
            #else:
            #    TrkletInfo = None
        else:
            ObjInfo = None
            TrkInfo = None
            TrkletInfo = None

        SelectedObj = []
        SelectedTrklet = []
        SelectedTrk = []
        NewTrackEnable = self.KeyState.Key_n
        p1 = TR.getPointD2P((rect[0], rect[1]))     # mouse position
        g1 = TR.getSizeD2P((40, 40))
        g2 = TR.getSizeD2P((60, 60))
        g3 = TR.getSizeD2P((30, 30))

        Temp_ObjMin = math.sqrt((g3[0] ** 2) + (g3[1] ** 2))
        Temp_TrkletMin = math.sqrt((g3[0] ** 2) + (g3[1] ** 2))
        Temp_TrkMin = math.sqrt((g3[0] ** 2) + (g3[1] ** 2))
        NearestObj = None
        NearestTrklet = None
        NearestTrk = None

        if ObjInfo is not None:
            for idx in range(len(ObjInfo)):
                if ObjInfo[idx][0] != 0:
                    if (self.Mode == 3) :
                        ObjDict = ObjectDataParsing_Log(ObjInfo[idx])
                    else:
                        ObjDict = ObjectDataParsing(ObjInfo[idx])

                    R = ObjDict['R']
                    AziAng = ObjDict['AziAng']
                    PosX = R * math.cos(AziAng / 180 * math.pi)
                    PosY = R * math.sin(AziAng / 180 * math.pi)
                    phys_pos = -PosY, PosX

                    if (abs(phys_pos[0] - p1[0]) < abs(g1[0])) and (abs(phys_pos[1] - p1[1]) < abs(g1[1])):
                        SelectedObj.append(idx)
                        temp_Dist = math.sqrt((phys_pos[0] - p1[0])**2 + (phys_pos[1] - p1[1])**2)
                        if temp_Dist < Temp_ObjMin:
                            Temp_ObjMin = temp_Dist
                            NearestObj = idx

        if TrkInfo is not None:
            for idx in range(len(TrkInfo)):
                if (self.Mode == 3):
                    TrkDict = TrackDataParsing(TrkInfo[idx])
                else:
                    TrkDict = TrackDataParsing(TrkInfo[idx])

                Status = TrkDict['Status']
                PosX = TrkDict['PosX']
                PosY = TrkDict['PosY']
                phys_pos = PosY, PosX

                if (Status == 1 and NewTrackEnable) or (Status == 2):
                    if (abs(phys_pos[0] - p1[0]) < abs(g2[0])) and (abs(phys_pos[1] - p1[1]) < abs(g2[1])):
                        SelectedTrk.append(idx)
                        temp_Dist = math.sqrt((phys_pos[0] - p1[0])**2 + (phys_pos[1] - p1[1])**2)
                        if temp_Dist < Temp_TrkMin:
                            Temp_TrkMin = temp_Dist
                            NearestTrk = idx


        if DebugInfo_On is True:
            if NearestObj is not None:
                ObjInfo_GUI.SetObjInfo(ObjInfo[NearestObj], DataSet)

            # if NearestTrk is not None:
                # QtTrk.SetTrkInfo(TrkInfo[NearestTrk], DataSet)

        # h5 저장
        if NearestObj is not None:
            h5file = h5py.File('Cur_objinfo' + '.h5', "w")
            Peak_num = ObjInfo[NearestObj][10]
            frame_idx = DataSet.name
            R_idx = ObjInfo[NearestObj][8]
            D_idx = ObjInfo[NearestObj][9]

            group_name = 'data'
            h5grp = h5file.create_group(group_name)
            h5grp.create_dataset("Peak", data=Peak_num, dtype='int16')
            h5grp.create_dataset("frame_idx", data=frame_idx)
            h5grp.create_dataset("R_idx", data=R_idx)
            h5grp.create_dataset("D_idx", data=D_idx)

            print('ObjInfo[NearestObj]', ObjInfo[NearestObj][10])
            print('frame_idx', DataSet.name)


        return SelectedObj, SelectedTrklet, SelectedTrk
