# ----------------------------------------------------------------------------------
# A .py script that takes one .csv file deliminated into
# "Address,Word" format, splits the bit data into equal and even 
# square-shaped divisions as cleanly as possible, and determines the average
# incidence of 1s in each division, the average of all averages, and the 
# standard deviation of the averages. This statistics are therein dumped
# into .csv files of their own.
#
# This script is currently configured for a memory device of size 8kB.
# It is intended to be used after "PreProcess.py".
#
# The program will create a directory under the working directory,
# titled 'TRAINING_DATA', and store the file into it. If this directory already
# exists, it will just store the file into the existing directory.
#
# Author : Gaines Odom
# Email : gaines.a.odom@gmail.com
# Inst. : Auburn University
# Advisor : Dr. Ujjwal Guin
#
# Created On : 08/24/2023
# Last Edited On: 08/28/2023
# ----------------------------------------------------------------------------------
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
from scipy.stats import norm
import statistics
import csv
import os
import math

FIRST_BANDING_LIMITER = 16384
LAST_BANDING_LIMITER = 49150

blockdict = {
    0: 16384,
    1: 7225,
    2: 4096,
    3: 2601,
    4: 1764,
    5: 1296,
    6: 1024,
    7: 784,
    8: 625,
    9: 529,
    10: 441,
    11: 361,
    12: 324,
    13: 289,
    14: 256,
    15: 225,
    16: 196,
    17: 169,
    18: 144
}


def Gauss(x, A, B):
    y = A*np.exp(-1*B*x**2)
    return y

def func(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

def make_plot(x, actually_make_plot, chip_number,num_blocks) :
    mu, sigma = norm.fit(x) 
    #mu_perc = mu/100
    '''if (actually_make_plot == 1) :
        num_bins = 10

        fig, ax = plt.subplots()

        # the histogram of the data
        n, bins, patches = ax.hist(x, num_bins, density=True)

        # add a 'best fit' line
        y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
            np.exp(-0.5 * (1 / sigma * (bins - mu))**2))
        ax.plot(bins, y, '--')
        plt.xlim(0.60,0.75)
        ax.set_xlabel('Percent of 1s at Startup')
        ax.set_ylabel('Probability Density')
        ax.set_title('Chip '+str(chip_number)+' $\mu={:.2%}$, $\sigma={:.2%}$'.format(mu, sigma))

        # Tweak spacing to prevent clipping of ylabel
        #fig.tight_layout()
        
        fname = 'hist_plot_chip'+str(chip_number)+'_'+str(num_blocks)+'blocks.png'
        plt.savefig(fname)
        plt.close()'''
    return mu, sigma

# Pre-Processing function: takes 65536 int list as input 'bitlist', inverts every bit within banding limiters, and returns pre-processed list of 65536 ints as 'blist'
def pre_processing(bitlist) :
   
    blist = []
    inverter = {1:0, 0:1}

    # Invert banded section
    for i in range(len(bitlist)) :
        if i < FIRST_BANDING_LIMITER or i > LAST_BANDING_LIMITER:
            blist.append(bitlist[i])
        else :
            blist.append(inverter[bitlist[i]])

    return blist

def write_to_csv(filename, sdevs, avgtots):
    # Open the CSV file for writing
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the header row
        csvwriter.writerow(['Block Size', 'Average','Standard Deviation'])

        # Loop through data and write each row
        for i in range (len(avgtots)) : 
            csvwriter.writerow([blockdict[i], '{:.4f}'.format(avgtots[i]), '{:.4f}'.format(sdevs[i])])

# .csv Decoding function. Takes .csv files of the format "Address,Word" and returns int list of addresses and int list of binary values.
def read_csv(filename):
    addresses = []
    bit_list = []
    bits = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader) # skips "Address,Word" header line
        for row in csvreader:
            address, byte = row # row = address: in leftmost space, byte: in rightmost space
            addresses.append(int(address, 16))  # Turns 4 digit hex address into decimal int value list
            bit_list.append(bin(int(byte, 16))[2:].zfill(8))    # Turns 2 digit hex byte into 8 bit binary string list

    # Create a list of 1-bit strings from 8-bit binary strings        
    for byte in bit_list:
        for bit in byte:  
            bits.append(bit)
    
    # Turn 1-bit strings into 1-bit ints
    bits = [int(bit) for bit in bits]

    return addresses, bits

