#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 09:57:15 2021

@author: jean-louquetin
"""

import cv2
import numpy as np
from PIL import Image

# Get screen size to display images within the visible range
import tkinter
root = tkinter.Tk()
root.withdraw()
SCREEN_WIDTH, SCREEN_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()

A4_ratio = 210.0/ 297.0

class PDFSaver:
    
    def __init__(self):
        A4 = input("Are you using A4 ? [y]/n\n")
        if A4=="n" or A4=="N":
            width = input("Width ?\n")
            height = input("Height ?\n")
            self.ratio = float(width)/float(height)
        else:
            self.ratio = A4_ratio
        self.pts = np.array([])
        self.ptsLocations = ["Bottom right", "Top Right", "Top left", "Bottom left"]

    # Main function : creates cropping the image to get only the targeted sheet
    def createPDF(self, input_image):
    
        self.original = input_image
        self.original_scaled, self.imgScale = self. __fit2screen(input_image)
        self.original_loop = np.array(self.original_scaled)

        blurred = cv2.GaussianBlur(input_image, (3, 3), 1)
        work_image = rescale_frame(blurred, self.imgScale*100)

        
        
        validated = False
        question = "Do you validate these corners ? [y]\nDo you want to rotate them clock-wise/ counter clock-wise? c/cc\nOr would you like to point them manually ? n\n"
        answer = "auto"

        while not(validated): # Loop until the user is OK with the result
            
            cv2.namedWindow('Proposition', cv2.WINDOW_NORMAL)
            cv2.setMouseCallback('Proposition',self.__choose_corners)
            while (True): # Loop until corners chosen are validated
                self.setPts = 0
                self.original_loop = np.array(self.original_scaled)
                if answer == "auto":
                    # Try to find the sheet autonomously
                    self.__computeCorners(work_image)
                    self.__draw_computed_pts(self.original_loop)
                    cv2.imshow('Proposition',self.original_loop)
                    answer = input(question)
                elif answer == "cc":
                    tmp = np.copy(self.pts[0])
                    self.pts[0:-1,:] = self.pts[1:,:]
                    self.pts[-1,:] = tmp
                    self.__draw_computed_pts(self.original_loop)
                    cv2.imshow('Proposition',self.original_loop)
                    answer = input(question)
                elif answer == "c":
                    tmp = np.copy(self.pts[-1])
                    self.pts[1:,:] = self.pts[0:-1,:]
                    self.pts[0,:] = tmp
                    self.__draw_computed_pts(self.original_loop)
                    cv2.imshow('Proposition',self.original_loop)
                    answer = input(question)
                elif answer == "n":
                    self.__manual_corner_selection()
                    answer = input("Do you validate these corners ? [y]/n\n")
                else:
                    break
            
            cv2.destroyAllWindows()
                
            self.result = self.__compute_transformation(self.original)
            
            result_scaled = rescale_frame(self.result, self.imgScale*100)
            cv2.imshow('Result',result_scaled)

            answer = input("Are you happy with the result ? [y]/n\n")
            if answer!="n":
                validated = True
            else:
                answer = "auto"
                # cv2.namedWindow('Proposition', cv2.WINDOW_NORMAL)
                # cv2.setMouseCallback('Proposition',self.__choose_corners)
                # cv2.imshow('Proposition',self.original_loop)
                # cv2.waitKey(1)
        
        return self.result

    def save_to_pdf(self, path, im):
        im = Image.fromarray(im[:,:,::-1]) # need to convert from bgr to rgb
        im.save(path)
        print("The pdf version of your image was saved at \n", path)
    
    # Compute mask for white paper sheet
    def __computeMask(self, im):
        gray_frame = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ## Threshold the HSV image to get src white colors
        binary = cv2.inRange(gray_frame, 160, 255)
        binary = cv2.erode(binary, kernel=None, iterations = 1)
        binary = cv2.dilate(binary, kernel=None, iterations = 1)
        return binary
    
    # Compute corners of the white sheet in the image
    def __computeCorners(self, orig):
        
        binary = self.__computeMask(orig)
         
        _, contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        contours = filter(lambda cont: cv2.arcLength(cont, False) > 100, contours)
        contours = filter(lambda cont: cv2.contourArea(cont) > 10000, contours)
        
        # simplify contours down to polygons
        self.rects = []
        for cont in contours:
            rect = cv2.approxPolyDP(cont, 40, True).copy().reshape(-1, 2)
            self.rects.append(rect)
        
        self.pts = self.rects[0]

    
    # Mouse callback function to draw corners manually
    def __choose_corners(self, event,x,y,flags,param):
        if event == cv2.EVENT_FLAG_LBUTTON:
            self.pts[self.setPts,:] = np.array([x, y])
            print("Corner ", self.setPts+1, " selected")
            
            if self.setPts < 3:
                self.original_loop = np.array(self.original_scaled)
                cv2.putText(self.original_loop, self.ptsLocations[self.setPts+1], self.txtLocation, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                for i in range(self.setPts+1):
                    cv2.drawMarker(	self.original_loop, (self.pts[i, 0], self.pts[i, 1]), (0,0,255), cv2.MARKER_CROSS , 4, 3)
            if self.setPts == 3:
                self.original_loop = np.array(self.original_scaled)    
                self.rects = [self.pts]
                self.__draw_computed_pts(self.original_loop)
                cv2.imshow('Proposition',self.original_loop)
                cv2.waitKey(10)
                

            self.setPts+=1
            
    # Choose corners manually thanks to the callback function on the window
    def __manual_corner_selection(self):
        self.setPts = 0
        self.pts = np.zeros((4,2), dtype=np.int32)
        self.txtLocation = (10, 30)
        cv2.putText(self.original_loop, self.ptsLocations[self.setPts], self.txtLocation, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        print("You can start selecting corners on the image !")
        while(1):
            cv2.imshow('Proposition',self.original_loop)
            if cv2.waitKey(20) & 0xFF == 27:
                break
            if self.setPts >= 4:
                break
            
    # Transforms an image given points corrsponding to the corners in the input image
    def __compute_transformation(self, image):
        self.__to_original_scale()
        D1 = np.max(self.pts[:,0]) - np.min(self.pts[:,0])
        D2 = np.max(self.pts[:,1]) - np.min(self.pts[:,1])
        height = max(D1, D2)
        width = int(height * self.ratio)
        
        dstPts = np.array([[0, 0],
                           [height-1, 0],
                           [height-1, width-1],
                           [0, width-1]])
        
        transformationMatrix, mark = cv2.findHomography(self.pts, dstPts, cv2.RANSAC)
        
        dst = cv2.warpPerspective(image, transformationMatrix, dsize=(height, width), flags=cv2.INTER_CUBIC)
        dst = cv2.transpose(dst)
        dst = cv2.rotate(dst, cv2.ROTATE_180)
        return dst
    
    # Resizing the image for it to fit within the computer screen
    def __fit2screen(self, original_img):
         height, width, depth = original_img.shape
         scaleWidth = 0.85*float(SCREEN_WIDTH)/float(width) 
         scaleHeight = 0.85*float(SCREEN_HEIGHT)/float(height)
         imgScale = min(scaleWidth, scaleHeight)
    
         newX,newY = original_img.shape[1]*imgScale, original_img.shape[0]*imgScale
         newimg = cv2.resize(original_img,(int(newX),int(newY)))
         return newimg, imgScale
     
        
    # Allows to bring back points selected on the resized image to points in the original image
    def __to_original_scale(self):
        for i in range(len(self.pts)):
            self.pts[i][0] = int(self.pts[i][0]/self.imgScale)
            self.pts[i][1] = int(self.pts[i][1]/self.imgScale)
           
    # Drawinf function for corners and  edges
    def __draw_computed_pts(self, img):
        cv2.drawContours(img, self.rects,-1,(0,255,0),1)
        for i in range(4):
            cv2.putText(img, self.ptsLocations[i], (self.pts[i, 0]+10, self.pts[i, 1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.drawMarker(	img, (self.pts[i, 0], self.pts[i, 1]), (0,0,255), cv2.MARKER_CROSS , 4, 3)

    
         
def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

        
        


