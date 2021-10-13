import pygame
import math
import numpy as np
import ColorTable as color
from GUI_DataParsing import *
from GUI_KeyState import *
from Trk_PerspectiveCamera import PerspectiveCamera


pygame.init()
pygame.font.init()
myFont1 = pygame.font.Font('./font/210 Haesol R.ttf', 24)
myFont2 = pygame.font.Font('./font/210 Haesol R.ttf', 20)
myFont3 = pygame.font.Font('./font/210 Haesol R.ttf', 22)
BGImage = pygame.image.load('./Image/Wise+Gray+Dark+Tone.JPG')
CAR_Image = pygame.image.load('./Image/CAR1.JPG')

ColorTable = [[]] * 6
a = ColorTable[0]
ColorTable[0] = [color.aquamarine, color.yellow, color.gray]
ColorTable[1] = [color.greenyellow, color.mistyrose, color.gray]
ColorTable[2] = [color.orangered, color.mistyrose, color.gray]
ColorTable[3] = [color.blueviolet, color.mistyrose, color.gray]
ColorTable[4] = [color.blueviolet, color.mistyrose, color.rosybrown]
ColorTable[5] = [color.magenta, color.magenta, color.magenta]


def DrawBirdView(screen, TR_View, KeyState, robj, vobj):

    SimDict = dict()

    DrawVisionObject(screen, TR_View, KeyState, vobj)

    if not KeyState.Key_t:
        DrawTrack(screen, TR_View, KeyState, robj)    



def DrawVisionObject(screen, TR_View, KeyState, vobj):

    # Configuration
    line_color = (255, 255, 0)
    line_width = 2

    for idx in range(len(vobj)):

        if vobj[idx].idx is not -1:

            # Data passing
            ID      = vobj[idx].idx
            obj_x   = vobj[idx].pos_x
            obj_y   = vobj[idx].pos_y
            obj_w   = vobj[idx].wid
            obj_l   = vobj[idx].len
            
            # bounding box
            bbox0 = TR_View.getPointP2D((obj_y - obj_w * 0.5, obj_x - obj_l * 0.5))
            bbox1 = TR_View.getPointP2D((obj_y + obj_w * 0.5, obj_x - obj_l * 0.5))
            bbox2 = TR_View.getPointP2D((obj_y + obj_w * 0.5, obj_x + obj_l * 0.5))
            bbox3 = TR_View.getPointP2D((obj_y - obj_w * 0.5, obj_x + obj_l * 0.5))

            pygame.draw.polygon(screen, line_color, [bbox0, bbox1, bbox2, bbox3], line_width)
        
            # ID
            label = myFont1.render('%d' %(ID), True, line_color)
            screen.blit(label, (bbox2[0]+5, bbox2[1]))


