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
