# import the necessary packages
from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
from imutils import perspective
import numpy as np
import argparse
import cv2
import copy, random, math
import pdb

# a class for the image.
class the_image(object):
    def __init__(self, image):
        self.image = image
        self.objects = None
        self.pairs = None

# an object class with fields for necessary properties.
class vis_obj(object):
    def __init__(self, contour, rect, the_image):
        self.contour = contour
        self.min_rect = rect
        self.bounding_rect = None
        self.length = None # in pixels. 
        self.height = None # in pixels.
        self.area = None # in pixels.
        self.allPointsOfContour = None
        self.midpoint = None
        self.position = None
        self.topmost = None
        self.bottommost = None
        self.leftmost = None
        self.rightmost = None
        self.my_image = the_image
        self.my_pairs = None
    
    # function to fill the rest of my fields.
    def fill_fields(self):
        # fill corners of bounding rect.
        corners = cv2.boxPoints(self.min_rect)
        self.corners = perspective.order_points(corners)
        # get the bounding rectangle.
        self.bounding_rect = cv2.boundingRect(self.contour)
        # fill length, height, and area of contour.
        self.length = self.min_rect[1][0]
        self.height = self.min_rect[1][1]
        self.area = cv2.contourArea(self.contour)
        # get all points of the contour.
        mask = np.zeros((self.my_image.image.shape[0],self.my_image.image.shape[1]),np.uint8)
        cv2.drawContours(mask,[self.contour],0,255,-1)
        self.allPointsOfContour = cv2.findNonZero(mask)
        # get the midpoint, and the top, bottom, left, and rightmost points of the contour.
        self.midpoint = (self.min_rect[1][0]+(self.min_rect[0][0]/2), self.min_rect[0][1]+(self.min_rect[1][1]/2)) # midpoint of the minimum bounding rectangle. 
        self.position = (self.bounding_rect[0]+(self.bounding_rect[2]/2), self.bounding_rect[1]+(self.bounding_rect[3]/2)) # midpoint of bounding rectangle. 
        self.leftmost = tuple(self.contour[self.contour[:,:,0].argmin()][0])
        self.rightmost = tuple(self.contour[self.contour[:,:,0].argmax()][0])
        self.topmost = tuple(self.contour[self.contour[:,:,1].argmin()][0])
        self.bottommost = tuple(self.contour[self.contour[:,:,1].argmax()][0])

# class to hold pairs of objects to calculate projections (lines) from points on the reference object to points on other objects (e.g., corner ot corner, or midpoint to midpoint).
class pairs(object):
    def __init__(self, object1, object2):
        self.object1 = object1
        self.object2 = object2