def DrawTrack(screen, TR_View, KeyState, TrkInfo):

    # Draw Configuration
    NewTrackEnable = KeyState.Key_n

    for idx in range(len(TrkInfo)):
        TrkDict = TrackDataParsing(TrkInfo[idx])

        TrkIdx          = TrkDict['idx']
        Status          = TrkDict['upd_state']
        AliveAge        = TrkDict['alive_age']
        MovState        = TrkDict['mov_state']
        PosX            = TrkDict['xpos']
        PosY            = TrkDict['ypos']
        VelX            = TrkDict['xvel']
        VelY            = TrkDict['yvel']
        HeadingAng      = TrkDict['heading']
        Pow             = TrkDict['power']
        Length          = TrkDict['length']
        Width           = TrkDict['width']
        RefPosX         = TrkDict['refxpos']
        RefPosY         = TrkDict['refypos']

        if (Status == 1 and NewTrackEnable) or (Status >= 2):

            if (MovState == 1) or (MovState == 2):  # Moving (1 : Moving / 2 : Stopped)
                colorT = color.white
                colorL = color.red
                lwidth = 2
            else:
                colorT = color.white
                colorL = color.gray
                lwidth = 1

            # Draw Track
            rotate_pos_x = PosX * math.cos(HeadingAng * math.pi / 180.) - PosY * math.sin(HeadingAng * math.pi / 180.)
            rotate_pos_y = -PosX * math.sin(HeadingAng * math.pi / 180.) - PosY * math.cos(HeadingAng * math.pi / 180.)

            BBox_X = (rotate_pos_x + (Length / 2)) * math.cos(HeadingAng * math.pi / 180.) - (
                        rotate_pos_y + (Width / 2)) * math.sin(HeadingAng * math.pi / 180.)
            BBox_Y = (rotate_pos_x + (Length / 2)) * math.sin(HeadingAng * math.pi / 180.) + (
                        rotate_pos_y + (Width / 2)) * math.cos(HeadingAng * math.pi / 180.)
            BBox0 = TR_View.getPointP2D((BBox_Y, BBox_X))

            BBox_X = (rotate_pos_x + (Length / 2)) * math.cos(HeadingAng * math.pi / 180.) - (
                        rotate_pos_y - (Width / 2)) * math.sin(HeadingAng * math.pi / 180.)
            BBox_Y = (rotate_pos_x + (Length / 2)) * math.sin(HeadingAng * math.pi / 180.) + (
                        rotate_pos_y - (Width / 2)) * math.cos(HeadingAng * math.pi / 180.)
            BBox1 = TR_View.getPointP2D((BBox_Y, BBox_X))

            BBox_X = (rotate_pos_x - (Length / 2)) * math.cos(HeadingAng * math.pi / 180.) - (
                        rotate_pos_y - (Width / 2)) * math.sin(HeadingAng * math.pi / 180.)
            BBox_Y = (rotate_pos_x - (Length / 2)) * math.sin(HeadingAng * math.pi / 180.) + (
                        rotate_pos_y - (Width / 2)) * math.cos(HeadingAng * math.pi / 180.)
            BBox2 = TR_View.getPointP2D((BBox_Y, BBox_X))

            BBox_X = (rotate_pos_x - (Length / 2)) * math.cos(HeadingAng * math.pi / 180.) - (
                        rotate_pos_y + (Width / 2)) * math.sin(HeadingAng * math.pi / 180.)
            BBox_Y = (rotate_pos_x - (Length / 2)) * math.sin(HeadingAng * math.pi / 180.) + (
                        rotate_pos_y + (Width / 2)) * math.cos(HeadingAng * math.pi / 180.)
            BBox3 = TR_View.getPointP2D((BBox_Y, BBox_X))

            if (MovState == 1) or (MovState == 2):  # Moving
                ref_radius = 4
            else:
                ref_radius = 1

            phys_pos = -PosY, PosX
            disp_pos = TR_View.getPointP2D(phys_pos)
            disp_off = TR_View.getSizeP2D((Width, -Length))
            disp_pos = disp_pos[0] - disp_off[0] / 2, disp_pos[1] - disp_off[1] / 2
            #pygame.draw.polygon(screen, colorL, [BBox0, BBox1, BBox2, BBox3], lwidth)

            RefPos = TR_View.getPointP2D((RefPosY, RefPosX))
            pygame.draw.circle(screen, colorL, RefPos, ref_radius)

            if (MovState == 1) or (MovState == 2):
                # Display Info
                label = myFont1.render('%d' % (TrkIdx), True, colorL)
                screen.blit(label, (RefPos[0]+5, RefPos[1]))



