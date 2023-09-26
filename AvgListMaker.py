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
import statistics
import csv
import os
import math

FIRST_BANDING_LIMITER = 16384
LAST_BANDING_LIMITER = 49150


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

def write_to_csv(filename, avglist, numblocks):
    # Open the CSV file for writing
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the header row
        csvwriter.writerow(['NumBlocks', 'Average'])
        
        # Loop through data and write each row
        for i in range (len(avglist)) : 
            csvwriter.writerow([str(numblocks[i]), '{:.4f}'.format(avglist[i])])

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

    avgtotal = statistics.mean(chunk_averages)
    stddev = statistics.stdev(chunk_averages)
    
    return chunk_averages, stddev, avgtotal

def main():
    try:
        
        avglist = []
        bitlists = []
        proclists = []
        numblocks = []

        prevdir = os.getcwd() # Purely for clarity of use

        # Get directory
        input_dir = input("Enter the input directory: ")
        one_or_two = input("2 chips? Y/N (N == one chip) ")
        if (one_or_two == 'Y') :
            iterations = 201
        else : 
            iterations = 101
        # If directory doesn't exist, throw error
        if not os.path.exists(input_dir):
            raise FileNotFoundError("This directory does not exist.")
        os.chdir(input_dir)

        for i in range(1, iterations) :
            if not os.path.exists(input_dir+'_'+str(i)+'.csv'):
                raise FileNotFoundError("File '"+input_dir+"_"+str(i)+".csv' does not exist.")
            
            a, b = read_csv(input_dir+'_'+str(i)+'.csv')
            bitlists.append(b)
            proclists.append(pre_processing(bitlists[i-1]))            

        os.chdir(prevdir)
        if not os.path.exists(input_dir+'Stats'):
            os.mkdir(input_dir+'Stats')
        os.chdir(input_dir+'Stats')

        for i in range(1,iterations) :
            
            for x in range(2,21) :
                averages, stddev, avgtotal = calculate_mean_and_dev(proclists[i-1], (x*x)) # SET NUMBERS LATER
                
                if (i == 1) :
                    for j in range(x*x) :
                        numblocks.append(x*x)

                avglist.append(averages)
            
            avglist = [item for sublist in avglist for item in sublist]

            filename = input_dir+'_'+str(i)+'AvgList.csv'
            write_to_csv(filename, avglist, numblocks)
            
            avglist.clear()        

        print("All statistics files created and placed in directory "+prevdir+"/"+input_dir+"Stats")
        
            # Error Handler
    except Exception as e:
        print("An error occurred: {e}")

    # Return to program directory, create training data directory and save training data to it
    finally:
        os.chdir(prevdir)    

if __name__ == "__main__":
    main()