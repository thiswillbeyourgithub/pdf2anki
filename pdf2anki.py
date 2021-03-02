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



import time
import requests
import subprocess
import os
import PyPDF2
import pdf2image
from pathlib import Path
from tqdm import tqdm

from joblib import Parallel, delayed
import multiprocessing


######### SETTINGS :
picture_quality=300 #default is 300
color_nb = "disabled" # default is "disabled", it's the number of colors in the picture
store_picture = "yes" #default is yes

username = "FILLME"
profile_name = "Main"
PDF_dir=f"/home/{username}/Downloads/PDF/"
ankiMediaFolder=f"/home/{username}/.local/share/Anki2/{profile_name}/collection.media/"

num_cores = max(multiprocessing.cpu_count()-1, 1)
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
    #print(str(r.json())) # to debug
    print("Finished template creation!\n")


def createImportDeck():
    r = requests.post('http://127.0.0.1:8765', json={
        "action": "createDeck",
        "version": 6,
        "params": {
            "deck": "Imported from PDF",
        }
    })
    print("Finished deck creation!\n")


def sendToAnki(JPG_name, back):
    r = requests.post('http://127.0.0.1:8765', json={
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": "Imported from PDF",
                "modelName": "PDF_per_page",
                "fields": {
                    "OnePage": str(''.join(['<img class="" src="', JPG_name,'">'])),
                    "Text": back ,
                },
                "tags": [
                    "ImportedFromPDF"
                ]
            }
        }
    })
    tqdm.write(str(r.json()))

def batch_convert(PDF_path):
        " converts single page pdf to jpg and moves them to the media folder "
        JPG_path = f"{ankiMediaFolder}{PDF_path[len(PDF_dir):]}.jpg"
        os.system(f'convert \
                -density {picture_quality} \
                {color_arg} \
                -background "#ffffff" \
                -quiet\
                {PDF_path} {JPG_path}')
        return

print("Adding Template...")
createBasicTemplate()

print("Adding destination Deck...")
createImportDeck()

paths = Path(PDF_dir).glob('./*.pdf')
paths = sorted(list(paths)) #get a list instead of a generator
#pdf_file = PdfFileReader(open(args.inputpdf, 'rb'))
#for page in pdf_file.pages:
#        PDF_text = page.extractText()

if store_picture == "yes":
    if color_nb == "disabled":
        color_arg = ""
    else:
        color_arg = f"-colors {color_nb}"
    print(f"Batch converting images + moving them to the collection using {num_cores} cores...")
    Parallel(n_jobs=num_cores)(delayed(batch_convert)(str(i)) for i in tqdm(paths))

print("Extracting text...")
for PDF_path in tqdm(paths):
        "extracts text"
        PDF_path = str(PDF_path)

        # extract text of pdf
        PDF_text = subprocess.run(["pdftotext", "-layout","-nopgbrk","-enc","UTF-8",PDF_path, "-"],stdout=subprocess.PIPE, encoding='utf-8')
        PDF_text = str(PDF_text.stdout)
        PDF_text = PDF_text.replace("\n","<br>") # tries to keep formatting in anki
        #PDF_text = PDF_text.replace(" ","&nbsp;")

        JPG_name = f"{PDF_path[len(PDF_dir):]}.jpg"
        if store_picture == "yes" :
            sendToAnki(JPG_name, PDF_text)
        else :
            sendToAnki(f"Picture not embedded : \n{JPG_name}", PDF_text)



print(f"Done! Duration = {time.process_time()}")
