import sys
import pygame


class DisplayToolKeyState:
    def __init__(self):
        self.Key_Num = 0

        self.Key_q = False
        self.Key_w = False
        self.Key_e = False
        self.Key_r = False
        self.Key_t = False
        self.Key_y = False
        self.Key_u = False
        self.Key_i = False
        self.Key_o = False
        self.Key_p = False
        self.Key_a = False
        self.Key_s = False
        self.Key_d = False
        self.Key_f = False
        self.Key_g = False
        self.Key_h = False
        self.Key_j = False
        self.Key_k = False
        self.Key_l = False
        self.Key_z = False
        self.Key_x = False
        self.Key_c = False
        self.Key_v = False
        self.Key_b = False
        self.Key_n = False
        self.Key_m = False

        self.MouseDrag_on = False
        self.MouseDrag_size = (0, 0)
        self.MouseLeftDown_on = False
        self.MouseLeftDown_pos = (0, 0)
        self.MouseLeftUp_on = False
        self.MouseRightDown_on = False
        self.MouseRightDown_pos = (0, 0)


    def KeyEvent(self, event_key):
        if event_key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event_key == pygame.K_0:
            self.Key_Num = 0
        if event_key == pygame.K_1:
            self.Key_Num = 1
        if event_key == pygame.K_2:
            self.Key_Num = 2
        if event_key == pygame.K_3:
            self.Key_Num = 3
        if event_key == pygame.K_4:
            self.Key_Num = 4
        if event_key == pygame.K_5:
            self.Key_Num = 5
        if event_key == pygame.K_6:
            self.Key_Num = 6
        if event_key == pygame.K_7:
            self.Key_Num = 7
        if event_key == pygame.K_8:
            self.Key_Num = 8
        if event_key == pygame.K_9:
            self.Key_Num = 9

        if event_key == pygame.K_q:
            self.Key_q = not self.Key_q
        if event_key == pygame.K_w:
            self.Key_w = not self.Key_w
        if event_key == pygame.K_e:
            self.Key_e = not self.Key_e
        if event_key == pygame.K_r:
            self.Key_r = not self.Key_r
        if event_key == pygame.K_t:
            self.Key_t = not self.Key_t
        if event_key == pygame.K_y:
            self.Key_y = not self.Key_y
        if event_key == pygame.K_u:
            self.Key_u = not self.Key_u
        if event_key == pygame.K_i:
            self.Key_i = not self.Key_i
        if event_key == pygame.K_o:
            self.Key_o = not self.Key_o
        if event_key == pygame.K_p:
            self.Key_p = not self.Key_p
        if event_key == pygame.K_a:
            self.Key_a = not self.Key_a
        if event_key == pygame.K_s:
            self.Key_s = not self.Key_s
        if event_key == pygame.K_d:
            self.Key_d = not self.Key_d
        if event_key == pygame.K_f:
            self.Key_f = not self.Key_f
        if event_key == pygame.K_g:
            self.Key_g = not self.Key_g
        if event_key == pygame.K_h:
            self.Key_h = not self.Key_h
        if event_key == pygame.K_j:
            self.Key_j = not self.Key_j
        if event_key == pygame.K_k:
            self.Key_k = not self.Key_k
        if event_key == pygame.K_l:
            self.Key_l = not self.Key_l
        if event_key == pygame.K_z:
            self.Key_z = not self.Key_z
        if event_key == pygame.K_x:
            self.Key_x = not self.Key_x
        if event_key == pygame.K_c:
            self.Key_c = not self.Key_c
        if event_key == pygame.K_v:
            self.Key_v = not self.Key_v
        if event_key == pygame.K_b:
            self.Key_b = not self.Key_b
        if event_key == pygame.K_n:
            self.Key_n = not self.Key_n
        if event_key == pygame.K_m:
            self.Key_m = not self.Key_m



    def MouseEvent(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:    # Left button
                pygame.mouse.get_rel()
                self.MouseLeftDown_pos = event.pos
                self.MouseLeftDown_on = True
                self.MouseDrag_size = (0, 0)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:    # Left button
                self.MouseLeftUp_on = True
                self.MouseLeftDown_on = False
                self.MouseDrag_on = False

            elif event.button == 2:  # middle button
                Test_A = 2

            elif event.button == 3:  # Right button
                self.MouseRightDown_on = True
                self.MouseRightDown_pos = event.pos

            elif event.button == 4:  # Mouse Scroll Up
                Test_A = 4

            elif event.button == 5:  # Mouse Scroll Down
                Test_A = 5

        if event.type == pygame.MOUSEMOTION:
            self.MouseDrag_on = True
            self.MouseDrag_size = (event.pos[0] - self.MouseLeftDown_pos[0], event.pos[1] - self.MouseLeftDown_pos[1])

