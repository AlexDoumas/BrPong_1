# DORA_GUI.py

# Are you being run on an iPhone?
run_on_iphone = False

# imports.
import dataTypes
import basicRunDORA
if not run_on_iphone:
    import pygame, os, sys
    from pygame.locals import *
import pdb

# Define colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255,255,50)
ORANGE = (255,100,0)
BLUE = (50,150,255)
GRAY = (150,150,150)

# What am I looking for the code to do? Let's start simple: Define a rectangle for each unit with a label for name and maybe a bar for activation.

# Initialize pygame screen size to 1200x800.
#screen_width = 1200.0
#screen_height = 800.0

# Initialize pygame fonts.
if not run_on_iphone:
    pygame.font.init()
    symfont = pygame.font.SysFont('times', 10)
    clock = pygame.time.Clock()

##############################################################
# THINK ABOUT HOW TO KEEP TRACK OF WHERE TO DRAW NEW NODES. MAYBE GUI_Nodes SHOULD BE AN OBJECT WITH FIELDS INDICATING WHERE LAST DRIVER P, LAST RECIPIENT RB, ETC. WERE DRAWN SO THAT NEXT NODE WILL BE DRAWN IN THE RIGHTSPOT. 
# OR SHOULD GUI_Nodes HAVE FIELDS FOR DRIVER, RECIPIENT, NEWSET WITH P, RB, AND PO FOR EACH? THAT WAY THE LAST NODE IN DRIVER.RB IS WHERE THE LAST RB IN DRIVER SET WAS DRAWN.
##############################################################

# pythonDORA GUI code.
class Node(object):
    def __init__(self, mynode, width, height, x_location, y_location):
        self.mynode = mynode
        self.name = mynode.name
        self.type = mynode.my_type
        self.act = 0.0
        self.rect = (x_location, y_location, width, height) # where I will be drawn on the screen.
        self.text_rect = (x_location, y_location, width, self.rect[3]/3) # where my text is drawn.
        # different act_rect for tokens and semantics.
        if self.type == 'semantic':
            self.act_rect = (x_location+(width/2), y_location, 0.0, self.rect[3]/1.05 )
        else:
            self.act_rect = (x_location+2, y_location+(self.rect[3]/2), self.act*self.rect[2], self.rect[3]/3) # where my activaiton bar is drawn
        # for my act and border colors, determine by my type.
        if self.type == 'P':
            self.act_color = GREEN # the color of my activation bar
            self.border_color = WHITE # the color of my border.
        elif self.type == 'RB':
            self.act_color = BLUE # the color of my activation bar
            self.border_color = WHITE # the color of my border.
        elif self.type == 'PO':
            self.act_color = RED # the color of my activation bar
            self.border_color = WHITE # the color of my border.
        elif self.type == 'semantic':
            self.act_color = YELLOW # the color of my activation bar
            self.border_color = WHITE # the color of my border.
    
    def update_act(self,memory):
        self.act = self.mynode.act*self.rect[2]

# a class to house all the nodes and GUI information for drawing.
# noinspection PyPep8Naming
class GUI_information_class(object):
    def __init__(self):
        self.GUI_Nodes = [] # empty now, but where all Node information will be.
        self.last_driver_group = None
        self.last_driver_P = None
        self.last_driver_RB = None
        self.last_driver_PO = None
        self.last_recipient_group = None
        self.last_recipient_P = None
        self.last_recipient_RB = None
        self.last_recipient_PO = None
        self.last_newSet_group = None
        self.last_newSet_P = None
        self.last_newSet_RB = None
        self.last_newSet_PO = None

# function to make a basic screen.
def make_screen(screen_width, screen_height):
    screen = pygame.display.set_mode((screen_width, screen_height))
    # NOTE: in updated pygame you need to reset the screen to black manually as status of old screen will be held over (i.e., whatever the state of the old screen variable will persist on the new screen, so old drawings on the screen will remain up and you'll just draw over them). 
    screen.fill(BLACK)
    return screen

# function to create the raw template screen.
def setup_screen(screen, screen_width, screen_height):
    # partition screen up into 4 quadrants (one each for driver, recipient, semantics, and newSet).
    driver_rect = (0,0, ((3*screen_width)/4), screen_height/3)
    recipient_rect = (0, screen_height/3, ((3*screen_width)/4), screen_height/3)
    new_rect = (0, ((2*screen_height)/3), ((3*screen_width)/4), screen_height/3)
    semantics_rect = (((3*screen_width)/4), 0, screen_width/4, screen_height)
    pygame.draw.rect(screen, WHITE, driver_rect, 4)
    pygame.draw.rect(screen, WHITE, recipient_rect, 4)
    pygame.draw.rect(screen, WHITE, new_rect, 4)
    pygame.draw.rect(screen, WHITE, semantics_rect, 4)
    # divide driver, recipient, and new quadrants into 4 rows (one for the quadrant label/groups, one for Ps, one for RBs, and one for POs) and one for label/groups (NOTE that the label row is large so that it can be appropriated for groups or other units later -- THANKS PAST ME!!!!!).
    quadrant_width = (3*screen_width)/4
    quadrant_height = screen_height/3
    unit_quadrant_width = quadrant_width
    unit_quadrant_height = quadrant_height/4
    driver_name_rect = (0,0,quadrant_width, quadrant_height/4)
    driver_Ps_rect = (0,unit_quadrant_height,quadrant_width, quadrant_height/4)
    driver_RBs_rect = (0,2*unit_quadrant_height,quadrant_width, quadrant_height/4)
    driver_POs_rect = (0,3*unit_quadrant_height,quadrant_width, quadrant_height/4)
    recipient_name_rect = (0,4*unit_quadrant_height,quadrant_width, quadrant_height/4)
    recipient_Ps_rect = (0,5*unit_quadrant_height,quadrant_width, quadrant_height/4)
    recipient_RBs_rect = (0,6*unit_quadrant_height,quadrant_width, quadrant_height/4)
    recipient_POs_rect = (0,7*unit_quadrant_height,quadrant_width, quadrant_height/4)
    new_name_rect = (0,2*quadrant_height,quadrant_width, quadrant_height/4)
    new_Ps_rect = (0,((2*quadrant_height)+(quadrant_height/4)),quadrant_width, quadrant_height/4)
    new_RBs_rect = (0,((2*quadrant_height)+((2*quadrant_height)/4)),quadrant_width, quadrant_height/4)
    new_POs_rect = (0,((2*quadrant_height)+((3*quadrant_height)/4)),quadrant_width, quadrant_height/4)
    pygame.draw.rect(screen, WHITE, driver_name_rect, 1)
    pygame.draw.rect(screen, WHITE, driver_Ps_rect, 1)
    pygame.draw.rect(screen, WHITE, driver_RBs_rect, 1)
    pygame.draw.rect(screen, WHITE, driver_POs_rect, 1)
    pygame.draw.rect(screen, WHITE, recipient_name_rect, 1)
    pygame.draw.rect(screen, WHITE, recipient_Ps_rect, 1)
    pygame.draw.rect(screen, WHITE, recipient_RBs_rect, 1)
    pygame.draw.rect(screen, WHITE, recipient_POs_rect, 1)
    pygame.draw.rect(screen, WHITE, new_name_rect, 1)
    pygame.draw.rect(screen, WHITE, new_Ps_rect, 1)
    pygame.draw.rect(screen, WHITE, new_RBs_rect, 1)
    pygame.draw.rect(screen, WHITE, new_POs_rect, 1)
    # update the screen.
    pygame.display.update()
    # done.
    # return the screen and the GUI_Nodes array.
    return screen

