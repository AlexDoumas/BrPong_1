import numpy as np
from scipy.spatial import distance as dist
from collections import OrderedDict
import cv2
import imutils

import matplotlib.pyplot as plt
import matplotlib.image as mpimg


class PongPreprocessor:
    """On Pong the left paddle is red, the ball is white and the right paddle is green, so object identification is
    based on color"""
    def __init__(self):
        # initialize img and lab
        self.img = None
        self.img_lab = None

        # initialize the colors dictionary, containing the color
        # name as the key and the RGB tuple as the value
        self.colors = OrderedDict()
        self.colors['orange'] = (213, 130, 74)
        self.colors['green'] = (92, 186, 92)
        self.colors['white'] = (236, 236, 236)

        # allocate memory for the L*a*b* image, then initialize
        # the color names list
        self.lab = np.zeros((len(self.colors), 1, 3), dtype="uint8")
        self.colorNames = []

        # loop over the colors dictionary
        for (i, (name, rgb)) in enumerate(self.colors.items()):
            # update the L*a*b* array and the color names list
            self.lab[i] = rgb
            self.colorNames.append(name)

        # convert the L*a*b* array from the RGB color space
        # to L*a*b*
        self.lab = cv2.cvtColor(self.lab, cv2.COLOR_RGB2LAB)

        # initialize boundaries in BGR... no need really
        self.boundaries = OrderedDict()
        for (name, rgb) in self.colors.items():
            to_bgr = list(rgb)
            to_bgr[0], to_bgr[2] = to_bgr[2], to_bgr[0]
            self.boundaries[name] = (np.array(to_bgr), np.array(to_bgr))

    def read_from_file(self, file_name):
        # read from file
        self.img = cv2.imread(file_name)
        self.img_lab = cv2.cvtColor(self.img, cv2.COLOR_BGR2LAB)

    def read_from_array(self, array):
        # read from rgb array, write bgr img
        self.img = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        self.img_lab = cv2.cvtColor(self.img, cv2.COLOR_BGR2LAB)

    def label(self, c):
        """return: a color label for an individual contour c"""
        # construct a mask for the contour, then compute the
        # average L*a*b* value for the masked region
        mask = np.zeros(self.img_lab.shape[:2], dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)
        mean = cv2.mean(self.img_lab, mask=mask)[:3]

        # initialize the minimum distance found thus far
        min_dist = (np.inf, None)

        # loop over the known L*a*b* color values
        for (i, row) in enumerate(self.lab):
            # compute the distance between the current L*a*b*
            # color value and the mean of the image
            d = dist.euclidean(row[0], mean)

            # if the distance is smaller than the current distance,
            # then update the bookkeeping variable
            if d < min_dist[0]:
                min_dist = (d, i)

        # return the name of the color with the smallest distance
        return self.colorNames[min_dist[1]]

    def get_contours(self):
        """return a list of contours"""
        # Draw filled black rectangles at the top and bottom of the img
        cv2.rectangle(self.img, (0, 0), (320, 33), (17, 72, 144), -1)
        cv2.rectangle(self.img, (0, 194), (320, 210), (17, 72, 144), -1)

        # generate masks based on color
        masked_imgs = []
        # loop over the boundaries
        for (name, boundaries) in self.boundaries.items():
            # find the colors within the specified boundaries and apply the mask
            mask = cv2.inRange(self.img, boundaries[0], boundaries[1])
            masked = cv2.bitwise_and(self.img, self.img, mask=mask)
            masked_imgs.append(masked)

        contours = []
        # convert masked images to grayscale
        for masked in masked_imgs:
            gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)[1]

            # find contour in the thresholded image
            contour = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            contour = contour[0] if imutils.is_cv2() else contour[1]
            if contour:
                contours.append(contour[0])  # contour[0] because is a list

        return contours

    def get_boxes(self):
        """Returns an array of boxes in order: orange paddle, green paddle, ball.
        Each box is x,y,w,h"""
        # get contours
        contours = self.get_contours()

        # get labels
        labels = [self.label(c) for c in contours]

        # get boxes
        boxes = [list(cv2.boundingRect(c)) for c in contours]

        # order boxes
        ordered_boxes = []
        ordered_colors = []
        for color, rgb in self.colors.items():
            if color in labels:
                ordered_boxes.append(boxes[labels.index(color)])
                ordered_colors.append(color)
            else:
                ordered_boxes.append([0, 0, 0, 0])
                ordered_colors.append(color)

        ordered_boxes = np.array(ordered_boxes)
        return ordered_boxes  # .flatten()

    def get_center_objects(self, array):
        """get the x-y coordinates of the center for orange paddle, ball, green paddle"""

        self.read_from_array(array)
        feature_array = self.get_boxes()

        # get_screen_features returns (x, y, w, h) orange paddle, green paddle, ball
        xc_paddle1 = feature_array[0][0] + feature_array[0][2] / 2
        yc_paddle1 = feature_array[0][1] + feature_array[0][3] / 2

        xc_paddle2 = feature_array[1][0] + feature_array[1][2] / 2
        yc_paddle2 = feature_array[1][1] + feature_array[1][3] / 2

        xc_ball = feature_array[2][0] + feature_array[2][2] / 2
        yc_ball = feature_array[2][1] + feature_array[2][3] / 2

        return np.array([xc_paddle1, yc_paddle1, xc_ball, yc_ball, xc_paddle2, yc_paddle2])

    def get_y(self, array):
        """Get the Y-vector used for training"""
        centers = self.get_center_objects(array)
        xc_paddle1 = centers[0]
        yc_paddle1 = centers[1]
        xc_ball = centers[2]
        yc_ball = centers[3]
        xc_paddle2 = centers[4]
        yc_paddle2 = centers[5]

        x_paddle1_vec = np.zeros(160, np.uint8)
        x_paddle1_vec[:xc_paddle1] = 1

        y_paddle1_vec = np.zeros(210, np.uint8)
        y_paddle1_vec[:yc_paddle1] = 1

        x_ball_vec = np.zeros(160, np.uint8)
        x_ball_vec[:xc_ball] = 1

        y_ball_vec = np.zeros(210, np.uint8)
        y_ball_vec[:yc_ball] = 1

        x_paddle2_vec = np.zeros(160, np.uint8)
        x_paddle2_vec[:xc_paddle2] = 1

        y_paddle2_vec = np.zeros(210, np.uint8)
        y_paddle2_vec[:yc_paddle2] = 1

        return np.concatenate([x_paddle1_vec, y_paddle1_vec, x_ball_vec, y_ball_vec, x_paddle2_vec, y_paddle2_vec])

    def get_screen_features(self, array):
        # wrapper to get x,y,w,h for ball and paddle
        self.read_from_array(array)
        return self.get_boxes()