def calculate_mean_and_dev(bitlist, num_of_blocks) : # num_of_blocks should be a squared product of an int, ex. 4, 9, 16 etc.
    
    chunk_size = int(math.sqrt(len(bitlist) // num_of_blocks)) # round down: 65536 // 81 = 809 -> int(sqrt(809)) = 28 -> chunks are 28x28
    excess_bits = len(bitlist) - (num_of_blocks * chunk_size * chunk_size) # 65536 - (81 * 28 * 28) = 2032
    row_size = 256 * chunk_size   # 256 * 28 = 7168 (start at addr 0, incrementing by 28, until next row -> addr is 0 + 7168)
    chunks_per_row = int(math.sqrt(num_of_blocks)) # chunks_per_row = sqrt(81) = 9
    chunks_per_column = int(math.sqrt(num_of_blocks))
    x_offset = math.ceil((excess_bits // 511) / 2)   # keeps it off the wall for purposes of evenness. Centremost divisions are used
    y_offset = x_offset * 256
    # print(str(chunk_size*chunk_size))
    chunk_averages = []
    chunk = []

    for i in range(chunks_per_column):
        for j in range(chunks_per_row):
            start_idx = i * row_size + j * chunk_size + x_offset + y_offset
            for k in range (chunk_size) : 
                vert_addr  = start_idx + k * 256
                end_idx = vert_addr + chunk_size
                chunk.append(bitlist[vert_addr:end_idx])
            
            chunk = [item for sublist in chunk for item in sublist]

            average = statistics.mean(chunk)
            
            chunk_averages.append(average)
            chunk.clear()
    #chunk_averages = [(item * 100) for item in chunk_averages]
    avgtotal = statistics.mean(chunk_averages)
    stddev = statistics.stdev(chunk_averages)
    
    return chunk_averages, stddev, avgtotal

def main():
    try:
        devlist = []
        avglist = []
        bitlists = []
        proclists = []
        list25 = []
        list16 = []
        list9 = []
        prevdir = os.getcwd() # Purely for clarity of use

        # Get directory
        input_dir = input("Enter the input directory: ")
        one_or_two = input("2 chips? Y/N (N == one chip)")
        if (one_or_two == 'Y') :
            itera = 201
        else : 
            itera = 101
        # If directory doesn't exist, throw error
        if not os.path.exists(input_dir):
            raise FileNotFoundError("This directory does not exist.")
        os.chdir(input_dir)

        for i in range(1, itera) :
            if not os.path.exists(input_dir+'_'+str(i)+'.csv'):
                raise FileNotFoundError("File '"+input_dir+"_"+str(i)+".csv' does not exist.")
            
            a, b = read_csv(input_dir+'_'+str(i)+'.csv')
            bitlists.append(b)
            proclists.append(pre_processing(bitlists[i-1]))            

        os.chdir(prevdir)
        if not os.path.exists(input_dir+'Stats'):
            os.mkdir(input_dir+'Stats')
        os.chdir(input_dir+'Stats')

        for i in range(1,itera) :
            
            for x in range(2,21) :
                averages, stddev, avgtotal = calculate_mean_and_dev(proclists[i-1], (x*x)) # SET NUMBERS LATER
                #print("Averages:", averages)
                #print("Standard Deviations:", stddev)
                #print("ok")

                mu, sigma = make_plot(averages, 0,1,0)
                #print("ok2")
                avglist.append(mu)
                devlist.append(sigma) 

                #if (x == 3) : list9.append(averages)
                #if (x == 4) : list16.append(averages)
                #if (x == 5) : list25.append(averages)
                
            filename = input_dir+'_'+str(i)+'Stats.csv'
            write_to_csv(filename, devlist, avglist)
            #if not os.path.exists(filename):
                #raise FileNotFoundError("Did not create "+filename+".")
            # else : 
                # print("CSV file "+filename+" has been created.")
            
            avglist.clear()
            devlist.clear()
        

        print("All statistics files created and placed in directory "+prevdir+"/"+input_dir+"Stats")
        #make_plot(list9[:len(list9)//2],1,1,9)
        #make_plot(list9[len(list9)//2:],1,2,9)
        #make_plot(list16[:len(list16)//2],1,1,16)
        #make_plot(list16[len(list16)//2:],1,2,16)
        #make_plot(list25[:len(list25)//2],1,1,25)
        #make_plot(list25[len(list25)//2:],1,2,25)
        print ("All plots made and saved in directory "+prevdir+"/"+input_dir+"Stats")
            # Error Handler
    except Exception as e:
        print("An error occurred: {e}")

    # Return to program directory, create training data directory and save training data to it
    finally:
        os.chdir(prevdir)    

if __name__ == "__main__":
    main()