# funciton to find the objects in an image using contours and watershedding. It takes as input the name of the file of the image, and returns an array of the limited bounding rectangle of all detected objects.
def find_objs(image_name): 
    # load the image as color (for later use with watershed() funciton), and convert to grayscale.
    image = cv2.imread(image_name,1)
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    #cv2.imshow("Input", image)
    #cv2.waitKey(0)    
    ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    # noise removal.
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
    # sure background area.
    sure_bg = cv2.dilate(opening,kernel,iterations=3)
    # Finding sure foreground area.
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform,0.1*dist_transform.max(),255,0)
    # Finding unknown region.
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)
    # Marker labelling.
    ret, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure background is not 0, but 1. Do so so that you can set the unknown regions to 0 for watersheding.
    markers = markers+1
    # Now, mark the region of unknown with zero.
    markers[unknown==255] = 0
    # apply watershed.
    markers2 = cv2.watershed(image,markers)
    # find the contours of each of the individual shapes. 
    # first, find out how many individual shapes you have (you can do this by looking at how many unique values there are in the markers2 matrix, minus 2 (element encode borders (-1), the other background (1)).
    unique_values = np.unique(markers2)
    # second, create a masked image for each figure that only includes that figure (i.e., create a copy of markers2, and set all values that don't code for a specific individual element (e.g., '2'), to background(=1)). Put all the masked images into a single array. 
    masked_images = []
    for value in unique_values:
        # create a copy of the thresholded image, set all values that code background in item to grey-scale black (0). Skip any values lower than 1 (the value you set the background to).
        if value > 1:
            thresh_image_copy = thresh.copy()
            thresh_image_copy[markers2 != value] = 0
            masked_images.append(thresh_image_copy)
    # third, get the minimum bounding rectangle for the element element in each of the masked images. Put those bounding rectangles into an array. 
    image_objects = []
    for item in masked_images:
        # get the minimum bounding rectagle for the object in that image.
        _, contours, _ = cv2.findContours(item,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        rect = cv2.minAreaRect(contours[0])
        object1 = [contours[0], rect]
        image_objects.append(object1)
    
    # done.
    return image_objects

# draw the borders on the original figure.
# image[markers2 == -1] = [0,255,0]
# cv2.imshow("fixed?", image)
# cv2.waitKey(0)

# function to take in an image, identify objects via edges, and create visual objects from each bounded edge. 
def get_vis_objs(image):
    image_objects = find_objs(image)
    image = cv2.imread(image,1)
    items = []
    # create the the_image object. 
    my_image = the_image(image)
    # put all the objects (as vis_obj objects) into the image object.
    for item in image_objects:
        vis_obj_current = vis_obj(item[0], item[1], my_image)
        items.append(vis_obj_current)
    # for each object in the image, fill in the fields.
    for item in items:
        item.fill_fields()
    # return the array of visual objects. 
    return items

# function to round to nearest x place.
def roundX(number, x):
    value = math.ceil(number/float(x)) * x
    return int(value)

# function to create DORA objects from the visual objects. The DORA objects have as features, ... 
prototype={'name': 'non_exist', 'RBs': [{'pred_name': 'non_exist', 'pred_sem': [], 'higher_order': False, 'object_name': 'obj', 'object_sem': [], 'P': 'non_exist'}], 'set': 'memory', 'analog': None, 'contour': None}
def make_DORA_objs(items):
    # for each item, make a DORA object with features ... 
    objs = []
    analog_counter = 0
    for item in items:
        # create a sym object for each visual object in item, and put all objects from the same image in the same analog.
        for vis_obj in item:
            # create a copy of the sym_file object prototype.
            new_sym_dict = copy.deepcopy(prototype)
            # fill in the analog for the object. 
            new_sym_dict['analog'] = analog_counter
            # create a name for the object.
            new_sym_dict['RBs'][0]['object_name'] = 'obj'+str(len(objs))+str(random.random())
            # add the x and y extent semantics to the semantic list.
            new_sym_dict['RBs'][0]['object_sem'].append(['x', 1, 'x', 'nil', 'state'])
            new_sym_dict['RBs'][0]['object_sem'].append(['x'+str(roundX(vis_obj.position[0], 10)), 1, 'x', roundX(vis_obj.position[0],10), 'value'])
            new_sym_dict['RBs'][0]['object_sem'].append(['y', 1, 'y', 'nil', 'state'])
            new_sym_dict['RBs'][0]['object_sem'].append(['y'+str(roundX(vis_obj.position[1], 10)), 1, 'y', roundX(vis_obj.position[1], 10), 'value'])
            new_sym_dict['RBs'][0]['object_sem'].append(['x_ext', 1, 'x_ext', 'nil', 'state'])
            new_sym_dict['RBs'][0]['object_sem'].append(['x_ext'+str(roundX(vis_obj.length, 10)), 1, 'x_ext', roundX(vis_obj.length, 10), 'value'])
            new_sym_dict['RBs'][0]['object_sem'].append(['y_ext', 1, 'y_ext', 'nil', 'state'])
            new_sym_dict['RBs'][0]['object_sem'].append(['y_ext'+str(roundX(vis_obj.height, 10)), 1, 'y_ext', roundX(vis_obj.height, 10), 'value'])
            new_sym_dict['RBs'][0]['object_sem'].append(['total_ext', 1, 'total_ext', 'nil', 'state'])
            new_sym_dict['RBs'][0]['object_sem'].append(['total_ext'+str(roundX(vis_obj.area, 10)), 1, 'total_ext', roundX(vis_obj.area, 10), 'value'])
            # add the contour to the sym object dictionary.
            #new_sym_dict['contour'] = vis_obj.contour
            # add the new sym object to objs. 
            objs.append(new_sym_dict)
        # update analog_counter
        analog_counter+=1
    # return list of DORA objects with features. 
    return objs


#########################################################################################
# MAIN BODY. 
#########################################################################################

# make a list of all the pictures you want to procoess. For this project, it's a bunch of images called 'shapesn.jpb', where n is a number starting from 1 and going to the number of images to be processed. 
num_pics = 100
image_list = []
for i in range(num_pics):
    img_name = 'shapes'+str(i+1)+'.jpg'
    image_list.append(img_name)

# for every picture in image_list, create vis_objs of objects in the image, and put them in a list. Add the list of vis_objs to a master list of all lists of objects from all images, master_list. 
master_list = []
for pic in image_list:
    items = get_vis_objs(pic)
    master_list.append(items)

# create DORA objects for all objects in the master_list. 
objs = make_DORA_objs(master_list)

# now write all the sym_objs to a file.
write_file = open('new_sym_file.py', 'w')
write_file.write('simType=\'sim_file\' \nsymProps = ' + str(objs))

#pdb.set_trace()