# create all the driver, recipient, newSet, and semantic nodes for the GUI.
def make_GUI_information(screen_width, screen_height, memory):
    # initialize measures.
    quadrant_width = (3*screen_width)/4
    quadrant_height = screen_height/3
    unit_quadrant_width = quadrant_width
    unit_quadrant_height = quadrant_height/4
    driver_groups_rect = (0,0,quadrant_width, quadrant_height/4)
    driver_Ps_rect = (0,unit_quadrant_height,quadrant_width, quadrant_height/4)
    driver_RBs_rect = (0,2*unit_quadrant_height,quadrant_width, quadrant_height/4)
    driver_POs_rect = (0,3*unit_quadrant_height,quadrant_width, quadrant_height/4)
    recipient_groups_rect = (0,4*unit_quadrant_height,quadrant_width, quadrant_height/4)
    recipient_Ps_rect = (0,5*unit_quadrant_height,quadrant_width, quadrant_height/4)
    recipient_RBs_rect = (0,6*unit_quadrant_height,quadrant_width, quadrant_height/4)
    recipient_POs_rect = (0,7*unit_quadrant_height,quadrant_width, quadrant_height/4)
    new_groups_rect = (0,2*quadrant_height,quadrant_width, quadrant_height/4)
    new_Ps_rect = (0,((2*quadrant_height)+(quadrant_height/4)),quadrant_width, quadrant_height/4)
    new_RBs_rect = (0,((2*quadrant_height)+((2*quadrant_height)/4)),quadrant_width, quadrant_height/4)
    new_POs_rect = (0,((2*quadrant_height)+((3*quadrant_height)/4)),quadrant_width, quadrant_height/4)
    # put all the nodes in a long array called GUI_Nodes.
    # initialize GUI_information.
    GUI_information = GUI_information_class()
    # iterate through all units in driver, recipient, semantics, and newSet, and create a Node for each unit.
    for group in memory.driver.Groups:
        # figure out the width and origin location (x_ and y_location).
        # the width should be default 1/10th of quadrant_width, unless there are more than 10 P units, in which case it should be quadrant_width/num_Groups.
        if len(memory.driver.Groups) <= 10:
            width = quadrant_width/10
        else:
            width = quadrant_width/len(memory.driver.Groups)
        # location depends on how many Groups you've already made. The first group starts at (0,driver_groups_rect[2]), the second group at (width, driver_groups_rect[2]), and so forth.
        x_location = width*memory.driver.Groups.index(group)
        y_location = driver_groups_rect[1]
        new_Node = Node(group, width, screen_height/12, x_location, y_location)
        # now update group's .GUI_unit field (i.e., keep a record of the GUI element it corresponds to) and add the new_Node to GUI_Nodes.
        group.GUI_unit = new_Node
        GUI_information.GUI_Nodes.append(new_Node)
        # and update the .last_driver_group field.
        GUI_information.last_driver_group = new_Node
    for myP in memory.driver.Ps:
        # figure out the width and origin location (x_ and y_location).
        # the width should be default 1/10th of quadrant_width, unless there are more than 10 P units, in which case it should be quadrant_width/num_Ps.
        if len(memory.driver.Ps) <= 10:
            width = quadrant_width/10
        else:
            width = quadrant_width/len(memory.driver.Ps)
        # location depends on how many Ps you've already made. The first P starts at (0,driver_Ps_rect[2]), the second P at (width, driver_Ps_rect[2]), and so forth.
        x_location = width*memory.driver.Ps.index(myP)
        y_location = driver_Ps_rect[1]
        new_Node = Node(myP, width, screen_height/12, x_location, y_location)
        # now update P's .GUI_unit field (i.e., keep a record of the GUI element it corresponds to) and add the new_Node to GUI_Nodes.
        myP.GUI_unit = new_Node
        GUI_information.GUI_Nodes.append(new_Node)
        # and update the .last_driver_P field.
        GUI_information.last_driver_P = new_Node
    for myRB in memory.driver.RBs:
        # figure out the width and origin location (x_ and y_location).
        # the width should be default 1/10th of quadrant_width, unless there are more than 10 RB units, in which case it should be quadrant_width/num_RBs.
        if len(memory.driver.RBs) <= 10:
            width = quadrant_width/10
        else:
            width = quadrant_width/len(memory.driver.RBs)
        # location depends on how many Ps you've already made. The first P starts at (0,driver_Ps_rect[2]), the second P at (width, driver_Ps_rect[2]), and so forth.
        x_location = width*memory.driver.RBs.index(myRB)
        y_location = driver_RBs_rect[1]
        new_Node = Node(myRB, width, screen_height/12, x_location, y_location)
        # now update PO's .GUI_unit field (i.e., keep a record of the GUI element it corresponds to) and add the new_Node to GUI_Nodes.
        myRB.GUI_unit = new_Node
        GUI_information.GUI_Nodes.append(new_Node)
        # and update the .last_driver_RB field.
        GUI_information.last_driver_RB = new_Node
    for myPO in memory.driver.POs:
        # figure out the width and origin location (x_ and y_location).
        # the width should be default 1/10th of quadrant_width, unless there are more than 10 PO units, in which case it should be quadrant_width/num_POs.
        if len(memory.driver.POs) <= 10:
            width = quadrant_width/10
        else:
            width = quadrant_width/len(memory.driver.POs)
        # location depends on how many Ps you've already made. The first P starts at (0,driver_Ps_rect[2]), the second P at (width, driver_Ps_rect[2]), and so forth.
        x_location = width*memory.driver.POs.index(myPO)
        y_location = driver_POs_rect[1]
        new_Node = Node(myPO, width, screen_height/12, x_location, y_location)
        # now update PO's .GUI_unit field (i.e., keep a record of the GUI element it corresponds to) and add the new_Node to GUI_Nodes.
        myPO.GUI_unit = new_Node
        GUI_information.GUI_Nodes.append(new_Node)
        # and update the .last_driver_PO field.
        GUI_information.last_driver_PO = new_Node
    for group in memory.recipient.Groups:
        # figure out the width and origin location (x_ and y_location).
        # the width should be default 1/10th of quadrant_width, unless there are more than 10 P units, in which case it should be quadrant_width/num_Groups.
        if len(memory.recipient.Groups) <= 10:
            width = quadrant_width/10
        else:
            width = quadrant_width/len(memory.recipient.Groups)
        # location depends on how many Groups you've already made. The first group starts at (0,driver_groups_rect[2]), the second group at (width, driver_groups_rect[2]), and so forth.
        x_location = width*memory.recipient.Groups.index(group)
        y_location = recipient_groups_rect[1]
        new_Node = Node(group, width, screen_height/12, x_location, y_location)
        # now update group's .GUI_unit field (i.e., keep a record of the GUI element it corresponds to) and add the new_Node to GUI_Nodes.
        group.GUI_unit = new_Node
        GUI_information.GUI_Nodes.append(new_Node)
        # and update the .last_driver_group field.
        GUI_information.last_recipient_group = new_Node
    for myP in memory.recipient.Ps:
        # figure out the width and origin location (x_ and y_location).
        # the width should be default 1/10th of quadrant_width, unless there are more than 10 P units, in which case it should be quadrant_width/num_Ps.
        if len(memory.recipient.Ps) <= 10:
            width = quadrant_width/10
        else:
            width = quadrant_width/len(memory.recipient.Ps)
        # location depends on how many Ps you've already made. The first P starts at (0,driver_Ps_rect[2]), the second P at (width, driver_Ps_rect[2]), and so forth.
        x_location = width*memory.recipient.Ps.index(myP)
        y_location = recipient_Ps_rect[1]
        new_Node = Node(myP, width, screen_height/12, x_location, y_location)
        # now update P's .GUI_unit field (i.e., keep a record of the GUI element it corresponds to) and add the new_Node to GUI_Nodes.
        myP.GUI_unit = new_Node
        GUI_information.GUI_Nodes.append(new_Node)
        # and update the .last_recipient_P field.
        GUI_information.last_recipient_P = new_Node
    for myRB in memory.recipient.RBs:
        # figure out the width and origin location (x_ and y_location).
        # the width should be default 1/10th of quadrant_width, unless there are more than 10 RB units, in which case it should be quadrant_width/num_RBs.
        if len(memory.recipient.RBs) <= 10:
            width = quadrant_width/10
        else:
            width = quadrant_width/len(memory.recipient.RBs)
        # location depends on how many Ps you've already made. The first RB starts at (0,driver_RBs_rect[2]), the second P at (width, driver_Ps_rect[2]), and so forth.
        x_location = width*memory.recipient.RBs.index(myRB)
        y_location = recipient_RBs_rect[1]
        new_Node = Node(myRB, width, screen_height/12, x_location, y_location)
        # now update RB's .GUI_unit field (i.e., keep a record of the GUI element it corresponds to) and add the new_Node to GUI_Nodes.
        myRB.GUI_unit = new_Node
        GUI_information.GUI_Nodes.append(new_Node)
        # and update the .last_recipient_RB field.
        GUI_information.last_recipient_RB = new_Node
    for myPO in memory.recipient.POs:
        # figure out the width and origin location (x_ and y_location).
        # the width should be default 1/10th of quadrant_width, unless there are more than 10 PO units, in which case it should be quadrant_width/num_POs.
        if len(memory.recipient.POs) <= 10:
            width = quadrant_width/10
        else:
            width = quadrant_width/len(memory.recipient.POs)
        # location depends on how many Ps you've already made. The first PO starts at (0,driver_POs_rect[2]), the second P at (width, driver_Ps_rect[2]), and so forth.
        x_location = width*memory.recipient.POs.index(myPO)
        y_location = recipient_POs_rect[1]
        new_Node = Node(myPO, width, screen_height/12, x_location, y_location)
        # now update PO's .GUI_unit field (i.e., keep a record of the GUI element it corresponds to) and add the new_Node to GUI_Nodes.
        myPO.GUI_unit = new_Node
        GUI_information.GUI_Nodes.append(new_Node)
        # and update the .last_recipient_PO field.
        GUI_information.last_recipient_PO = new_Node
    # there is nothing in newSet now, so nothing to do yet.
    # NOTE: FOR THE SEMANTICS, YOU CAN ONLY DISPLAY THE FIRST 100.
    # semantics are displayed in 50 rows and 2 columns of units.
    semantic_counter = 0
    semantic_names = []
    # create all semantics in driver.
    for myPO in memory.driver.POs:
        for Link in myPO.mySemantics:
            # create a semantic Node for the semantic attached to Link if it has not already been made.
            if not (Link.mySemantic.name in semantic_names):
                # make a Node for this semantic.
                # width is 1/4 of screen_width / 2.
                width = (screen_width/4)/2
                # height is screen_height/50.
                height = screen_height/50
                # x_ and y_locations depend on how many semantics you've made.
                # if semantic_counter is even, then x_location is screen_width/4, otherwise, it is screen_width/4+width.
                if semantic_counter%2 == 0:
                    x_location = (3*screen_width)/4
                else:
                    x_location = ((3*screen_width)/4) + width
                # the y_location is 0 + ((semantic_counter/2) * height).
                y_location = ((semantic_counter/2) * height)
                # make the new Node.
                new_Node = Node(Link.mySemantic, width, height, x_location, y_location)
                # update Link.mySemantic's GUI_unit field (i.e., keep a record of the GUI element it corresponds to).
                Link.mySemantic.GUI_unit = new_Node
                # add the new_Node to GUI_Nodes
                GUI_information.GUI_Nodes.append(new_Node)
                # update semantic_counter.
                semantic_counter += 1
                # update semantic_names
                semantic_names.append(Link.mySemantic.name)
    # create all semantics in recipient.
    for myPO in memory.recipient.POs:
        for Link in myPO.mySemantics:
            # create a semantic Node for the semantic attached to Link if it has not already been made.
            if not (Link.mySemantic.name in semantic_names):
                # make a Node for this semantic.
                # width is 1/4 of screen_width / 2.
                width = (screen_width/4)/2
                # height is screen_height/50.
                height = screen_height/50
                # x_ and y_locations depend on how many semantics you've made.
                # if semantic_counter is even, then x_location is screen_width/4, otherwise, it is screen_width/4+width.
                if semantic_counter%2 == 0:
                    x_location = (3*screen_width)/4
                else:
                    x_location = ((3*screen_width)/4) + width
                # the y_location is 0 + ((semantic_counter/2) * height).
                y_location = ((semantic_counter/2) * height)
                # make the new Node.
                new_Node = Node(Link.mySemantic, width, height, x_location, y_location)
                # update Link.mySemantic's GUI_unit field (i.e., keep a record of the GUI element it corresponds to).
                Link.mySemantic.GUI_unit = new_Node
                # add the new_Node to GUI_Nodes
                GUI_information.GUI_Nodes.append(new_Node)
                # update semantic_counter.
                semantic_counter += 1
                # update semantic_names
                semantic_names.append(Link.mySemantic.name)
    # also add screen_width and screen_height to GUI_information.
    GUI_information.screen_width = screen_width
    GUI_information.screen_height = screen_height
    # done.
    # return GUI_information and memory.
    return GUI_information, memory

