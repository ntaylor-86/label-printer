# Label-Printer
A python script that scans Job tickets that have been exported from iTMS into a .txt format. Once the job has been scanned it saves all the relevant data into different arrays. It then establishes a connection to the Brother QL-580N label printer and prints off the customers labels.

## Getting Started

You will need a .txt file for the script to scrape all the information from. In iTMS, open Jobs (5), Print Job Ticket (3), enter the job number, click on print, choose Number. This will open the iTMS Print Preview, click on Export, choose Text as the file type and save the .txt file in the same location as the shell script.

### Prerequisites

You will need Python 2.7, pip and the python library "python-brotherprint"

https://github.com/fozzle/python-brotherprint

Many thanks to fozzle for this :D



```
python-brotherprint

$ sudo pip install brotherprint
```

### Installing

Copy the script to your home directory preferably its own folder and make the script executable

```
Change into the directory where the script is located,
$ cmod +x label-printer.py
```

### Runnings the Script

Once you have exported a job into a .txt format you can now run the script

replace 'jobNumber.txt' with the file you exported from iTMS

```
Change into the directory where the script is located,
$ python label-printer.py jobNumber.txt
```
