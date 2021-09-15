class TransRect:

    def __init__(self, phys_rect, disp_rect, rotation):       # rect = (x_init, y_init, x_width, y_height)

        self.PhysRect = list(phys_rect)
        self.DispRect = list(disp_rect)
        self.R        = list(rotation)

        self.S        = [1,1]                   # Scale
        self.O        = [0,0]                   # Offset
        self.UpdateScaleOffset(self.PhysRect, self.DispRect)

        # backup original value as initial setting
        self.S_Org = list(self.S)
        self.O_Org = list(self.O)

        return

    def UpdateScaleOffset(self, prect, drect=None):

        if drect==None: drect = self.DispRect

        # 1. Scale
        # S[0] = (R1*w + R3*h)/W             # Scale Phys x to Disp (?)
        # S[1] = (R2*w + R4*h)/H             # Scale Phys y to Disp (?)
        self.S[0] = 1.0*(self.R[0]*drect[2] + self.R[2]*drect[3])/prect[2]             # Scale Phys x to Disp (?)
        self.S[1] = 1.0*(self.R[1]*drect[2] + self.R[3]*drect[3])/prect[3]             # Scale Phys y to Disp (?)
        #print 'scale: ', self.S
        # 2. Offset
        self.O = [0,0]
        d = (drect[0], drect[1]) 
        P = self.getPointD2P(d)
        self.O[0] = prect[0] - P[0]
        self.O[1] = prect[1] - P[1]
        #print 'offset: ', self.O

        return

    def UpdateScaleOffsetOriginal(self):
        
        self.S = list(self.S_Org)
        self.O = list(self.O_Org)

        return

    def AddOffset(self, pos):
        self.O = [self.O[0]+pos[0],self.O[1]+pos[1]]

    # D2P : Display to Physical Position
    def getPointD2P(self, point):

        #Px = (R1*dx + R3*dy)/S1 + O1
        #Py = (R2*dx + R4*dy)/S2 + O2
        Px = 1.0*(self.R[0]*point[0] + self.R[2]*point[1])/self.S[0] + self.O[0]
        Py = 1.0*(self.R[1]*point[0] + self.R[3]*point[1])/self.S[1] + self.O[1]

        return (Px,Py)

    def getSizeD2P(self, point):

        #Px = (R1*dx + R3*dy)/S1
        #Py = (R2*dx + R4*dy)/S2
        Px = 1.0*(self.R[0]*point[0] + self.R[2]*point[1])/self.S[0]
        Py = 1.0*(self.R[1]*point[0] + self.R[3]*point[1])/self.S[1]

        return (Px,Py)

    def getPointP2D(self, point):

        #dx = R1*S1*(Px-Ox) + R2*S2*(Py-Oy)
        #dy = R3*S1*(Px-Ox) + R4*S2*(Py-Oy)
        dx = int(self.R[0]*self.S[0]*(point[0]-self.O[0]) + self.R[1]*self.S[1]*(point[1]-self.O[1]) )
        dy = int(self.R[2]*self.S[0]*(point[0]-self.O[0]) + self.R[3]*self.S[1]*(point[1]-self.O[1]) )

        return (dx, dy)

    def getSizeP2D(self, point):

        #dx = R1*S1*(Px) + R2*S2*(Py)
        #dy = R3*S1*(Px) + R4*S2*(Py)
        dx = int(self.R[0]*self.S[0]*(point[0]) + self.R[1]*self.S[1]*(point[1]) )
        dy = int(self.R[2]*self.S[0]*(point[0]) + self.R[3]*self.S[1]*(point[1]) )

        return (dx, dy)

    def Test(self):

        print('Test TransRect..')
        print('Display  Rect: ', self.DispRect)
        print('Physical Rect: ', self.PhysRect)

        print('Disp Corner 2 Phys')
        d = (self.DispRect[0], self.DispRect[1])
        print('..', d, '  -->  ', self.getPointD2P(d))
        d = (self.DispRect[0]+self.DispRect[2], self.DispRect[1])
        print('..', d, '  -->  ', self.getPointD2P(d))
        d = (self.DispRect[0], self.DispRect[1] + self.DispRect[3])
        print('..', d, '  -->  ', self.getPointD2P(d))
        d = (self.DispRect[0]+self.DispRect[2], self.DispRect[1] + self.DispRect[3])
        print('..', d, '  -->  ', self.getPointD2P(d))

        print('Phys Corner 2 Disp')
        d = (self.PhysRect[0], self.PhysRect[1])
        print('..', d, '  -->  ', self.getPointP2D(d))
        d = (self.PhysRect[0]+self.PhysRect[2], self.PhysRect[1])
        print('..', d, '  -->  ', self.getPointP2D(d))
        d = (self.PhysRect[0], self.PhysRect[1] + self.PhysRect[3])
        print('..', d, '  -->  ', self.getPointP2D(d))
        d = (self.PhysRect[0]+self.PhysRect[2], self.PhysRect[1] + self.PhysRect[3])
        print('..', d, '  -->  ', self.getPointP2D(d))


if __name__ == '__main__':

    display_rect = (0,0,300,800)
    #physical_rect = (200,-20,-200,40)
    #Rotation  = (0,1,-1,0)
    physical_rect = (-20,200,40,-200)
    Rotation  = (1,0,0,1)

    TR = TransRect(physical_rect,display_rect, Rotation)

    TR.Test()

    TR.UpdateScaleOffset((100,-20,-100,40))

    TR.Test()

    TR.UpdateScaleOffsetOriginal()

    TR.Test()
