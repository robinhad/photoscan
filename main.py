from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import numpy as np
import math
from datetime import datetime
MIN_MATCH_COUNT = 10


def getComponents(normalised_homography):
  '''((translationx, translationy), rotation, (scalex, scaley), shear)'''
  a = normalised_homography[0,0]
  b = normalised_homography[0,1]
  c = normalised_homography[0,2]
  d = normalised_homography[1,0]
  e = normalised_homography[1,1]
  f = normalised_homography[1,2]

  p = math.sqrt(a*a + b*b)
  r = (a*e - b*d)/(p)
  q = (a*d+b*e)/(a*e - b*d)

  translation = (round(c,2),round(f,2))
  scale = (round(p,2),round(r,2))
  shear = round(q,2)
  theta = round(math.atan2(b,a),2)

  return (translation, theta, scale, shear)


class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)
        # Initiate SIFT detector
        self.sift = cv2.AKAZE_create()
        self.img1 = cv2.UMat(cv2.imread('box_in_scene.JPG',0))        # queryImage
        self.kp1, self.des1 = self.sift.detectAndCompute(self.img1,None)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.flann = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.max_matches = 0
        self.max_matches_m = ()
        self.last_match_time = datetime.now()


    def update(self, dt):
        ret, frame = self.capture.read()
        
        
        if ret:
            img2 = cv2.UMat(frame) # trainImage

            # find the keypoints and descriptors with SIFT
            kp2, des2 = self.sift.detectAndCompute(img2,None)

            matches = self.flann.match(self.des1,des2)
            # store all the good matches as per Lowe's ratio test.
            #good = sorted(matches, key = lambda x:x.distance)
            good = []
            for i in matches:
                if i.distance <= 100:
                    good.append(i)
	    
            if len(good)>MIN_MATCH_COUNT:
                src_pts = np.float32([ self.kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
                matchesMask = mask.ravel().tolist()

                h,w = self.img1.get().shape
                pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
                if M is None:
                    pass
                else:
                    self.max_matches = len(good)
                    self.max_matches_m = M
                    self.last_match_time = datetime.now()
                    components = getComponents(self.max_matches_m)
                    cv2.putText(img2,"Matches: " + str(self.max_matches),(1,30), self.font, 0.6,(255,255,255),2,cv2.LINE_AA)
                    cv2.putText(img2,"Translation: " + str(components[0]),(1,60), self.font, 0.6,(255,255,255),2,cv2.LINE_AA)
                    cv2.putText(img2,"Theta: " + str(components[1]),(1,90), self.font, 0.6,(255,255,255),2,cv2.LINE_AA)
                    cv2.putText(img2,"Scale: " + str(components[2]),(1,120), self.font, 0.6,(255,255,255),2,cv2.LINE_AA)
                    cv2.putText(img2,"Shear: " + str(components[3]),(1,150), self.font, 0.6,(255,255,255),2,cv2.LINE_AA)
                    dst = cv2.perspectiveTransform(pts,self.max_matches_m)
                    img2 = cv2.polylines(img2,[np.int32(dst)],True,(255,255,255),3, cv2.LINE_AA)

            # convert it to texture
            buf1 = cv2.flip(img2.get(),0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(img2.get().shape[1], img2.get().shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture



class CamApp(App):
    def build(self):
        self.capture = cv2.VideoCapture(0)
        self.my_camera = KivyCamera(capture=self.capture, fps=60)
        return self.my_camera

    def on_stop(self):
        #without this, app will not exit even if the window is closed
        self.capture.release()


if __name__ == '__main__':
    CamApp().run()
