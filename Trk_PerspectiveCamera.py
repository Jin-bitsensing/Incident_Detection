import numpy as np
import math


def RotX(rad):
	return np.array([	[1,					0,					0				], 
						[0,					math.cos(rad),		-math.sin(rad)	],
						[0,					math.sin(rad),		math.cos(rad)	]])

def RotY(rad):
	return np.array([	[math.cos(rad),		0,					math.sin(rad)	],
						[0,					1,					0				],
						[-math.sin(rad),	0,					math.cos(rad)	]])

def RotZ(rad):
	return np.array([	[math.cos(rad),		-math.sin(rad),		0				],
						[math.sin(rad),		math.cos(rad),      0               ],
						[0,					0,					1				]])

class PerspectiveCamera:

    UNDISTORT_N_ITER = 3

    def __init__(self, image_size, intrinsic_parameter, distortion_coefficient, rvec, tvec, scale):        

        ## public
        # Image size = [width, height]
        self.image_size = image_size
        self.scale      = scale

        ## private
        # Intrinsic parameter
        self._fx	= intrinsic_parameter[0]
        self._fy	= intrinsic_parameter[1]
        self._cx	= intrinsic_parameter[2]
        self._cy	= intrinsic_parameter[3]
        self._skew	= intrinsic_parameter[4]
        
        self._k1	= distortion_coefficient[0]
        self._k2	= distortion_coefficient[1]
        self._k3	= distortion_coefficient[2]
        self._p1	= distortion_coefficient[3]
        self._p2	= distortion_coefficient[4]
        
        self._rvec = rvec
        self._tvec = np.reshape(tvec, (3,1))
        

        self.InitCameraMatrix()
        
    def InitCameraMatrix(self):
        
        ############################
        ##### Intrinsic matrix #####
        ############################
        self._K = np.array([[self._fx,  self._skew, self._cx],
                            [0,			self._fy,	self._cy],
                            [0,			0,			1		]])
        
        ############################
        ##### Extrinsic matrix #####
        ############################
        
        Rz = RotZ(math.radians(-90.0))
        Ry = RotY(math.radians(-90.0))
        Rx = RotX(math.radians(180.0))
        
        RzRy = np.matmul(Rz, Ry)
        R_tf = np.matmul(RzRy, Rx)
        
        
        Rz = RotZ(math.radians(self._rvec[2]))  # yaw
        Ry = RotY(math.radians(self._rvec[1]))  # pitch
        Rx = RotX(math.radians(self._rvec[0]))  # roll
        
        RzRy   = np.matmul(Rz, Ry)
        R_inst = np.matmul(RzRy, Rx)
        
        self._R = np.matmul(R_tf, R_inst)
        self._t = np.matmul(self._R, (-1) * self._tvec)
        
        
        #############################
        ##### Projection matrix #####
        #############################
        
        Rt = np.concatenate((self._R, self._t), axis=1)
        self._P = np.matmul(self._K, Rt)
        
        
        #############################
        ##### Homography matrix #####
        #############################
        
        P_z0    = np.delete(self._P, 2, axis=1)
        self._H = np.linalg.inv(P_z0)
        

    def img2wld(self, img):
        img = self.image_undistort(img)
        img_homo = np.reshape(np.append(img, [1]), (3,1))

        wld = np.matmul(self._H, img_homo)
        wld = wld / wld[2]
        wld[2] = 0

        return wld


    def wld2img(self, wld):
        wld_homo = np.reshape(np.append(wld, [1]), (4,1))

        img_homo = np.matmul(self._P, wld_homo)
        img_homo = img_homo / img_homo[2]
        img = np.resize(img_homo, (2,1))
        
        img = self.image_distort(img)
        
        return img
        
        
    def image_undistort(self, pt_src):
        pt_norm = self.image_normalize(pt_src)

        pt_norm_init = pt_norm
        for iter in range(self.UNDISTORT_N_ITER):
            pt_dist = self.image_distort_normal(pt_norm)
            err = pt_dist - pt_norm_init
            pt_norm -= err

        pt_dst = self.image_denormalize(pt_norm)

        return pt_dst
    
        
    def image_distort(pt_src):
        pt_norm = self.image_normalize(pt_src)
        pt_dist = self.image_distort_normal(pt_norm)
        pt_dst = self.image_denormalize(pt_dist)

        return pt_dst


    def image_normalize(self, pt_img):
        pt_norm = np.zeros((2,1))
        pt_norm[1] = (pt_img[1] - self._cy) / self._fy
        pt_norm[0] = (pt_img[0] - self._cx - self._skew * pt_norm[1]) / self._fx

        return pt_norm


    def image_denormalize(self, pt_norm):
        pt_img = np.zeros((2,1))
        pt_img[0] = self._fx * pt_norm[0] + self._cx + self._skew * pt_norm[1]
        pt_img[1] = self._fy * pt_norm[1] + self._cy

        return pt_img


    def image_distort_normal(self, pt_norm):
        # compute radial distortion
        r2 = pt_norm[0] * pt_norm[0] + pt_norm[1] * pt_norm[1];
        
        alpha = self._k1 * (r2)              \
              + self._k2 * (r2 * r2)         \
              + self._k3 * (r2 * r2 * r2);
        
        # compute tangential distortion
        dxTangential = 2 * self._p1 * pt_norm[0] * pt_norm[1] + self._p2 * (r2 + 2 * pt_norm[0] * pt_norm[0]);
        dyTangential = self._p1 * (r2 + 2 * pt_norm[1] * pt_norm[1]) + 2 * self._p2 * pt_norm[0] * pt_norm[1];
        
        pt_dist = np.zeros((2,1))
        pt_dist[0] = pt_norm[0] + pt_norm[0] * alpha + dxTangential;
        pt_dist[1] = pt_norm[1] + pt_norm[1] * alpha + dyTangential;
        
        return pt_dist
