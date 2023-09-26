# ----------------------------------------------------------------------------------
# A .py script that takes one (or multiple) .csv file(s) deliminated into
# "Address,Word" format and creates a bitmap from them.
#
# This script is currently configured for a memory device of size 8kB.
# It creates a 256 by 256 bitmap in Single-Full & Distribution-Full Modes.
# It creates a 256 by 156 bitmap in Single-Image & Distribution-Image Modes.
#
# To use in Single Mode: Place singular file in the same directory as program.
# Select 'SF' as mode, and provide name of file, sans '.csv'.
# The program will create a directory under the current working directory,
# titled 'BITMAPS', and store the bitmap into it. If this directory already
# exists, it will just store the bitmap into the existing directory.
#
# To use in Distribution Mode: Place file directory under the working directory.
# Select 'F' as mode, and provide name of file directory.
# The program will create a directory under the working directory,
# titled 'BITMAPS', and store the bitmap into it. If this directory already
# exists, it will just store the bitmap into the existing directory.
#
# Author : Gaines Odom
# Email : gaines.a.odom@gmail.com
# Inst. : Auburn University
# Advisor : Dr. Ujjwal Guin
#
# Created On : 08/05/2023
# Last Edited On: 08/31/2023
# ----------------------------------------------------------------------------------

import csv
import os
from PIL import Image

# Constants (Change if necessary, currently set for 8kB chip)
CHIP_WIDTH = 256
CHIP_HEIGHT = 256
IMAGE_HEIGHT = 156
SINGLE = 1
SUM = 100
WORD_SIZE = 8
DOUBLE = 200

# Bitmap Type Dictionary. Sets appropriate parameters for single run and distribution bitmaps.
bitmap_type = {
    'I': [CHIP_WIDTH, IMAGE_HEIGHT, SUM],
    'F': [CHIP_WIDTH, CHIP_HEIGHT, SUM],
    'SI': [CHIP_WIDTH, IMAGE_HEIGHT, SINGLE],
    'SF': [CHIP_WIDTH, CHIP_HEIGHT, SINGLE],
    '2CI': [CHIP_WIDTH, IMAGE_HEIGHT, DOUBLE],
    '2CF': [CHIP_WIDTH, CHIP_HEIGHT, DOUBLE],
    'default': [0,0,0],
}

# .csv Decoding function. Takes .csv files of the format "Address,Word" and returns int list of addresses and int list of binary values.
def read_csv(filename):
    addresses = []
    bit_list = []
    bits = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            address, byte = row
            addresses.append(int(address, 16))  # Turns 4 digit hex address into decimal int value list
            bit_list.append(bin(int(byte, 16))[2:].zfill(WORD_SIZE))    # Turns 2 digit hex byte into 8 bit binary string list

    # Create a list of 1-bit strings from 8-bit binary strings        
    for byte in bit_list:
        for bit in byte:  
            bits.append(bit)
    
    # Turn 1-bit strings into 1-bit ints
    bits = [int(bit) for bit in bits]

    return addresses, bits

# Bit Distribution Creator. Uses "weight" list to determine how dark a pixel is (darker pixels imply more frequent occurence of 1's).
def create_bit_distribution(weight,width,height,iterations): 
    img = Image.new('RGB', (width, height), color='white')
    for y in range(height):
        for x in range(width):
            pixel_index = y * width + x
            pixel_value = 255 - int(weight[pixel_index] * 255/iterations)
            img.putpixel((x, y), (pixel_value,pixel_value,pixel_value))
    return img

# Bitmap Creator. Uses raw bit data list to determine whether or not a pixel will be black or white.
def create_bitmap(bits, width, height): # deal with this
    img = Image.new('1', (width, height), color=0)
    for y in range(height):
        for x in range(width):
            pixel_index = y * width + x
            pixel_value = 1 - bits[pixel_index]
            img.putpixel((x, y), pixel_value)
    return img

def main():
    try:
        weight = []
        lists = []
        prevdir = os.getcwd()
        input_text = '''
    Enter the bitmap type.
    Your options are: 
    'I' ["Image" -- A bit distribution map of binary image, 100 reads.]
    'F' ["Full" -- A bit distribution map of full chip, 100 reads.]
    'SI' ["Single Image" -- A purely B&W bitmap of one image read.]
    'SF' ["Single Full" -- A purely B&W bitmap of one full read.]
    '2CI' ["2 Chip Image" -- A bit distribution map of binary image, 200 reads.]
    '2CF' ["2 Chip Full" -- A bit distribution map of full chip, 200 reads.]
    '''
        print(input_text)
        type = input().strip()

        # Set the type
        bitmap_width, bitmap_height, iterations = bitmap_type.get(type, bitmap_type['default'])

        # Create bitmap directory (if necessary)
        if not os.path.exists('BITMAPS'):
            os.mkdir('BITMAPS')

        # SI or SF execution block
        if iterations == SINGLE : 
            # Get file
            input_file = input("Enter the file name (File MUST be in this directory): ")

            # If file does not exist, throw error
            if not os.path.exists(input_file+'.csv'):
                raise FileNotFoundError("This file does not exist.")

            # Read .csv file
            addresses, bytelist = read_csv(input_file+'.csv')
            
            # Create bitmap and name output file
            bitmap = create_bitmap(bytelist, bitmap_width, bitmap_height) 
            output_file = input_file+'-bitmap.png'
            
            # Enter bitmap directory and save output file
            os.chdir('BITMAPS')
            bitmap.save(output_file)
            print("Bitmap generated and saved as "+output_file+" in "+prevdir+"\BITMAPS.")

        # I or F execution block
        else :
            # Get directory
            input_file = input("Enter the file directory (e.g. 'JUL4' for JUL4_1.csv to JUL4_100.csv): ")
            
            # If directory doesn't exist, throw error
            if not os.path.exists(input_file):
                raise FileNotFoundError("This directory does not exist.")
            
            # Go to directory 
            os.chdir(input_file)
            
            # Read all files. If missing even one, error is thrown.
            for i in range(1, iterations + 1) :
                if not os.path.exists(input_file+'_'+str(i)+'.csv'):
                    raise FileNotFoundError("File '"+input_file+"_"+str(i)+".csv' does not exist.")
                
                a, b = read_csv(input_file+'_'+str(i)+'.csv')
                lists.append(b)

            # Compute weight for bit distribution
            for nums in zip(*lists):
                total = sum(nums)
                weight.append(total)
            #print(weight)     # For use in debugging

            # Create bit distribution and name output file
            bit_distribution = create_bit_distribution(weight, bitmap_width, bitmap_height, iterations)
            output_file = input_file+'-bitdistribution.png'

            # Leave directory full of .csv files
            os.chdir(prevdir)

            # Enter bitmap directory and save output file
            os.chdir('BITMAPS')
            bit_distribution.save(output_file)
            print("Bit distribution generated and saved as "+output_file+" in "+prevdir+"\BITMAPS.")

    # Error Handler
    except Exception as e:
        print("An error occurred: {e}")

    # Return to program directory
    finally:
        os.chdir(prevdir)    

if __name__ == "__main__":
    main()
