#!/usr/bin/env python

###################################################
#  label-printer.py
#  Author:  N4tH4N
#  Date:    09/02/2018
#  Brief:   a python program to scrape a jobs txt file, save
#           all the parts into arrays and then print the
#           parts on the job to the brother ql-580n label printer
###################################################

import re
from brotherprint import BrotherPrint
import socket
import time

##################################################################
############     Opening the .txt file to work on    #############
##################################################################

txt_file = open('89131.txt', "r")
contents = txt_file.read()
txt_file_lines = contents.splitlines()  # have to do this because python adds extra line breaks
txt_file.close()

##################################################################
#######   Finding all the lines that have * - number *    ########
##################################################################

ticket_line_number_array = []
customer = ""
job_number = ""

counter = 1
for line in txt_file_lines:
    # finding the start of each job ticket
    # using regex to find lines that contain for e.g. *88931-1*
    if re.match("^\*.*-[0-9]*\*", line) is not None:
        ticket_line_number_array.append(counter)
    # the customers name is always on line 2
    if counter == 2:
        customer = line
    # the fist job ticket start on line 3
    elif counter == 3:
        job_number = line
        # removing the '*' from the job number
        job_number = job_number.replace("*", "")
        # removing everything after the '-' to leave only the job number left
        job_number = re.sub("-.*$", "", job_number)
    counter += 1

array_length = len(ticket_line_number_array)

print "Customer =", customer
print "Job Number =", job_number
print "The number of parts in the job =", array_length
print

##################################################################
############  Creating the Client Part Number Array  #############
##################################################################

client_part_number_array = []

for i in ticket_line_number_array:
    lines_ahead_array = []
    for counter, line in enumerate(txt_file_lines, 1):
        if counter < ( i + 12 ) and counter > ( i + 3 ):
            lines_ahead_array.append(line)

    for j, item in enumerate(lines_ahead_array):
        if j < 3 and item.find("Issue Date") >= 0:
            # going back by one line and splitting the string by {TAB}
            client_part_number_array.append(lines_ahead_array[j-1].split("\t")[1])
        elif j > 4 and item.find("Issue Date") >= 0:
            # going back by two lines
            client_part_number_array.append(lines_ahead_array[j-2])


# for counter, item in enumerate(client_part_number_array, 1):
#     print "Item number", counter, ":", item

###################################################
############  Creating the Qty Array  #############
###################################################

qty_array = []

for i in ticket_line_number_array:
    lines_ahead_array = []
    for counter, line in enumerate(txt_file_lines, 1):
        if counter < ( i + 15 ) and counter > ( i + 6 ):
            lines_ahead_array.append(line)

    for j, item in enumerate(lines_ahead_array):
        if item.find("Order Qty") >= 0:
            qty_array.append(lines_ahead_array[j+1].split("\t")[4])


# for i, item in enumerate(ticket_line_number_array):
#     if i < len(ticket_line_number_array):
#         ticket_number = str(i + 1)
#         ticket_number = job_number + "-" + ticket_number
#     print "Ticket No.", ticket_number, "Part No:", client_part_number_array[i], "Qty:", qty_array[i]



###########################################################
############   Starting to print the labels   #############
###########################################################

f_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# The IP Address of the printer is 192.168.5.64 and the default port number for it is 9100
f_socket.connect(('192.168.5.64', 9100))
printjob = BrotherPrint(f_socket)

printjob.template_mode()
printjob.template_init()
# This command to stop the printer from cutting every label after it prints it
printjob.send('^CO0990')
# The Varley template is template number: 1
printjob.choose_template(1)

for i, item in enumerate(ticket_line_number_array):
    if i < ticket_line_number_array:
        ticket_number = str(i + 1)
        ticket_number = job_number + "-" + ticket_number
    printjob.template_init()
    printjob.send('^CO0990')
    printjob.select_and_insert("part no.", client_part_number_array[i])
    print "Client Part Number:", client_part_number_array[i]
    printjob.select_and_insert("qty", qty_array[i])
    print "Qty:", qty_array[i]
    printjob.select_and_insert("ticket no.", ticket_number)
    print "Ticket Number:", ticket_number
    printjob.template_print()
    time.sleep(1)