# draw the nodes to the screen for the first time (i.e., initialize Nodes to screen).
def initialize_screen_nodes(screen, GUI_information):
    # draw each Node in GUI_Nodes, including border, name, and activation.
    for Node in GUI_information.GUI_Nodes:
        # draw the border.
        pygame.draw.rect(screen, Node.border_color, Node.rect, 1)
        # position the name text.
        mytext = symfont.render(Node.name, True, WHITE, BLACK)
        mytextpos = Node.text_rect
        screen.blit(mytext, mytextpos)
        # draw the activation.
        if Node.act > 0:
            pygame.draw.rect(screen, Node.act_color, Node.act_rect, 0)
        #else:
            #1.05 pygame.draw.rect(screen, WHITE, Node.act_rect, 0)
    # update the screen.
    pygame.display.update()
    # done.
    return screen

# update the activation rectangles for each Node in GUI_Nodes.
def update_node_acts(screen, GUI_information):
    # update the activation rectangles for each Node in GUI_Nodes.
    for Node in GUI_information.GUI_Nodes:
        # update the Node's act.
        Node.act = Node.mynode.act
        # draw the rect for that nodes activation.
        # erase the current activation rect.
        if Node.type == 'semantic':
            pygame.draw.rect(screen, BLACK, (Node.act_rect[0], Node.act_rect[1], (Node.rect[2]/2)/1.05 , Node.act_rect[3]), 0)
        else:
            pygame.draw.rect(screen, BLACK, (Node.act_rect[0], Node.act_rect[1], Node.rect[2]/1.05 , Node.act_rect[3]/1.05 ), 0)
        if Node.act > 0:
            if Node.type == 'semantic':
                pygame.draw.rect(screen, Node.act_color, (Node.act_rect[0], Node.act_rect[1], (Node.act*Node.rect[2]/2)/1.05 , Node.act_rect[3]), 0)
            else:
                pygame.draw.rect(screen, Node.act_color, (Node.act_rect[0], Node.act_rect[1], Node.act*Node.rect[2]/1.05 , Node.act_rect[3]/1.05 ), 0)
    # update the screen.
    pygame.display.update()
    # done.
    return screen

