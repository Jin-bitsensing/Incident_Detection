import pygame
import ColorTable as Color
from GUI_DataParsing import *


pygame.init()
pygame.font.init()
InfoFont1 = pygame.font.Font('./font/210 Haesol R.ttf', 20)
InfoFont2 = pygame.font.Font('./font/210 Haesol R.ttf', 16)
InfoFont3 = pygame.font.Font('./font/210 Haesol R.ttf', 16)
BGImage = pygame.image.load('./Image/Wise+Gray+Dark+Tone.JPG')


def DrawInfo(screen, frame_data):

    DY = 17
    X_ORG = 10
    Y_ORG = 5
    screen.blit(pygame.transform.scale(BGImage, screen.get_size()), (0, 0))

    pos = [X_ORG, Y_ORG]
    # ------------------
    pos[1] += DY
    display = '========== Information =========='
    label = InfoFont2.render(display, 1, Color.goldenrod)
    screen.blit(label, tuple(pos))

#    # Selected Track
#    pos[1] += DY
#    display = 'Idx | Stat | Mov | PosX | PosY | VelX | VelY | HAng | Len | Wid'
#    label = InfoFont3.render(display, 1, Color.blue)
#    screen.blit(label, tuple(pos))

#    colorL = Color.white
#    for idx in range(len(SelData['SimTrk'])):
#        pos[1] += DY
#        TrkDict = TrackDataParsing(Sim_TrkInfo[SelData['SimTrk'][idx]])
#        display = GetTrkDataStr(TrkDict)
#        label = InfoFont3.render(display, 1, colorL)
#        screen.blit(label, tuple(pos))


#def GetTrkDataStr(TrkDict):

#    TrkInfo = (TrkDict['TrkIdx'], TrkDict['Status'], TrkDict['MovStat'],
#               TrkDict['PosX'], TrkDict['PosY'], TrkDict['VelX'], TrkDict['VelY'],
#               TrkDict['HeadingAng'], TrkDict['Length'], TrkDict['Width'])
#    display = '%03d | %03d | %03d | %3.1f | %3.1f | %3.1f | %3.1f | %d | %3.1f | %3.1f' % TrkInfo

#    return display