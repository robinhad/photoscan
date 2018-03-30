import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
MIN_MATCH_COUNT = 10


def get_components(normalised_homography):
    '''((translationx, translationy), rotation, (scalex, scaley), shear)'''
    a = normalised_homography[0, 0]
    b = normalised_homography[0, 1]
    c = normalised_homography[0, 2]
    d = normalised_homography[1, 0]
    e = normalised_homography[1, 1]
    f = normalised_homography[1, 2]

    p = math.sqrt(a*a + b*b)
    r = (a*e - b*d)/(p)
    q = (a*d+b*e)/(a*e - b*d)

    translation = (round(c, 2), round(f, 2))
    scale = (round(p, 2), round(r, 2))
    shear = round(q, 2)
    theta = round(math.atan2(b, a), 2)

    return (translation, theta, scale, shear)


def find_image_angle_properties():
    surf = cv2.xfeatures2d.SURF_create()
    img1 = cv2.imread('box_in_scene.JPG', 0)  # query image in grayscale mode
    kp1, des1 = surf.detectAndCompute(img1, None)
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    font = cv2.FONT_HERSHEY_SIMPLEX
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    img2 = cv2.imread('box_in_scene.JPG', 0)  # trainImage

    # find the keypoints and descriptors with SURF
    kp2, des2 = surf.detectAndCompute(img2, None)

    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m, n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32(
            [kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32(
            [kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        matches_properties, mask = cv2.findHomography(
            src_pts, dst_pts, cv2.RANSAC, 5.0)

        h, w = img1.shape
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]
                         ).reshape(-1, 1, 2)
        if matches_properties is None:
            pass
        else:
            matches_count = len(good)
            matches_data = matches_properties
            components = get_components(matches_data)
            cv2.putText(img2, "Matches: " + str(matches_count), (1, 30),
                        font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(img2, "Translation: " +
                        str(components[0]), (1, 60), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(
                img2, "Theta: " + str(components[1]), (1, 90), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(
                img2, "Scale: " + str(components[2]), (1, 120), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(
                img2, "Shear: " + str(components[3]), (1, 150), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            dst = cv2.perspectiveTransform(pts, matches_data)
            img2 = cv2.polylines(img2, [np.int32(dst)],
                                 True, (255, 255, 255), 3, cv2.LINE_AA)

    plt.imshow(img2, cmap='gray', interpolation='bicubic')
    plt.show()


if __name__ == '__main__':
    find_image_angle_properties()