# initialize GUI.
def initialize_GUI(screen_width, screen_height, memory):
    # draw a screen.
    screen = make_screen(screen_width, screen_height)
    screen = setup_screen(screen, screen_width, screen_height)
    GUI_information, memory = make_GUI_information(screen_width, screen_height, memory)
    screen = initialize_screen_nodes(screen, GUI_information)
    # done.
    return screen, GUI_information

# draw any newly inferred nodes in driver, recipient, or newSet.
# NOTE: Right now this function will just draw new nodes. If you exceed the size of the GUI, it won't notice.
def draw_new_GUI_Nodes(screen, GUI_information, memory, debug):
    # initial quadrants.
    quadrant_width = (3*GUI_information.screen_width)/4
    quadrant_height = GUI_information.screen_height/3
    unit_quadrant_width = quadrant_width
    unit_quadrant_height = quadrant_height/4
    recipient_Ps_rect = (0,5*unit_quadrant_height,quadrant_width, quadrant_height/4)
    recipient_RBs_rect = (0,6*unit_quadrant_height,quadrant_width, quadrant_height/4)
    recipient_POs_rect = (0,7*unit_quadrant_height,quadrant_width, quadrant_height/4)
    new_name_rect = (0,8*unit_quadrant_height,quadrant_width, quadrant_height/4)
    new_Ps_rect = (0,9*unit_quadrant_height,quadrant_width, quadrant_height/4)
    new_RBs_rect = (0,10*unit_quadrant_height,quadrant_width, quadrant_height/4)
    new_POs_rect = (0,11*unit_quadrant_height,quadrant_width, quadrant_height/4)
    # look for any new nodes and draw them. Add newly drawn nodes as the last_type in GUI_information.
    for myP in memory.driver.Ps:
        # if the unit has not GUI_unit, make one.
        if myP.GUI_unit is None:
            # the new P should be drawn next to the last P already drawn.
            # if the space for Ps is empty, start in the first available space.
            width = quadrant_width/10
            height = GUI_information.screen_height/12
            x_location = width*memory.driver.Ps.index(myP)
            y_location = recipient_Ps_rect[1]
            new_node = Node(myP, width, height, x_location, y_location)           
            # add new_node to myP.
            myP.GUI_unit = new_node
            # add the node to GUI_information.GUI_Nodes.
            GUI_information.GUI_Nodes.append(new_node)
            # draw the new_node.
            # draw the border.
            pygame.draw.rect(screen, new_node.border_color, new_node.rect, 1)
            # position the name text.
            mytext = symfont.render(new_node.name, True, WHITE, BLACK)
            mytextpos = new_node.text_rect
            screen.blit(mytext, mytextpos)
            # draw the activation.
            if new_node.act > 0:
                pygame.draw.rect(screen, new_node.act_color, new_node.act_rect, 0)
            else:
                pygame.draw.rect(screen, WHITE, new_node.act_rect, 0)
    for myRB in memory.driver.RBs:
        # if the unit has not GUI_unit, make one.
        if myRB.GUI_unit is None:
            # the new P should be drawn next to the last P already drawn.
            # if the space for RBs is empty, start in the first available space.
            width = quadrant_width/10
            height = GUI_information.screen_height/12
            x_location = width*memory.driver.RBs.index(myRB)
            y_location = recipient_RBs_rect[1]
            new_node = Node(myRB, width, height, x_location, y_location)
            # add new_node to myRB.
            myRB.GUI_unit = new_node
            # add the node to GUI_information.GUI_Nodes.
            GUI_information.GUI_Nodes.append(new_node)
            # draw the new_node.
            # draw the border.
            pygame.draw.rect(screen, new_node.border_color, new_node.rect, 1)
            # position the name text.
            mytext = symfont.render(new_node.name, True, WHITE, BLACK)
            mytextpos = new_node.text_rect
            screen.blit(mytext, mytextpos)
            # draw the activation.
            if new_node.act > 0:
                pygame.draw.rect(screen, new_node.act_color, new_node.act_rect, 0)
            else:
                pygame.draw.rect(screen, WHITE, new_node.act_rect, 0)
    for myPO in memory.driver.POs:
        # if the unit has not GUI_unit, make one.
        # Alternately, if the number of POs is beyond the range displayable in the current GUI, erase and re-display the entire row of PO units.
        if myPO.GUI_unit is None:
            # the new P should be drawn next to the last P already drawn.
            # if the space for POs is empty, start in the first available space.
            width = quadrant_width/10
            height = GUI_information.screen_height/12
            x_location = width*memory.driver.POs.index(myPO)
            y_location = recipient_POs_rect[1]
            new_node = Node(myPO, width, height, x_location, y_location)
            # add new_node to myPO.
            myPO.GUI_unit = new_node
            # add the node to GUI_information.GUI_Nodes.
            GUI_information.GUI_Nodes.append(new_node)
            # draw the new_node.
            # draw the border.
            pygame.draw.rect(screen, new_node.border_color, new_node.rect, 1)
            # position the name text.
            mytext = symfont.render(new_node.name, True, WHITE, BLACK)
            mytextpos = new_node.text_rect
            screen.blit(mytext, mytextpos)
            # draw the activation.
            if new_node.act > 0:
                pygame.draw.rect(screen, new_node.act_color, new_node.act_rect, 0)
            else:
                pygame.draw.rect(screen, WHITE, new_node.act_rect, 0)
    for myP in memory.recipient.Ps:
        # if the unit has no GUI_unit, make one.
        if myP.GUI_unit is None:
            # the new P should be drawn next to the last P already drawn.
            # if the space for Ps is empty, start in the first available space.
            width = quadrant_width/10
            height = GUI_information.screen_height/12
            x_location = width*memory.recipient.Ps.index(myP)
            y_location = recipient_Ps_rect[1]
            new_node = Node(myP, width, height, x_location, y_location)
            # add new_node to myP.
            myP.GUI_unit = new_node
            # add the node to GUI_information.GUI_Nodes.
            GUI_information.GUI_Nodes.append(new_node)
            # draw the new_node.
            # draw the border.
            pygame.draw.rect(screen, new_node.border_color, new_node.rect, 1)
            # position the name text.
            mytext = symfont.render(new_node.name, True, WHITE, BLACK)
            mytextpos = new_node.text_rect
            screen.blit(mytext, mytextpos)
            # draw the activation.
            if new_node.act > 0:
                pygame.draw.rect(screen, new_node.act_color, new_node.act_rect, 0)
            else:
                pygame.draw.rect(screen, WHITE, new_node.act_rect, 0)
    for myRB in memory.recipient.RBs:
        # if the unit has no GUI_unit, make one.
        if myRB.GUI_unit is None:
            # the new RB should be drawn next to the last RB already drawn.
            # if the space for RBs is empty, start in the first available space.
            width = quadrant_width/10
            height = GUI_information.screen_height/12
            x_location = width*memory.recipient.RBs.index(myRB)
            y_location = recipient_RBs_rect[1]
            new_node = Node(myRB, width, height, x_location, y_location)
            # add new_node to myRB.
            myRB.GUI_unit = new_node
            # add the node to GUI_information.GUI_Nodes.
            GUI_information.GUI_Nodes.append(new_node)
            # draw the new_node.
            # draw the border.
            pygame.draw.rect(screen, new_node.border_color, new_node.rect, 1)
            # position the name text.
            mytext = symfont.render(new_node.name, True, WHITE, BLACK)
            mytextpos = new_node.text_rect
            screen.blit(mytext, mytextpos)
            # draw the activation.
            if new_node.act > 0:
                pygame.draw.rect(screen, new_node.act_color, new_node.act_rect, 0)
            else:
                pygame.draw.rect(screen, WHITE, new_node.act_rect, 0)
    for myPO in memory.recipient.POs:
        # if the unit has no GUI_unit, make one.
        if myPO.GUI_unit is None:
            # the new PO should be drawn next to the last PO already drawn.
            # if the space for POs is empty, start in the first available space.
            width = quadrant_width/10
            height = GUI_information.screen_height/12
            x_location = width*memory.recipient.POs.index(myPO)
            y_location = recipient_POs_rect[1]
            new_node = Node(myPO, width, height, x_location, y_location)      
            # add new_node to myPO.
            myPO.GUI_unit = new_node
            # add the node to GUI_information.GUI_Nodes.
            GUI_information.GUI_Nodes.append(new_node)
            # draw the new_node.
            # draw the border.
            pygame.draw.rect(screen, new_node.border_color, new_node.rect, 1)
            # position the name text.
            mytext = symfont.render(new_node.name, True, WHITE, BLACK)
            mytextpos = new_node.text_rect
            screen.blit(mytext, mytextpos)
            # draw the activation.
            if new_node.act > 0:
                pygame.draw.rect(screen, new_node.act_color, new_node.act_rect, 0)
            else:
                pygame.draw.rect(screen, WHITE, new_node.act_rect, 0)
    for myP in memory.newSet.Ps:
        # if the unit has not GUI_unit, make one.
        if myP.GUI_unit is None:
            # the new P should be drawn next to the last P already drawn.
            # if the newSet is empty, start in the first newSet space.
            width = quadrant_width/10
            height = GUI_information.screen_height/12
            x_location = width*memory.newSet.Ps.index(myP)
            y_location = new_Ps_rect[1]
            new_node = Node(myP, width, height, x_location, y_location)
            # add new_node to myP.
            myP.GUI_unit = new_node
            # add the node to GUI_information.GUI_Nodes.
            GUI_information.GUI_Nodes.append(new_node)
            # draw the new_node.
            # draw the border.
            pygame.draw.rect(screen, new_node.border_color, new_node.rect, 1)
            # position the name text.
            mytext = symfont.render(new_node.name, True, WHITE, BLACK)
            mytextpos = new_node.text_rect
            screen.blit(mytext, mytextpos)
            # draw the activation.
            if new_node.act > 0:
                pygame.draw.rect(screen, new_node.act_color, new_node.act_rect, 0)
            else:
                pygame.draw.rect(screen, WHITE, new_node.act_rect, 0)
    for myRB in memory.newSet.RBs:
        # if the unit has not GUI_unit, make one.
        if myRB.GUI_unit is None:
            # if the newSet is empty, start in the first newSet space.
            width = quadrant_width/10
            height = GUI_information.screen_height/12
            x_location = width*memory.newSet.RBs.index(myRB)
            y_location = new_RBs_rect[1]
            new_node = Node(myRB, width, height, x_location, y_location)
            # add new_node to myRB.
            myRB.GUI_unit = new_node
            # add the node to GUI_information.GUI_Nodes.
            GUI_information.GUI_Nodes.append(new_node)
            # draw the new_node.
            # draw the border.
            pygame.draw.rect(screen, new_node.border_color, new_node.rect, 1)
            # position the name text.
            mytext = symfont.render(new_node.name, True, WHITE, BLACK)
            mytextpos = new_node.text_rect
            screen.blit(mytext, mytextpos)
            # draw the activation.
            if new_node.act > 0:
                pygame.draw.rect(screen, new_node.act_color, new_node.act_rect, 0)
            else:
                pygame.draw.rect(screen, WHITE, new_node.act_rect, 0)
    for myPO in memory.newSet.POs:
        # if the unit has not GUI_unit, make one.
        if myPO.GUI_unit is None:
            # if the newSet is empty, start in the first newSet space.
            width = quadrant_width/10
            height = GUI_information.screen_height/12
            x_location = width*memory.newSet.POs.index(myPO)
            y_location = new_POs_rect[1]
            new_node = Node(myPO, width, height, x_location, y_location)
            # add new_node to myPO.
            myPO.GUI_unit = new_node
            # add the node to GUI_information.GUI_Nodes.
            GUI_information.GUI_Nodes.append(new_node)
            # draw the new_node.
            # draw the border.
            pygame.draw.rect(screen, new_node.border_color, new_node.rect, 1)
            # position the name text.
            mytext = symfont.render(new_node.name, True, WHITE, BLACK)
            mytextpos = new_node.text_rect
            screen.blit(mytext, mytextpos)
            # draw the activation.
            if new_node.act > 0:
                pygame.draw.rect(screen, new_node.act_color, new_node.act_rect, 0)
            else:
                pygame.draw.rect(screen, WHITE, new_node.act_rect, 0)
    # done.
    return GUI_information, memory

