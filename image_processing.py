import cv2
import numpy as np
import math
import base64
MIN_MATCH_COUNT = 10

def rotate_image(image, angle):
    """
    Rotates an OpenCV 2 / NumPy image about it's centre by the given angle
    (in degrees). The returned image will be large enough to hold the entire
    new image, with a black background
    """

    # Get the image size
    # No that's not an error - NumPy stores image matricies backwards
    image_size = (image.shape[1], image.shape[0])
    image_center = tuple(np.array(image_size) / 2)

    # Convert the OpenCV 3x2 rotation matrix to 3x3
    rot_mat = np.vstack(
        [cv2.getRotationMatrix2D(image_center, angle, 1.0), [0, 0, 1]]
    )

    rot_mat_notranslate = np.matrix(rot_mat[0:2, 0:2])

    # Shorthand for below calcs
    image_w2 = image_size[0] * 0.5
    image_h2 = image_size[1] * 0.5

    # Obtain the rotated coordinates of the image corners
    rotated_coords = [
        (np.array([-image_w2,  image_h2]) * rot_mat_notranslate).A[0],
        (np.array([ image_w2,  image_h2]) * rot_mat_notranslate).A[0],
        (np.array([-image_w2, -image_h2]) * rot_mat_notranslate).A[0],
        (np.array([ image_w2, -image_h2]) * rot_mat_notranslate).A[0]
    ]

    # Find the size of the new image
    x_coords = [pt[0] for pt in rotated_coords]
    x_pos = [x for x in x_coords if x > 0]
    x_neg = [x for x in x_coords if x < 0]

    y_coords = [pt[1] for pt in rotated_coords]
    y_pos = [y for y in y_coords if y > 0]
    y_neg = [y for y in y_coords if y < 0]

    right_bound = max(x_pos)
    left_bound = min(x_neg)
    top_bound = max(y_pos)
    bot_bound = min(y_neg)

    new_w = int(abs(right_bound - left_bound))
    new_h = int(abs(top_bound - bot_bound))

    # We require a translation matrix to keep the image centred
    trans_mat = np.matrix([
        [1, 0, int(new_w * 0.5 - image_w2)],
        [0, 1, int(new_h * 0.5 - image_h2)],
        [0, 0, 1]
    ])

    # Compute the tranform for the combined rotation and translation
    affine_mat = (np.matrix(trans_mat) * np.matrix(rot_mat))[0:2, :]

    # Apply the transform
    result = cv2.warpAffine(
        image,
        affine_mat,
        (new_w, new_h),
        flags=cv2.INTER_LINEAR
    )

    return result


def largest_rotated_rect(w, h, angle):
    """
    Given a rectangle of size wxh that has been rotated by 'angle' (in
    radians), computes the width and height of the largest possible
    axis-aligned rectangle within the rotated rectangle.

    Original JS code by 'Andri' and Magnus Hoff from Stack Overflow

    Converted to Python by Aaron Snoswell
    """

    quadrant = int(math.floor(angle / (math.pi / 2))) & 3
    sign_alpha = angle if ((quadrant & 1) == 0) else math.pi - angle
    alpha = (sign_alpha % math.pi + math.pi) % math.pi

    bb_w = w * math.cos(alpha) + h * math.sin(alpha)
    bb_h = w * math.sin(alpha) + h * math.cos(alpha)

    gamma = math.atan2(bb_w, bb_w) if (w < h) else math.atan2(bb_w, bb_w)

    delta = math.pi - alpha - gamma

    length = h if (w < h) else w

    d = length * math.cos(alpha)
    a = d * math.sin(alpha) / math.sin(delta)

    y = a * math.cos(gamma)
    x = y * math.tan(gamma)

    return (
        bb_w - 2 * x,
        bb_h - 2 * y
    )


def crop_around_center(image, width, height):
    """
    Given a NumPy / OpenCV 2 image, crops it to the given width and height,
    around it's centre point
    """

    image_size = (image.shape[1], image.shape[0])
    image_center = (int(image_size[0] * 0.5), int(image_size[1] * 0.5))

    if(width > image_size[0]):
        width = image_size[0]

    if(height > image_size[1]):
        height = image_size[1]

    x1 = int(image_center[0] - width * 0.5)
    x2 = int(image_center[0] + width * 0.5)
    y1 = int(image_center[1] - height * 0.5)
    y2 = int(image_center[1] + height * 0.5)

    return image[y1:y2, x1:x2]

def encode_image_as_string(img):
    retval, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer)


def decode_image_from_string(image_string):
    nparr = np.fromstring(base64.b64decode(image_string), np.uint8)
    return cv2.imdecode(nparr, 0)  # cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def decode_grayscale_image_from_string(image_string):
    nparr = np.fromstring(base64.b64decode(jpg_as_text), np.uint8)
    return cv2.imdecode(nparr, 0)


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
    shear = round(q, 2) #y axis
    theta = round(math.atan2(b, a), 2) #x axis

    return (translation, theta, scale, shear)

def toRadians(radians):
    return round(math.degrees(radians),2)

def find_image_angle_properties(img1, img2):
    print("Initializing comparers")
    surf = cv2.xfeatures2d.SURF_create()
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    font = cv2.FONT_HERSHEY_SIMPLEX
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    img1 = img1
    img2 = img2
    image_height, image_width = img2.shape[0:2]
    img2 = rotate_image(img2, 270)
    img2 = crop_around_center(
        img2,
        *largest_rotated_rect(
            image_width,
            image_height,
            math.radians(270)
        )
    )
    kp1, des1 = surf.detectAndCompute(img1, None)
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
            fontScale = 4
            color = (255, 255, 255)
            fontThickness = 10
            lineHeight = 120
            cv2.putText(img2, "Matches: " + str(matches_count), (1, 1*lineHeight),
                        font, fontScale, color, fontThickness, cv2.LINE_AA)
            cv2.putText(img2, "Translation: " +
                        str(components[0]), (1, 2*lineHeight), font, fontScale, color, fontThickness, cv2.LINE_AA)
            cv2.putText(
                img2, "Theta: " + str(toRadians(components[1])), (1, 3*lineHeight), font, fontScale, color, fontThickness, cv2.LINE_AA)
            cv2.putText(
                img2, "Scale: " + str(components[2]), (1, 4*lineHeight), font, fontScale, color, fontThickness, cv2.LINE_AA)
            cv2.putText(
                img2, "Shear: " + str(toRadians(components[3])), (1, 5*lineHeight), font, fontScale, color, fontThickness, cv2.LINE_AA)
            dst = cv2.perspectiveTransform(pts, matches_data)
            img2 = cv2.polylines(img2, [np.int32(dst)],
                                 True, (255, 255, 255), 3, cv2.LINE_AA)
            return img2, components

    return img2
    

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    img1 = cv2.imread('test.jpg', 0)
    img2 = cv2.imread('test.jpg', 0)
    img = find_image_angle_properties(img1, img2)
    plt.imshow(img, cmap='gray', interpolation='bicubic')
    plt.show()
