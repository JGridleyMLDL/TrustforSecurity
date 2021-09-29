# Created by Jared Gridley - 10/18/2020
# Rensselear Polytechnic Institute - Deep Learning for Threat Intelligence
#
# This will parse through the freebase text file and create a database as a json file
# Run with:
#   $ python this-script.py [input_file] [output_file]

import json
import sys
import os



# Testing opening the input file for reading
def CheckFile(file):
    try:
        open(file, "r")
        return 1
    except IOError:
        print("Error: Cannot find input file in specified directory.")
        return 0
    #File closes automatically after leaving function scope



#Time to start actually reading the file:
def parse_text(ifile, ofile):
    #Seperates each line into Subject, Object, Predicate triple and stores in json file

    while True:
        line = ifile.readline()

        #Parse the line into a python dictionary
        split_line = line.strip().split("\t")

        #If at end of file, end the loop
        if len(split_line) != 3:
            break 

        temp_dict = {
            "Subject": split_line[0],
            "Predicate": split_line[1],
            "Object": split_line[2],
        }

        json.dump(temp_dict, ofile, ensure_ascii=False, indent = 4)  
        temp_dict.clear()

    return None



# main - parsing through the command line arguments
if __name__ == '__main__':

    input_file = ''
    output_file = ''

    #Check for correct number of arguments
    arg_num = len(sys.argv)
    if(arg_num != 3):
        print("Usage: $ python this-script.py [input_file] [output_file]")
        sys.exit(2)

    #Setting input and output files
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    #Is the input file there?
    if(CheckFile(input_file) == False):
        sys.exit(2)
    
    infile = open(input_file, 'r')
    outfile = open(output_file, 'w')

    parse_text(infile, outfile)
    
    infile.close()
    outfile.close()

    print("JSON conversion sucessful.")


