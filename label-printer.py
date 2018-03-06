#!/usr/bin/env python

###################################################
#  label-printer.py
#  Author:  N4tH4N
#  Date:    06/02/2018
#  Brief:   a python program to scrape a jobs txt file, save
#           all the parts into arrays and then print the
#           parts on the job to the brother ql-580n label printer
###################################################

import re
from brotherprint import BrotherPrint
import socket
import time
import os.path
import sys


print
print "  N4tH4N's                          "
print ".__        ___.          .__              "
print "|  | _____ \_ |__   ____ |  |             "
print "|  | \__  \ | __ \_/ __ \|  |             "
print "|  |__/ __ \| \_\ \  ___/|  |__           "
print "|____(____  /___  /\___  >____/  "
print "          \/    \/     \/  "
print "             .__        __                "
print "_____________|__| _____/  |_  ___________  "
print "\____ \_  __ \  |/    \   __\/ __ \_  __ \ "
print "|  |_> >  | \/  |   |  \  | \  ___/|  | \/  "
print "|   __/|__|  |__|___|  /__|  \___  >__|     "
print "|__|                 \/          \/         "
print
# print " |-------------------------------|"
# print " |   1) Print Labels             |"
# print " |   2) Test Mode                |"
# print " |-------------------------------|"
# print
# mode = raw_input("# Please enter an option number: ")

print_labels = True
test_mode = False

# if mode == "1":
#     print_labels = True
# elif mode == "2":
#     test_mode = True


###########################################################################
############    Defining and opening the .txt file to work on    ##########
###########################################################################

# prompting the user for the job number
user_input = raw_input("##  Enter the Job Number: ")
# combining the 'user_input' string with the extension '.txt'
input_file = user_input + ".txt"

if os.path.isfile(input_file):
    txt_file = open(input_file, "r")
    contents = txt_file.read()
    txt_file_lines = contents.splitlines()  # have to do this because python adds extra line breaks
    txt_file.close()
else:
    print
    print "   WhAt??!?!?"
    print "   That file doesn't seem to exist..."
    print "   Are you sure you exported the job from iTMS?"
    print
    sys.exit(-1)

print
print


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

###########################################################
############  Defining the customer variable  #############
###########################################################

# VARLEY BNE and VARLEY TOMAGO (SCHOOL DRIVE) use the same label template
if customer == "G H VARLEY - BNE":
    customer = "VARLEY"
elif customer == "G H VARLEY - TOMAGO (SCHOOL DRIVE)":
    customer = "VARLEY"
# VARLEY TOMAGO DEFENCE use a different label template
elif customer == "G H VARLEY - TOMAGO (McINTYRE ROAD - DEFENCE)":
    customer = "VARLEY_TOMAGO_DEFENCE"
elif customer == "TRITIUM PTY LTD":
    customer = "TRITIUM"


##################################################################
############  Creating the Client Part Number Array  #############
##################################################################

client_part_number_array = []

for i in ticket_line_number_array:
    lines_ahead_array = []
    for counter, line in enumerate(txt_file_lines, 1):
        if counter < ( i + 12 ) and counter > ( i + 2 ):
            lines_ahead_array.append(line)

    if customer == "VARLEY":
        for j, item in enumerate(lines_ahead_array):
            if j < 3 and item.find("Issue Date") >= 0:
                # going back by one line and splitting the string by {TAB}
                client_part_number_array.append(lines_ahead_array[j-1].split("\t")[1])
            elif j > 4 and item.find("Issue Date") >= 0:
                # going back by two lines
                client_part_number_array.append(lines_ahead_array[j-2])

    # TRITIUM and VARLEY TOMAGO DEFENCE get the client part number from the line below 'Part Description'
    # once it finds 'Part Description', it will look one line ahead, then split the line at the first space " "
    # and keep the first string that is there
    if customer == "TRITIUM" or customer == "VARLEY_TOMAGO_DEFENCE":
        for j , item in enumerate(lines_ahead_array):
            # tritium has their client part number in the part description field
            # looking for "Part Description" then jumping one line ahead
            if item.find("Part Description") >= 0:
                # adding "CUSTOMER LABELS" if the next line contains "CUSTOMER"
                if lines_ahead_array[j+1].split(" ")[0] == "CUSTOMER":
                    client_part_number_array.append("CUSTOMER-LABELS")
                else:
                    # one line down from "Part Description" and splitting the string with the first white space
                    client_part_number_array.append(lines_ahead_array[j+1].split(" ")[0])


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


#################################################################
#####  Arrays and Variables for VARLEY TOMAGO DEFENCE only  #####
#################################################################