class BreakoutPreprocessor:
    """On Breakout the paddle and the ball are red, so object identification is based on position and shape instead."""
    def __init__(self):
        # initialize img and lab
        self.img = None
        self.img_lab = None

        # initialize the colors dictionary, containing the color
        # name as the key and the RGB tuple as the value
        self.colors = OrderedDict()
        self.colors['red'] = (200, 72, 72)

        # allocate memory for the L*a*b* image, then initialize
        # the color names list
        self.lab = np.zeros((len(self.colors), 1, 3), dtype="uint8")
        self.colorNames = []

        # loop over the colors dictionary
        for (i, (name, rgb)) in enumerate(self.colors.items()):
            # update the L*a*b* array and the color names list
            self.lab[i] = rgb
            self.colorNames.append(name)

        # convert the L*a*b* array from the RGB color space
        # to L*a*b*
        self.lab = cv2.cvtColor(self.lab, cv2.COLOR_RGB2LAB)

        # initialize boundaries in BGR
        self.boundaries = OrderedDict()
        for (name, rgb) in self.colors.items():
            to_bgr = list(rgb)
            to_bgr[0], to_bgr[2] = to_bgr[2], to_bgr[0]
            self.boundaries[name] = (np.array(to_bgr)-20, np.array(to_bgr)+20)

    def read_from_file(self, file_name):
        # read from file
        self.img = cv2.imread(file_name)
        self.img_lab = cv2.cvtColor(self.img, cv2.COLOR_BGR2LAB)

    def read_from_array(self, array):
        # read from rgb array, write bgr img
        self.img = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        self.img_lab = cv2.cvtColor(self.img, cv2.COLOR_BGR2LAB)

    def get_contours(self):
        """
        :return: list of contours
        """
        # check self.img...
        # plt.imshow(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
        # plt.show()

        # Draw filled black rectangles at the top, left and right of the img
        cv2.rectangle(self.img, (0, 0), (160, 32), (0, 0, 0), -1)
        cv2.rectangle(self.img, (0, 0), (7, 210), (0, 0, 0), -1)
        cv2.rectangle(self.img, (152, 0), (160, 210), (0, 0, 0), -1)
        # Also cover the red bricks
        cv2.rectangle(self.img, (8, 56), (152, 62), (0, 0, 0), -1)

        # check self.img...
        # plt.imshow(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
        # plt.show()

        # generate masks based on color
        masked_imgs = []
        # loop over the boundaries
        for (name, boundaries) in self.boundaries.items():
            # find the colors within the specified boundaries and apply the mask
            mask = cv2.inRange(self.img, boundaries[0], boundaries[1])
            masked = cv2.bitwise_and(self.img, self.img, mask=mask)
            masked_imgs.append(masked)

        # convert masked images to grayscale
        for masked in masked_imgs:
            gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]

            # find contours in the thresholded image
            contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            contours = contours[0] if imutils.is_cv2() else contours[1]

        return contours

    def get_area(self, bounding_rect):
        """Get the area of a single opencv bounding rectangle"""
        # every bounding box is composed of: x,y,w,h
        return bounding_rect[2] * bounding_rect[3]

    def separate_ball_paddle(self, bounding_rect):
        # bounding rectangle coordiantes
        bounding_x = bounding_rect[0]
        bounding_y = bounding_rect[1]
        bounding_w = bounding_rect[2]
        bounding_h = bounding_rect[3]

        # grayscale and thresh
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]

        # find contours in the thresholded image
        contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if imutils.is_cv2() else contours[1]

        # contours a a list of numpy arrays (one is this case)
        # the array contains x,y indexes of the vertices
        vertices = contours[0]
        # remove unnecessary dimension
        vertices = np.squeeze(vertices, axis=1)

        # If the bounding rectangle is above the fixed y-coordinate of the paddle (189), the ball is above the paddle
        if bounding_y < 189:

            # the highest, leftmost vertex is the ball (x, y) coordinate
            ball_x = vertices[0][0]
            ball_y = vertices[0][1]
            # difference between the y-coordinates of the first and last vertices corresponds to the  width of the ball
            # min w value is 1
            ball_w = max(abs(ball_x - vertices[-1][0]) + 1, 1)
            # assume ball height is always 4
            ball_h = 4

            # paddle y-coordinate is always 189, paddle height is always 4
            paddle_y = 189
            paddle_h = 4
            # if the bounding rectangle has the same width as the paddle the x-coordinate is the same
            if bounding_w <= 16:
                paddle_x = bounding_x
                paddle_w = bounding_w
            # if the width of the bounding rectangle is higher than the standard width of the paddle (16)...
            if bounding_w > 16:
                if ball_x == bounding_x:
                    paddle_x = ball_x + ball_w  # is always at the next pixel
                else:
                    paddle_x = bounding_x
                paddle_w = 16

        # if the bounding rectangle is at the level of the paddle, the ball is bellow the paddle
        else:
            # the highest, leftmost vertex is the ball (x, y) coordinate
            paddle_x = vertices[0][0]
            paddle_y = vertices[0][1]
            # the width of the paddle is the standard (16), unless the width of the bounding box is less than that
            if bounding_w >= 16:
                paddle_w = 16
            else:
                paddle_w = bounding_w
            # assume the height of the paddle to be always 4
            paddle_h = 4

            # assume ball width and height
            ball_h = 4
            ball_w = 2

            # infer ball y-coordinate based on vertex most at the bottom
            y_values = []
            for vector in vertices:
                y_values.append(vector[1])
            ball_y = max(y_values) - (ball_h - 1)

            # infer ball x-coordinate from the leftmost vertex under the paddle...
            x_values = []
            for vector in vertices:
                if vector[1] >= paddle_y + paddle_h-1:
                    x_values.append(vector[0])
            ball_x = min(x_values)

        # check the vertices
        counter = 1
        for cnt in contours[0]:
            indexes = cnt[0, :]
            if counter % 2 == 0:
                # green
                self.img[indexes[1], indexes[0], :] = [0, 255, 0]
            else:
                # blue
                self.img[indexes[1], indexes[0], :] = [0, 0, 255]
            counter += 1

        return [ball_x, ball_y, ball_w, ball_h], [paddle_x, paddle_y, paddle_w, paddle_h]

    def get_boxes(self):
        """
        :param contours: list of contours
        :return: array of boxes in order: orange paddle, green paddle, ball
        """
        # get contours
        contours = self.get_contours()

        # get labels
        # labels = [self.label(c) for c in contours]

        # get boxes
        boxes = [list(cv2.boundingRect(c)) for c in contours]

        # Check whether the ball is touching the paddle
        # in which case there will be just one box with area bigger than 16*4
        if len(boxes) == 1 and self.get_area(boxes[0]) > 64:
            # Get rectangle
            rect = boxes[0]
            # Get x,y,w,h for ball and paddle
            ball, paddle = self.separate_ball_paddle(rect)

        # If there is more than one box get ball and paddle individually
        else:
            # ball has shape (w, h) (2, 4) and paddle (16, 4)
            # the ball has always a width of max 2 and a max height of 4
            ball = [x for x in boxes if x[2] <= 2 and x[3] <= 4]
            if not ball:
                ball = [0, 0, 0, 0]
            else:
                ball = ball[0]

            # for the paddle include the y coordinate as it never changes....
            # something like if y = number and w > h... would be bullet proof
            paddle = [x for x in boxes if x[1] == 189 and 8 <= x[2] <= 16 and x[3] == 4]
            if not paddle:
                paddle = [0, 0, 0, 0]
            else:
                paddle = paddle[0]

        ordered_boxes = ball + paddle

        return np.array(ordered_boxes)

    def get_center_objects(self, array):
        """get the x-y coordinates of the center for the ball and paddle"""

        self.read_from_array(array)
        feature_array = self.get_boxes()

        # get_screen_features returns (x, y, w, h) ball and paddle
        xc_ball = feature_array[0] + feature_array[2] / 2
        yc_ball = feature_array[1] + feature_array[3] / 2

        xc_paddle = feature_array[4] + feature_array[6] / 2
        yc_paddle = feature_array[5] + feature_array[7] / 2

        # placeholder for the game controlled paddle in Pong
        xc_game_paddle = 0
        yc_game_paddle = 0

        return np.array([xc_game_paddle, yc_game_paddle, xc_ball, yc_ball, xc_paddle, yc_paddle])

    def get_y(self, array):
        """Get the Y-vector used for training"""
        centers = self.get_center_objects(array)
        xc_ball = centers[2]
        yc_ball = centers[3]
        xc_paddle = centers[4]
        yc_paddle = centers[5]

        x_ball_vec = np.zeros(160, np.uint8)
        x_ball_vec[:xc_ball] = 1

        y_ball_vec = np.zeros(210, np.uint8)
        y_ball_vec[:yc_ball] = 1

        x_paddle_vec = np.zeros(160, np.uint8)
        x_paddle_vec[:xc_paddle] = 1

        y_paddle_vec = np.zeros(210, np.uint8)
        y_paddle_vec[:yc_paddle] = 1

        # placeholders for game controlled paddle
        x_game_paddle = np.zeros(160, np.uint8)
        y_game_paddle = np.zeros(210, np.uint8)

        return np.concatenate([x_game_paddle, y_game_paddle, x_ball_vec, y_ball_vec, x_paddle_vec, y_paddle_vec])

    def get_screen_features_breakout(self, array):
        # wrapper to get x,y,w,h for ball and paddle
        self.read_from_array(array)
        return self.get_boxes()


# Usage of preprocessors
# p = PongPreprocessor()
# p = BreakoutPreprocessor()
# features = p.get_center_objects(img)
# feature_vec = p.get_y(img)

def get_next_state_features(current, obs):
    # Next state is composed by the last 3 feature vectors of the previous state and the new observation
    return np.append(current[6:], obs, axis=0)


def transform_reward(reward):
    return np.sign(reward)


