#from Phuong T. Pham - Begin: 08.10.2021
import cv2
import numpy as np
import os
import glob
import mahotas as mt
import matplotlib.pyplot as plt
import string

#define a extract haralick features function
def extract_haralick_features(image):
    features = mt.features.haralick(image)

    haralick_features_mean = features.mean(axis=0)
    return haralick_features_mean


#define a extract LBP features function
def extract_LBP(image):
    feat = mt.features.lbp(image=image, points=(2*8), radius=2, ignore_zeros="True")
    feat = np.reshape(cv2.calcHist([np.float32(feat)], [0], None, [256], [0, 256]),(256))
    return feat

#devide a image in 5x4 grid images and calculating the HF for each image
def features_of_grid(image, axis = 0):
    height = image.shape[0]
    width = image.shape[1]    

    x_step = int(width / 5)
    y_step = int(height / 4)

    x = 0
    y= 0
    
    all_features = []
    
    for j in range(4):
        if j < 3: 
            h = y_step 
        else:
            h = height - y
        for i in range(5):
            if i < 4: 
                w = x_step 
            else:
                w = width - x
        
            crop_img = image[y:y+h, x:x+w] 
            
            x += w
            if axis == 0:
                if i == 0 and j == 0:
                    all_features = extract_haralick_features(crop_img)
                elif j == 0 and i == 1:
                    hfc = extract_haralick_features(crop_img)
                    all_features = np.stack((all_features, hfc), axis=-1)
                else:
                    hfc = []
                    hfc.append(extract_haralick_features(crop_img))
                    hfc = np.asarray(hfc)
                    all_features = np.concatenate((all_features, hfc.T), axis=1)
            else:
                all_features.append(extract_haralick_features(crop_img))
        y += h
        x= 0
            
    return all_features


def extract_HF_of_a_probe(image1_path, image2_path, axis = 0):
    image = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
    if axis == 0:
        f = np.column_stack((features_of_grid(gray, axis=axis), features_of_grid(gray2, axis= axis)))
    else:
        f = np.row_stack((features_of_grid(gray, axis=axis), features_of_grid(gray2, axis= axis)))
       
    return f




def extract_HF_mean_of_a_probe(grid_features):
    return np.mean(grid_features, axis= 1)

def extract_HF_mean_of_a_probe(image1_path, image2_path):
    features = extract_HF_of_a_probe(image1_path, image2_path)
    return np.mean(features, axis= 1)

def get_labels_of_grid():
    g = string.ascii_uppercase
    g = g[:20]
    g = list(g)
    k = string.ascii_lowercase
    k = k[:20]
    k = list(k)
    k = np.asarray(k)
    k = np.split(k, 4)
    k = np.flipud(k)
    k = k.flatten()
    g = np.stack((g, k))
    apb = g.flatten()
    return apb

# fs = extract_HF_of_a_probe("./Klebeverbindungen_Daten/2D-MakroImages/ProbeE2_1.png", 
#                                         "./Klebeverbindungen_Daten/2D-MakroImages/ProbeE2_2.png", axis=1)
# print(fs)