if customer == "VARLEY_TOMAGO_DEFENCE":

    # starting to find the Order Number
    for i in enumerate(ticket_line_number_array):
        # only searching the first element in the ticket_line_number_array
        if i < 1:
            lines_ahead_array = []
            for counter, line in enumerate(txt_file_lines, 1):
                # only reading in lines 5 to 14 from the txt file into the array
                if counter > 4 and counter < 15:
                    lines_ahead_array.append(line)

    # searching each line for the word "Order No"
    for j, item in enumerate(lines_ahead_array):
        if item.find("Order No") >= 0:
            # the Order Number is one line below, and the third tab over
            order_no = lines_ahead_array[j+1].split("\t")[2]

    print "Order Number =", order_no
    print
    print

    # Getting the Kit Number from the USER, this changes with each order
    print "*  VARLEY - TOMAGO DEFENCE, require a kit number to be printed on each label."
    print "*  The kit number should be written on the 'CUSTOMER-LABELS' ticket."
    print "*  If there is no kit number on that ticket, see Jamie."
    print
    kit_number = raw_input("##  Please enter the Kit Number for this job: ")

    # Creating the Revision Array

    revision_array = []

    for i in ticket_line_number_array:
        lines_ahead_array = []
        for counter, line in enumerate(txt_file_lines, 1):
            if counter < ( i +  14 ) and counter > ( i + 3 ):
                lines_ahead_array.append(line)

        for j, item in enumerate(lines_ahead_array):
            if item.find("Revision") >= 0:
                # added the 'try' because you will get an IndexError if there is no revision in iTMS
                try:
                    # the revision will be one line down and the 5th tab over
                    revision_array.append(lines_ahead_array[j+1].split("\t")[4])
                except IndexError:
                    # adding an empty string to the array if there is no revision
                    revision_array.append(" ")


###############################################################
##############   Starting to print the labels   ###############
###############################################################

if print_labels == True:

    ########################################
    ####  Defining the template number  ####
    # VARLEY has a key value of 1  ( VARLEY BNE and VARLEY TOMAGO - SCHOOL DRIVE, use the same template number (1) )
    # TRITIUM has a key value of 2
    # you can check the printers web page to see the templates that are loaded onto it
    if customer == "VARLEY":
        template_number = "1"
    elif customer == "TRITIUM":
        template_number = "2"
    elif customer == "VARLEY_TOMAGO_DEFENCE":
        template_number = "3"
    ########################################

    f_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # The IP Address of the printer is 192.168.5.64 and the default port number for it is 9100
    f_socket.connect(('192.168.5.64', 9100))
    printjob = BrotherPrint(f_socket)

    printjob.template_mode()
    printjob.template_init()
    # Check the printers web page to see the template numbers
    printjob.choose_template(template_number)

    if customer == "VARLEY_TOMAGO_DEFENCE":

        # This command is sent to the printer to tell it to cut after every 5 labels
        # 5 labels fits an A4 nicely for TOMAGO DEFENCE labels
        printjob.send('^CO1050')

        for i, item in enumerate(ticket_line_number_array):

            ticket_number = job_number + "-" + str( i + 1 )

            print
            print
            print "Ticket Number:", ticket_number
            print "Client Part Number:", client_part_number_array[i]
            print "Revision:", revision_array[i]
            print "Order Number:", order_no
            print "Kit Number:", kit_number

            print
            print "Number of labels to be printed for this part:", qty_array[i]
            print

            counter = 0
            while counter < int(qty_array[i]):

                print "Printing label number", (counter +1)

                # print "Ticket Number:", ticket_number
                printjob.select_and_insert("ticket no.", ticket_number)
                # print "Client Part Number:", client_part_number_array[i]
                printjob.select_and_insert("part no.", client_part_number_array[i])
                # print "Revision:", revision_array[i]
                printjob.select_and_insert("revision no.", revision_array[i])
                # print "Order Number:", order_no
                printjob.select_and_insert("order no.", order_no)
                # print "Kit Number:", kit_number
                printjob.select_and_insert("kit no.", kit_number)

                printjob.template_print()
                time.sleep(1)
                counter += 1


    else:
        # This command is sent to the printer to tell it to cut after every 6 labels
        # 6 labels fits an A4 nicely for VARLEY BNE and TRITIUM labels
        printjob.send('^CO1060')
        for i, item in enumerate(ticket_line_number_array):
            if i < ticket_line_number_array:
                ticket_number = str(i + 1)
                ticket_number = job_number + "-" + ticket_number

            print "Ticket Number:", ticket_number
            printjob.select_and_insert("ticket no.", ticket_number)

            print "Client Part Number:", client_part_number_array[i]
            printjob.select_and_insert("part no.", client_part_number_array[i])

            print "Qty:", qty_array[i]
            printjob.select_and_insert("qty", qty_array[i])

            # command to print the template
            printjob.template_print()
            # the program will sleep for 1 second before starting the next command
            time.sleep(1)


#################################
##########  Test Mode  ##########
#################################

if test_mode == True:

    print
    print "****  Test Mode  ****"
    print "Looping through and testing all of the arrays."
    print

    for i, item in enumerate(ticket_line_number_array):
        print "Ticket Number:", job_number+"-"+str(i+1)
        print "Part Number: ", client_part_number_array[i]
        if customer == "VARLEY_TOMAGO_DEFENCE":
            print "Revision:", revision_array[i]
        print "Quantity:", qty_array[i]
        print
