
def GetTRInput(LeftTop_Pos, RightBottom_Pos):

    RightBottom_Offset = RightBottom_Pos[0] - LeftTop_Pos[0], RightBottom_Pos[1] - LeftTop_Pos[1]
    PhysRect = LeftTop_Pos + RightBottom_Offset

    return PhysRect



def GetMouseWinPos(rect, ViewPos, ViewSize):

    p1 = (rect[0], rect[1])
    p2 = (rect[0] + rect[2], rect[1] + rect[3])

    SelView = -1
    outRect = (0, 0, 0, 0)

    for idx in range(len(ViewPos)):
        # Selected VIEW
        if (p1[0] > ViewPos[idx][0]) and (p1[1] > ViewPos[idx][1]) and (p1[0] < ViewPos[idx][0]+ViewSize[idx][0]) and (p1[1] < ViewPos[idx][1]+ViewSize[idx][1]):
            if (p2[0] > ViewPos[idx][0]) and (p2[1] > ViewPos[idx][1]) and (p2[0] < ViewPos[idx][0]+ViewSize[idx][0]) and (p2[1] < ViewPos[idx][1]+ViewSize[idx][1]):
                SelView = idx
                outRect = (p1[0]-ViewPos[idx][0], p1[1]-ViewPos[idx][1], rect[2], rect[3])

    return SelView, outRect