# run the GUI (update the activation of all nodes in the screen).
def run_GUI(screen, GUI_information, memory, debug):
    # each time GUI is called you want to update the screen with: (a) changes in activation of units algready on screen, and (b) create nodes for new units inferred in newSet, and draw them to the screen.
    # update activations of nodes.
    for node in GUI_information.GUI_Nodes:
        node.update_act(memory)
    # now draw the updated activations to the screen.
    screen = update_node_acts(screen, GUI_information)
    # draw any newly added nodes to recipient or to newSet.
    GUI_information, memory = draw_new_GUI_Nodes(screen, GUI_information, memory, debug)
    # update the screen.
    pygame.display.update()
    return screen, memory

# function that runs at the end of a DORA run and keeps the GUI window open until the user manually closes it.
# NOTE: I see this function as useful as an option before run, that will keep run window open until user manually quits the window.
def manually_close_window(screen):
    keep_going = True
    while keep_going:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            keep_going = False
            # close the window with pygame.display.quit().
            pygame.display.quit()

###################################################
############ GUIs FOR TERMINAL DISPLAY ############
###################################################
# super simple GUI: Display inputs and activations of driver and recipient units in the shell.
def simple_term_state_display(memory):
    # display driver state.
    print('DRVER STATE')
    print('GROUP units:')
    for group in memory.driver.Groups:
        printstring = str(group.name) + ': ACT=' + str(group.act) + ' and INPUT=' + str(group.net_input)
        print(printstring)
    print('P units:')
    for myP in memory.driver.Ps:
        printstring = str(myP.name) + ': ACT=' + str(myP.act) + ' and INPUT=' + str(myP.net_input)
        print(printstring)
    print('RB units:')
    for myRB in memory.driver.RBs:
        printstring = str(myRB.name) + ': ACT=' + str(myRB.act) + ' and INPUT=' + str(myRB.net_input)
        print(printstring)
    print('PO units:')
    for myPO in memory.driver.POs:
        printstring = str(myPO.name) + ': ACT=' + str(myPO.act) + ' and INPUT=' + str(myPO.net_input)
        print(printstring)
    print('')
    # display recipient state.
    print('RECIPIENT STATE')
    print('GROUP units:')
    for group in memory.recipient.Groups:
        printstring = str(group.name) + ': ACT=' + str(group.act) + ' and INPUT=' + str(group.net_input)
        print(printstring)
    print('P units:')
    for myP in memory.recipient.Ps:
        printstring = str(myP.name) + ': ACT=' + str(myP.act) + ' and INPUT=' + str(myP.net_input)
        print(printstring)
    print('RB units:')
    for myRB in memory.recipient.RBs:
        printstring = str(myRB.name) + ': ACT=' + str(myRB.act) + ' and INPUT=' + str(myRB.net_input)
        print(printstring)
    print('PO units:')
    for myPO in memory.recipient.POs:
        printstring = str(myPO.name) + ': ACT=' + str(myPO.act) + ' and INPUT=' + str(myPO.net_input)
        print(printstring)
    print('')

