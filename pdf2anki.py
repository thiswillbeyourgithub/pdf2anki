"""
Copyright (c) 2020 the pdf2anki team

This file is part of pdf2anki.

    pdf2anki is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    pdf2anki is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with pdf2anki.  If not, see <https://www.gnu.org/licenses/>.
"""



import requests
import subprocess
import re
from pathlib import Path
from tqdm import tqdm

# tested with python3 and anki 2.1.33
# you need the addon anki-connect

# use pdftk to burst a PDF into single pages like so :
#   pdftk masterPDF.pdf burst
# I recommend uding "rename" package to rename the individual pages
# into something more legible, and this way the sort field contain some information like document name etc :
#   rename 's/^pg_00/my_document_/' *.pdf
# don't forget to remove the large pdf from the folder to only import the single page pdf


######### SETTINGS :
username = "FILLME"
profile_name = "Main"
#
PDF_dir=f"/home/{username}/Downloads/temp/"
ankiMediaFolder=f"/home/{username}/.local/share/Anki2/{profile_name}/collection.media/"
######### 


def createBasicTemplate():
    r = requests.post('http://127.0.0.1:8765', json={
        "action": "createModel",
        "version": 6,
        "params": {
            "modelName": "PDF_per_page",
            "inOrderFields": ["OnePage", "Text"],
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
                }
            ]
        }
    })
    #print(str(r.json())) # debug in case of error
    print("Finished template creation!")
    print("")


def createImportDeck():
    r = requests.post('http://127.0.0.1:8765', json={
        "action": "createDeck",
        "version": 6,
        "params": {
            "deck": "Imported from PDF",
        }
    })
    print("Finished deck creation!")
    print("")


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
                },
                "tags": [
                    "ImportedFromPDF"
                ]
            }
        }
    })
    tqdm.write(str(r.json()))


####### Initialization
print("Adding Template...")
createBasicTemplate()
print("Adding destination Deck...")
createImportDeck()
####### 


####### Main :
paths = Path(PDF_dir).glob('./*.pdf')
paths = sorted(list(paths)) # otherwise it's this weird generator type thingie

for PDF_path in tqdm(paths):
        PDF_path = str(PDF_path)

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
