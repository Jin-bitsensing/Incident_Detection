def VisionObjectDataParsing(VobjInfo):
    dic = dict()
    dic['class_id'] = int(VobjInfo[0])
    dic['confidence'] = VobjInfo[1]
    dic['height'    ] = VobjInfo[2]
    dic['width'     ] = VobjInfo[3]
    dic['x_location'] = VobjInfo[4]
    dic['y_location'] = VobjInfo[5]

    return dic


def TrackDataParsing(TrkInfo):
    dic = dict()
    dic['idx']              = TrkInfo[0 ]
    dic['upd_state']        = TrkInfo[1 ]
    dic['reserved']         = TrkInfo[2 ]
    dic['mov_state']        = TrkInfo[3 ]
    dic['alive_age']        = TrkInfo[4 ]
    dic['xpos']             = TrkInfo[5 ]
    dic['ypos']             = TrkInfo[6 ]
    dic['refxpos']          = TrkInfo[7 ]
    dic['refypos']          = TrkInfo[8 ]
    dic['xvel']             = TrkInfo[9 ]
    dic['yvel']             = TrkInfo[10]
    dic['heading']          = TrkInfo[11]
    dic['power']            = TrkInfo[12]
    dic['width']            = TrkInfo[13]
    dic['length']           = TrkInfo[14]
    dic['class']            = TrkInfo[15]
    dic['fusion_type']      = TrkInfo[16]
    dic['fusion_age']       = TrkInfo[17]
    dic['height']           = TrkInfo[18]
    dic['lane']             = TrkInfo[19]
    dic['occupancy_time']   = TrkInfo[20]

    return dic


def ObjectDataParsing(ObjInfo):
    dic = dict()
    dic['R'] = ObjInfo[0]
    dic['V'] = ObjInfo[1]
    dic['AziAng'] = ObjInfo[2]
    dic['EleAng'] = ObjInfo[3]
    dic['Pow'] = ObjInfo[4]
    dic['RCS'] = ObjInfo[5]
    dic['Chirp'] = int(ObjInfo[6])
    dic['Beam'] = int(ObjInfo[7])
    dic['IdxR'] = int(ObjInfo[8])
    dic['IdxD'] = int(ObjInfo[9])
    dic['MergeIdx'] = int(ObjInfo[10])
    dic['NumTrk'] = int(ObjInfo[11])
    dic['GFStep'] = int(ObjInfo[12])
    dic['NoiseVar'] = ObjInfo[13]
    dic['TargetProb'] = ObjInfo[14]
    dic['MeasIdx'] = int(ObjInfo[15])
    dic['TklIdx'] = int(ObjInfo[16])
    dic['TrkIdx'] = int(ObjInfo[17])

    return dic

def ObjectDataParsing_Log(ObjInfo):
    dic = dict()
    dic['R'] = ObjInfo[0]
    dic['AziAng'] = ObjInfo[1]
    dic['V'] = ObjInfo[2]

    return dic


def TrackDataParsing_Log(TrkInfo):
    dic = dict()
    dic['TrkIdx']           = int(TrkInfo[0])
    dic['Status']           = int(TrkInfo[1])
    dic['UpdStat']          = int(TrkInfo[2])
    dic['MovStat']          = int(TrkInfo[3])
    dic['AliveAge']         = int(TrkInfo[4])
    dic['PosX']             = TrkInfo[5]
    dic['PosY']             = TrkInfo[6]
    dic['RefPosX']          = TrkInfo[7]
    dic['RefPosY']          = TrkInfo[8]
    dic['VelX']             = TrkInfo[9]
    dic['VelY']             = TrkInfo[10]
    dic['HeadingAng']       = TrkInfo[11]
    dic['POW']              = TrkInfo[12]
    dic['Width']            = TrkInfo[13]
    dic['Length']           = TrkInfo[14]
    dic['Class']            = TrkInfo[15]
    dic['FusionType']       = TrkInfo[16]
    dic['PosZ']             = TrkInfo[17]
    dic['Height']           = TrkInfo[18]
    dic['Lane']             = TrkInfo[19]
    dic['OccupancyTime']    = TrkInfo[20]

    return dic