# super simple GUI II: display inputs and activations of all semantics in the shell.
def term_semantic_state_display(memory):
    print('SEMANTICS')
    for semantic in memory.semantics:
        printstrng = printstring = str(semantic.name) + ': ACT=' + str(semantic.act) + ' and INPUT=' + str(semantic.myinput)
        print(printstring)
    print('')

# simple GUI: Display inputs and activations of driver, recipient, AND MEMORY units in the shell.
def full_term_state_display(memory):
    # display driver state.
    print('DRVER STATE')
    print('GROUP units:')
    for group in memory.driver.Groups:
        printstring = str(group.name) + ': ACT=' + str(group.act) + ' and INPUT=' + str(group.net_input)
        print(printstring)
    print('P units:')
    for myP in memory.driver.Ps:
        printstring = str(myP.name) + ': ACT=' + str(myP.act) + ' and INPUT=' + str(myP.net_input)
        print(printstring)
    print('RB units:')
    for myRB in memory.driver.RBs:
        printstring = str(myRB.name) + ': ACT=' + str(myRB.act) + ' and INPUT=' + str(myRB.net_input)
        print(printstring)
    print('PO units:')
    for myPO in memory.driver.POs:
        printstring = str(myPO.name) + ': ACT=' + str(myPO.act) + ' and INPUT=' + str(myPO.net_input)
        print(printstring)
    print('')
    # display recipient state.
    print('RECIPIENT STATE')
    print('GROUP units:')
    for group in memory.recipient.Groups:
        printstring = str(group.name) + ': ACT=' + str(group.act) + ' and INPUT=' + str(group.net_input)
        print(printstring)
    print('P units:')
    for myP in memory.recipient.Ps:
        printstring = str(myP.name) + ': ACT=' + str(myP.act) + ' and INPUT=' + str(myP.net_input)
        print(printstring)
    print('RB units:')
    for myRB in memory.recipient.RBs:
        printstring = str(myRB.name) + ': ACT=' + str(myRB.act) + ' and INPUT=' + str(myRB.net_input)
        print(printstring)
    print('PO units:')
    for myPO in memory.recipient.POs:
        printstring = str(myPO.name) + ': ACT=' + str(myPO.act) + ' and INPUT=' + str(myPO.net_input)
        print(printstring)
    print('')
    # display memory state.
    # display all units neither in driver or recipient.
    print('MEMORY STATE')
    print('GROUP units:')
    for group in memory.Groups:
        printstring = str(group.name) + ': ACT=' + str(group.act) + ' and INPUT=' + str(group.net_input)
        print(printstring)
    print('P units:')
    for myP in memory.Ps:
        if myP.set != 'driver' and myP.set != 'recipient':
            printstring = str(myP.name) + ': ACT=' + str(myP.act) + ' and INPUT=' + str(myP.net_input)
            print(printstring)
    print('RB units:')
    for myRB in memory.RBs:
        if myRB.set != 'driver' and myRB.set != 'recipient':
            printstring = str(myRB.name) + ': ACT=' + str(myRB.act) + ' and INPUT=' + str(myRB.net_input)
            print(printstring)
    print('PO units:')
    for myPO in memory.POs:
        if myPO.set != 'driver' and myPO.set != 'recipient':
            printstring = str(myPO.name) + ': ACT=' + str(myPO.act) + ' and INPUT=' + str(myPO.net_input)
            print(printstring)
    print('')