def DrawGrid(screen, TR_View, BG_Image=False):

    temp_WinSize = TR_View.DispRect[2], TR_View.DispRect[3]
    LeftTop_Pos = TR_View.PhysRect[0], TR_View.PhysRect[1]
    RightBottom_Pos = TR_View.PhysRect[0] + TR_View.PhysRect[2], TR_View.PhysRect[1] + TR_View.PhysRect[3]

    # for adaptive scaling for longitudinal lines
    dw = TR_View.getSizeD2P((40, -40))
    dx = max(1, int(dw[0]))      # minimum resolution : 1
    dy = max(1, int(dw[1]))
    if (dy % 2 == 1) and(dy > 1) and(dy != 5):
        dy -= 1
    if dy > 5:
        dy = 10

    # Image
    if BG_Image:
        screen.blit(pygame.transform.scale(BGImage, temp_WinSize), (0, 0))

    # Color
    colorL = color.darkgray
    colorT = color.lightslategray

    # Lateral Lines
    for i in range(RightBottom_Pos[1], LeftTop_Pos[1], dy):
        p1 = TR_View.getPointP2D((LeftTop_Pos[0], i))
        p2 = TR_View.getPointP2D((RightBottom_Pos[0], i))
        pt = TR_View.getPointP2D((-4, i))

        pygame.draw.line(screen, colorL, p1, p2, 1)
        label = myFont1.render(str(i), 1, colorT)
        screen.blit(label, (5, pt[1]))

    # Longitudinal Lines
    for i in range(0, RightBottom_Pos[0], dx):
        p1 = TR_View.getPointP2D((i, RightBottom_Pos[1]))
        p2 = TR_View.getPointP2D((i, LeftTop_Pos[1]))
        pt = TR_View.getPointP2D((i, 10))
        pygame.draw.line(screen, colorL, p1, p2, 1)
        label = myFont1.render(str(i * 1), 1, colorT)
        screen.blit(label, (pt[0], temp_WinSize[1] - 20))

    for i in range(0, LeftTop_Pos[0], -dx):
        p1 = TR_View.getPointP2D((i, RightBottom_Pos[1]))
        p2 = TR_View.getPointP2D((i, LeftTop_Pos[1]))
        pt = TR_View.getPointP2D((i, 10))
        pygame.draw.line(screen, colorL, p1, p2, 1)
        label = myFont1.render(str(i * 1), 1, colorT)
        screen.blit(label, (pt[0], temp_WinSize[1] - 20))

    # Center Line
    p1 = TR_View.getPointP2D((LeftTop_Pos[0], 0))
    p2 = TR_View.getPointP2D((RightBottom_Pos[0], 0))
    pygame.draw.line(screen, color.darkgray, p1, p2, 2)

    p1 = TR_View.getPointP2D((0, LeftTop_Pos[1]))
    p2 = TR_View.getPointP2D((0, RightBottom_Pos[1]))
    pygame.draw.line(screen, color.darkgray, p1, p2, 2)

    # Car Image
    p1 = TR_View.getPointP2D((-1, 0))
    s1 = TR_View.getSizeP2D((2, -5))
    screen.blit(pygame.transform.scale(CAR_Image, s1), p1)


def DrawTrafficLane(screen, TR_View, TrafficInfo):

    lane_color = color.aliceblue

    for lane in range(TrafficInfo['NumLane'][0]):
        linesL = []
        linesR = []

        step_len = TrafficInfo['NumLaneStep'][lane]
        drawL_Y = TrafficInfo['LeftLane_X'][lane][:step_len[0]]
        drawL_X = TrafficInfo['LeftLane_Y'][lane][:step_len[0]]
        drawR_Y = TrafficInfo['RightLane_X'][lane][:step_len[0]]
        drawR_X = TrafficInfo['RightLane_Y'][lane][:step_len[0]]

        for idx in range(len(drawL_Y)):
            pL = TR_View.getPointP2D((drawL_X[idx], drawL_Y[idx]))
            pR = TR_View.getPointP2D((drawR_X[idx], drawR_Y[idx]))

            linesL.append(pL)
            linesR.append(pR)

        pygame.draw.lines(screen, lane_color, False, linesL, 3)
        pygame.draw.lines(screen, lane_color, False, linesR, 3)

    return


def DrawFoVAng(screen, TR_View, RangeFoV, AngFoV, Color=False):
    if not Color:
        colorL = (0xd4, 0xaa, 0x00)
    else:
        colorL = Color

    temp_Pos = RangeFoV[0], RangeFoV[1]
    temp_R = RangeFoV[2]
    temp_BeamAng = AngFoV[0]
    temp_Ang1 = AngFoV[1] + temp_BeamAng
    temp_Ang2 = -AngFoV[1] + temp_BeamAng

    p1 = TR_View.getPointP2D((temp_Pos[0], temp_Pos[1]))
    p2 = TR_View.getPointP2D((temp_R * math.sin(temp_Ang1 * math.pi / 180.) + temp_Pos[0],
                              temp_R * math.cos(temp_Ang1 * math.pi / 180.) + temp_Pos[1]))
    pygame.draw.line(screen, colorL, p1, p2, 1)

    p1 = TR_View.getPointP2D((temp_Pos[0], temp_Pos[1]))
    p2 = TR_View.getPointP2D((temp_R * math.sin(temp_Ang2 * math.pi / 180.) + temp_Pos[0],
                              temp_R * math.cos(temp_Ang2 * math.pi / 180.) + temp_Pos[1]))
    pygame.draw.line(screen, colorL, p1, p2, 1)

    p1 = TR_View.getPointP2D((-temp_R + temp_Pos[0], temp_R + temp_Pos[1]))
    p2 = TR_View.getSizeP2D((temp_R * 2, -temp_R * 2))
    pygame.draw.arc(screen, colorL, p1 + p2, (90. - temp_Ang1) * math.pi / 180.,
                    ((90. - temp_Ang2 + 1.) * math.pi) / 180., 1)
