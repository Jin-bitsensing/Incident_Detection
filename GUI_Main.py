import os
import sys
import shutil
import pygame
import h5py
import time as stopwatch

from GUI_Class import GUI
from pyqtgraph.Qt import QtGui
from GUI_DataParsing import VisionObjectDataParsing
from Trk_VobjTracking import VobjTracking 


######### Static function ##########
def GetFrameData(h5_file, group_name):
    if h5_file is not None:
        frame_data = h5_file[group_name]
    else:
        frame_data = None

    return frame_data


######### Global Variable ##########
WIN_CAM_SIZE = 640, 480
scaling_factor = [1920 / 640, 1080 / 480] # for atm220 data only

# Loop
LOOP_BASIC = 1
LOOP_FAST = 20
LOOP_PLAY = 1

PLAY_ON = False
DISP_STOPWATCH = False


######### Initialization ##########
pygame.init()
pygame.mixer.quit()
app = QtGui.QApplication([])
desktop_widget = app.desktop()
primary_screen = desktop_widget.primaryScreen()
screen_rect = desktop_widget.screenGeometry(primary_screen)
SCREEN_SIZE = screen_rect.width(), screen_rect.height()
WIN_VIEW_SIZE = int(SCREEN_SIZE[0]*0.2), int(SCREEN_SIZE[1]*0.64)


######### Data Loading ##########
file_handle = open('Config_DataPath.ini', 'r')
file_name = file_handle.read().splitlines()
file_name = file_name[1]
file_handle.close()

if os.path.isfile(file_name):
    input_file_h5 = (h5py.File(file_name, 'r'))
else:
    sys.exit('no input file')


######### Tracking #########
# Tracker initialization
print('Tracking process start')
vobj_tracker = VobjTracking()
vobj_trk_hist = []
for frame_idx in range(1, len(input_file_h5) + 1):
    print('Frame #%d processing' % frame_idx)

    # Data loading
    start = stopwatch.time()
    group_name = 'SCAN_{:05d}'.format(frame_idx)
    frame_data = GetFrameData(input_file_h5, group_name)
    end = stopwatch.time()
    if DISP_STOPWATCH: print('H5 file loading = %f ms' %((end - start) * 1000))

    # dump to ai object input interface
    start = stopwatch.time()
    ai_object_list = []
    for i_obj in range(len(frame_data['AI'].value)):

        if frame_data['AI'].value[i_obj][1] > 0:
            # ai object data parsing
            ai_object_dict = VisionObjectDataParsing(frame_data['AI'].value[i_obj])

            # Re-scaling object position
            ai_object_dict['height']        *= scaling_factor[1]   # height
            ai_object_dict['width']         *= scaling_factor[0]   # width
            ai_object_dict['x_location']    *= scaling_factor[0]   # x
            ai_object_dict['y_location']    *= scaling_factor[1]   # y

            # build new list
            ai_object_list.append(ai_object_dict)

        else:
            break
        
    end = stopwatch.time()
    if DISP_STOPWATCH: print('AI object loading = %f ms' %((end - start) * 1000))

    # Tracking
    start = stopwatch.time()
    vobj_tracker.tracking(ai_object_list)
    end = stopwatch.time()
    if DISP_STOPWATCH: print('Tracking = %f ms' %((end - start) * 1000))
    
    # Store simulation output
    vobj_trk_hist.append(vobj_tracker.obj_in_nms)

print('Tracking process finished')


######### Output GUI #########
print('\nOutput display')
output_gui = GUI(WIN_VIEW_SIZE, WIN_CAM_SIZE, SCREEN_SIZE, vobj_trk_hist, vobj_tracker.cmr_model)

FrameIndexOld = 0
FrameIndexCur = 0
keys1 = pygame.key.get_pressed()
keys2 = pygame.key.get_pressed()
temp_cnt = 0

FrameIndexMin = 1
FrameIndexMax = len(input_file_h5)
FrameIndexCur = FrameIndexMin
    
while True:
    if FrameIndexOld != FrameIndexCur:
        GroupName = 'SCAN_{:05d}'.format(FrameIndexCur)
        frame_data = GetFrameData(input_file_h5, GroupName)

        output_gui.display(output_gui.DisplaySurf, frame_data, FrameIndexCur)

        if PLAY_ON:
            pygame.time.delay(40)

        pygame.display.update()

    FrameIndexOld = FrameIndexCur


    # Key Input Event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.VIDEORESIZE:
            output_gui.VideoResizeEvent(event, frame_data, FrameIndexCur)

        # KeyBoard Event
        elif event.type == pygame.KEYDOWN:

            # Move
            if event.key == pygame.K_LEFT:  # Left
                if FrameIndexCur - LOOP_BASIC > FrameIndexMin:
                    FrameIndexCur -= LOOP_BASIC
                else:
                    FrameIndexCur = FrameIndexMin
            elif event.key == pygame.K_RIGHT:  # Right
                if FrameIndexCur + LOOP_BASIC < FrameIndexMax:
                    FrameIndexCur += LOOP_BASIC
                else:
                    FrameIndexCur = FrameIndexMax
            elif event.key == pygame.K_UP:  # Up
                if FrameIndexCur + LOOP_FAST < FrameIndexMax:
                    FrameIndexCur += LOOP_FAST
                else:
                    FrameIndexCur = FrameIndexMax
            elif event.key == pygame.K_DOWN:  # Down
                if FrameIndexCur - LOOP_FAST > FrameIndexMin:
                    FrameIndexCur -= LOOP_FAST
                else:
                    FrameIndexCur = FrameIndexMin
            elif event.key == pygame.K_SPACE:  # Play
                PLAY_ON = not PLAY_ON

            else:
                output_gui.KeyState.KeyEvent(event.key)
                # do nothing

            output_gui.display(output_gui.DisplaySurf, frame_data, FrameIndexCur)

        # Mouse Event
        elif (event.type == pygame.MOUSEBUTTONUP) or (event.type == pygame.MOUSEBUTTONDOWN)\
                or ((event.type == pygame.MOUSEMOTION) and (output_gui.KeyState.MouseLeftDown_on)):
            output_gui.KeyState.MouseEvent(event)

            output_gui.display(output_gui.DisplaySurf, frame_data, FrameIndexCur)

        pygame.display.update()



    # Key Pressing
    keys1 = pygame.key.get_pressed()
    if keys1==keys2:
        if keys1[pygame.K_RIGHT]:
            temp_cnt += 1
            input_key = pygame.K_RIGHT
        elif keys1[pygame.K_LEFT]:
            temp_cnt += 1
            input_key = pygame.K_LEFT
        elif keys1[pygame.K_UP]: 
            temp_cnt += 1
            input_key = pygame.K_UP
        elif keys1[pygame.K_DOWN]:
            temp_cnt += 1
            input_key = pygame.K_DOWN
        else:
            temp_cnt = 0
    else:
        temp_cnt = 0

    if temp_cnt > 30000:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=input_key))

    keys2 = keys1


    if PLAY_ON:
        if FrameIndexCur + LOOP_BASIC < FrameIndexMax:
            FrameIndexCur += LOOP_PLAY
        else:
            FrameIndexCur = FrameIndexMax
            PLAY_ON = False