# super simple GUI to display the structure of items in driver, recipient, or memory.
def term_network_display(memory, set_to_display):
    # this function takes as input the memory data, and a set_to_display string specifying, 'driver', 'recipient', or 'memory', and then prints the elements in that set to the screen and to a text file.
    # structure of a printed analog is myP.name /n myRB.name-PO_pred.name(PO.semantics)-PO_obj.name(PO.semantics), for each RB, for each analog topping out at a P unit, then myRB.name-PO_pred.name(PO.semantics)-PO_obj.name(PO>semantics), for each analog toppig out at a RB, then myPO.name(semantics), for each analog topping out with a PO unit.
    if set_to_display == 'driver':
        print('')
        print('DRIVER:')
        group_counter = 0
        for group in memory.driver.Groups:
            group_counter += 1
            # print my name and info for all my tokens.
            print('')
            term_display_group(group, group_counter)
        # now draw the Ps.
        P_counter = 0
        for myP in memory.driver.Ps:
            # you are starting the counter at 1 so that the 0th element in the Ps array lists starting from (1) (rather than 0; which I think is more readable for the user). 
            P_counter += 1
            # NOTE: you might eventually want code here to only print P units with no groups (which is added below, but commented out).
            #if len(myP.myGroups) < 1:
            #   # print my name, then info for each of my RBs.
            #   print ''
            #   term_display_P(myP, P_counter)
            # print my name, then info for each of my RBs.
            print('')
            term_display_P(myP, P_counter)
        # draw each RB that has no Ps above it.
        RB_counter = 0
        for myRB in memory.driver.RBs:
            # you are starting the counter at 1 so that the 0th element in the RBs array lists starting from (1) (rather than 0; which I think is more readable for the user). 
            RB_counter += 1
            # if that RB has no Ps above it (i.e., myRB.myParentPs is empty), then draw it.
            # NOTE: term_display_RB function takes care of not drawing RBs without P parents.
            term_display_RB(myRB, RB_counter)
        # for draw each PO that has no RBs.
        PO_counter = 0
        for myPO in memory.driver.POs:
            # you are starting the counter at 1 so that the 0th element in the POs array lists starting from (1) (rather than 0; which I think is more readable for the user). 
            PO_counter += 1
            # if that PO has no RBs (i.e., myPO.myRBs is empty), then draw it.
            # NOTE: term_display_PO function takes care of not drawing POs with no RBs.
            term_display_PO(myPO, PO_counter)
    elif set_to_display == 'recipient':
        print('')
        print('RECIPIENT:')
        group_counter = 0
        for group in memory.recipient.Groups:
            group_counter += 1
            # print my name and info for all my tokens.
            print('')
            term_display_group(group, group_counter)
        # now draw the Ps.
        P_counter = 0
        for myP in memory.recipient.Ps:
            # you are starting the counter at 1 so that the 0th element in the Ps array lists starting from (1) (rather than 0; which I think is more readable for the user). 
            P_counter += 1
            # NOTE: you might eventually want code here to only print P units with no groups (which is added below, but commented out).
            #if len(myP.myGroups) < 1:
            #   # print my name, then info for each of my RBs.
            #   print ''
            #   term_display_P(myP, P_counter)
            # print my name, then info for each of my RBs.
            print('')
            term_display_P(myP, P_counter)
        # draw each RB that has no Ps above it.
        RB_counter = 0
        for myRB in memory.recipient.RBs:
             # you are starting the counter at 1 so that the 0th element in the RBs array lists starting from (1) (rather than 0; which I think is more readable for the user). 
            RB_counter += 1
            # if that RB has no Ps above it (i.e., myRB.myParentPs is empty), then draw it.
            # NOTE: term_display_RB function takes care of not drawing RBs without P parents.
            term_display_RB(myRB, RB_counter)
        # for draw each PO that has no RBs.
        PO_counter = 0
        for myPO in memory.recipient.POs:
            # you are starting the counter at 1 so that the 0th element in the POs array lists starting from (1) (rather than 0; which I think is more readable for the user). 
            PO_counter += 1
            # if that PO has no RBs (i.e., myPO.myRBs is empty), then draw it.
            # NOTE: term_display_PO function takes care of not drawing POs with no RBs.
            term_display_PO(myPO, PO_counter)
    else:
        print('')
        print('MEMORY:')
        group_counter = 0
        for group in memory.Groups:
            group_counter += 1
            # print my name and info for all my tokens.
            print('')
            term_display_group(group, group_counter)
        # now draw the Ps.
        P_counter = 0
        for myP in memory.Ps:
            # you are starting the counter at 1 so that the 0th element in the Ps array lists starting from (1) (rather than 0; which I think is more readable for the user). 
            P_counter += 1
            # NOTE: you might eventually want code here to only print P units with no groups (which is added below, but commented out).
            #if len(myP.myGroups) < 1:
            #   # print my name, then info for each of my RBs.
            #   print ''
            #   term_display_P(myP, P_counter)
            # print my name, then info for each of my RBs.
            print('')
            term_display_P(myP, P_counter)
        # draw each RB that has no Ps above it.
        RB_counter = 0
        for myRB in memory.RBs:
            # you are starting the counter at 1 so that the 0th element in the RBs array lists starting from (1) (rather than 0; which I think is more readable for the user). 
            RB_counter += 1
            # if that RB has no Ps above it (i.e., myRB.myParentPs is empty), then draw it.
            # NOTE: term_display_RB function takes care of not drawing RBs without P parents.
            term_display_RB(myRB, RB_counter)
        # for draw each PO that has no RBs.
        PO_counter = 0
        for myPO in memory.POs:
            # you are starting the counter at 1 so that the 0th element in the POs array lists starting from (1) (rather than 0; which I think is more readable for the user). 
            PO_counter += 1
            # if that PO has no RBs (i.e., myPO.myRBs is empty), then draw it.
            # NOTE: term_display_PO function takes care of not drawing POs with no RBs.
            term_display_PO(myPO, PO_counter)

# function to display a group and all its tokens (for use with .term_network_display).
def term_display_group(group, counter):
    print(('group', counter, '. ', group.name))
    for group2 in group.myGroups:
        myindex = group2.myindex + 1
        term_display_group(group2, myindex)
    for myP in group.myPs:
        myindex = myP.myindex + 1
        term_display_P(myP, myindex)

