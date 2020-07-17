import requests
import subprocess
from pathlib import Path
import re

# tested with python3 and anki 2.1.22
# you need the addon anki-connect

# use pdftk to burst a PDF into single pages like so :
#   pdftk masterPDF.pdf burst
# I recommend uding "rename" package to rename the individual pages
# into something more legible, and this way the sort field contain some information like document name etc
# ex : rename 's/^pg_00/my_document_/' *.pdf


# todo :
# script that automatically uses pdftk and rename
# use enumerate instead of a stupid if
# add a time estimation
# add ocr functionnality
# add functions inspired by https://github.com/kryzar/Stupid-Serguei-Scripts/blob/master/Angif.sh
# make it so that it does all this in the same folder
# make it optionnal to store the picture
# allow to choose picture quality
# solve the css formating in the template
# parallelize the whole thing : it could be much faster : https://pymotw.com/2/multiprocessing/basics.html
        # maybe thanks to the map function : https://stackoverflow.com/questions/1704401/is-there-a-simple-process-based-parallel-map-for-python


def createBasicTemplate():
    r = requests.post('http://127.0.0.1:8765', json={
        "action": "createModel",
        "version": 6,
        "params": {
            "modelName": "PDF_per_page",
            "modelType": "basic",
            "inOrderFields": ["OnePage", "Text", "OCR"],
            "css":".card { font-family: arial; font-size: 14px; text-align: left; color: black; background-color: white; } \a\
                .title { text-align : center !important; font-size : 30px} \a\
                .col1 {width:50% ; float:left ; text-align:left}  \a\
                .col2 {width:50% ; float:right ; text-align:left }  \a\
                .container {width:100% ;  display:table }",
            "cardTemplates": [
                {
                    "Front": "{{OnePage}}",
                    "Back": '<div class="title">	Side by side comparison</div>\a\
                            <div class = "container"> \a\
                                    <div class="col1"><u><b>Repeated page :</u></b> <br> {{OnePage}} <br>##<br>{{OnePage}}</div>\a\
                                    <div class="col2"><u><b>Text content :</u></b> {{Text}} </div> \a\
                            </div>'
                    # OCR is not displayed as it is used only to find the card
                }
            ]
        }
    })
    print("Template created!")


def createImportDeck():
    r = requests.post('http://127.0.0.1:8765', json={
        "action": "createDeck",
        "version": 6,
        "params": {
            "deck": "Imported from PDF",
        }
    })
    print("Deck created!")


def sendPDFPageToAnki(PNG_name, back):
    r = requests.post('http://127.0.0.1:8765', json={
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": "Imported from PDF",
                "modelName": "PDF_per_page",
                "fields": {
                    "OnePage": str(''.join(['<img class="" src="', PNG_name,'">'])),
                    "Text": back ,
                    "OCR": "" # not yet used
                },
                "tags": [
                    "ImportedFromPDF"
                ]
            }
        }
    })
    print(r.json())


# Initialization
print("Adding Template...")
createBasicTemplate()
print("Adding destination Deck...")
createImportDeck()


# iterate over all pdfs, turn them into picture and extract text
PDF_dir="/home/glume/Downloads/temp/"
ankiMediaFolder="/home/glume/.local/share/Anki2/Main/collection.media/"

paths = Path(PDF_dir).glob('./*.pdf')
paths=sorted(list(paths)) # otherwise it's this weird generator type thingie
n=len(paths)

i=0
for PDF_path in paths:
    #if (i<1) :  #d debug
        PDF_path = str(PDF_path)

        i=i+1
        print("######################## Step : ",i,"/",n,,"  (",str(int(i)/int(n)*100) "%) #")
        

        # convert pdf to png
        PNG_path = ankiMediaFolder + PDF_path[len(PDF_dir):] + ".png"
        subprocess.run(["convert", "-density", "300","-quiet", PDF_path, PNG_path],stdout=subprocess.PIPE)

        # extract text of pdf
        PDF_text = subprocess.run(["pdftotext", "-layout","-nopgbrk","-enc","UTF-8",PDF_path, "-"],stdout=subprocess.PIPE, encoding='utf-8').stdout

        PDF_text = str(PDF_text)
        PDF_text = PDF_text.replace("\n","<br>") # tries to keep formatting in anki
        PDF_text = PDF_text.replace(" ","&nbsp;") 

        # sends card into anki
        PNG_name = str(''.join([PDF_path[len(PDF_dir):],".png"]))
        sendPDFPageToAnki(PNG_name, PDF_text)
        #print("sent!")
        print("\r\r")