# function to display a P and all its tokens (for use with .term_network_display).
def term_display_P(myP, counter):
    print(('P ', counter, '. ', myP.name))
    for myRB in myP.myRBs:
        RB_string = myRB.name + '-- Pred_name: ' + myRB.myPred[0].name + ' ('
        # organise the links by weight to disply from hight to low. 
        link_list = []
        for link in myRB.myPred[0].mySemantics:
            link_list.append([link.mySemantic.name, link.weight])
            link_list.sort(key=lambda x: x[1], reverse=True)
        for link in link_list:
            RB_string = RB_string + link[0] + '-' + str(link[1]) + ', '
        # now print the name of the object or child P serving as the argument of the myRB. Organise the links by weight to disply from hight to low. 
        link_list = []
        if len(myRB.myObj) > 0:
            RB_string = RB_string + ') -- Obj_name:' + myRB.myObj[0].name + ' ('
            link_list = []
            for link in myRB.myObj[0].mySemantics:
                link_list.append([link.mySemantic.name, link.weight])
                link_list.sort(key=lambda x: x[1], reverse=True)
            for link in link_list:
                RB_string = RB_string + link[0] + '-' + str(link[1]) + ', '
            RB_string += ')'
        elif len(myRB.myChildP) > 0:
            RB_string = RB_string + ') -- PROP_name:' + myRB.myChildP[0].name + ' '
        print(RB_string)

# function to display RB and all its tokens (for use with .term_network_display).
def term_display_RB(myRB, counter):
    if len(myRB.myParentPs) == 0:
        print('')
        RB_string = 'RB ' + str(counter) + '.' + myRB.name + '-- Pred_name: ' + myRB.myPred[0].name + ' ('
        # organise the links by weight to disply from hight to low. 
        link_list = []
        for link in myRB.myPred[0].mySemantics:
            link_list.append([link.mySemantic.name, link.weight])
            link_list.sort(key=lambda x: x[1], reverse=True)
        for link in link_list:
            RB_string = RB_string + link[0] + '-' + str(link[1]) + ', '
        RB_string = RB_string + ') -- Obj_name:' + myRB.myObj[0].name + ' ('
        # organise the links by weight to disply from hight to low. 
        link_list = []
        for link in myRB.myObj[0].mySemantics:
            link_list.append([link.mySemantic.name, link.weight])
            link_list.sort(key=lambda x: x[1], reverse=True)
        for link in link_list:
            RB_string = RB_string + link[0] + '-' + str(link[1]) + ', '
        RB_string += ')'
        print(RB_string)

# function to display PO (for use with .term_network_display).
def term_display_PO(myPO, counter):
    if len(myPO.myRBs) == 0:
        print('')
        PO_string = 'PO ' + str(counter) + '. -- Obj_name: ' + myPO.name + ' ('
        # organise the links by weight to disply from hight to low. 
        link_list = []
        for link in myPO.mySemantics:
            link_list.append([link.mySemantic.name, link.weight])
        link_list.sort(key=lambda x: x[1], reverse=True)
        for link in link_list:
            PO_string = PO_string + link[0] + '-' + str(link[1]) + ', '
        PO_string += ')'
        print(PO_string)

# function to display the mapping state of the network (i.e., how driver and recipient map).
def term_map_display(memory):
    # for each item in the driver, write its name and show the unit in the recipient it most maps to and the mapping weight.
    memory = basicRunDORA.get_max_map_units(memory)
    for group in memory.driver.Groups:
        if group.max_map_unit:
            group_string = 'GROUP: ' + group.name + ' -- ' + group.max_map_unit.name + ' -- mapping_weight=', group.max_map
        else:
            group_string = 'GROUP: ' + group.name + ' -- ' + 'NONE' + ' -- mapping_weight=', group.max_map
        print(group_string)
    for myP in memory.driver.Ps:
        if myP.max_map_unit:
            P_string = 'P: ' + myP.name + ' -- ' + myP.max_map_unit.name + ' -- mapping_weight=', myP.max_map
        else:
            P_string = 'P: ' + myP.name + ' -- ' + 'NONE' + ' -- mapping_weight=', myP.max_map
        print(P_string)
    for myRB in memory.driver.RBs:
        if myRB.max_map_unit:
            RB_string = 'RB: ' + myRB.name + ' -- ' + myRB.max_map_unit.name + ' -- mapping_weight=', myRB.max_map
        else:
            RB_string = 'RB: ' + myRB.name + ' -- ' + 'NONE' + ' -- mapping_weight=', myRB.max_map
        print(RB_string)
    for myPO in memory.driver.POs:
        if myPO.max_map_unit:
            PO_string = 'PO: ' + myPO.name + ' -- ' + myPO.max_map_unit.name + ' -- mapping_weignt=', myPO.max_map
        else:
            PO_string = 'PO: ' + myPO.name + ' -- ' +'NONE' + ' -- mapping_weignt=', myPO.max_map
        print(PO_string)

# function to display names of all tokens of a particular type and their place in memory.
def display_token_names(memory, token):
    if token == 'GROUP':
        group_counter = 0
        for group in memory.groups:
            group_counter += 1
            print((group_counter, ' -- ', group.name))
    if token == 'P':
        P_counter = 0
        for myP in memory.Ps:
            P_counter += 1
            print((P_counter, ' -- ', myP.name))
    elif token == 'RB':
        RB_counter = 0
        for myRB in memory.RBs:
            RB_counter += 1
            print((RB_counter, ' -- ', myRB.name))
    elif token == 'PO':
        PO_counter = 0
        for myPO in memory.POs:
            PO_counter += 1
            print((PO_counter, ' -- ', myPO.name))

# function to display all properties of a specific unit.
def display_unit(unit):
    # display the unit's act, net_input, td_input, bu_input, map_input, max_map, mappingHypotheses, and mappingConnections.
    print('')
    print(('act', unit.act))
    print(('net_input', unit.net_input))
    print(('td_input', unit.td_input))
    print(('bu_input', unit.bu_input))
    print(('lateral_input', unit.lateral_input))
    print(('map_input', unit.map_input))
    print('HYPOTHESES:')
    for hypothesis in unit.mappingHypotheses:
        print((hypothesis.driverToken.name, hypothesis.recipientToken.name, hypothesis.hypothesis))
    print('MAPPINGS:')
    for mapping in unit.mappingConnections:
        print((mapping.driverToken.name, mapping.recipientToken.name, mapping.weight))
    print('')

# function to display mapping hypothesis information for DEBUGGING.
def display_mapHyp(memory):
    for hypothesis in memory.mappingHypotheses:
        print((hypothesis.driverToken.name, hypothesis.recipientToken.name, hypothesis.hypothesis, hypothesis.max_hyp))



