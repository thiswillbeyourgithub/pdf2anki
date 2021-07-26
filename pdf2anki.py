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


import subprocess
import argparse
import re
import multiprocessing

import requests
import pdf2image
from tqdm import tqdm
import PyPDF2

import time
start = time.time()

parser = argparse.ArgumentParser()
parser.add_argument("-u",
                    "--username",
                    help="The home folder name as in /home/USER/anki_path",
                    dest="username",
                    metavar="USERNAME")
parser.add_argument("-f",
                    "--PDF",
                    help="Path to the pdf you want to add to anki",
                    dest="PDF",
                    metavar="file.pdf")
args = parser.parse_args().__dict__

if args['PDF'] is None:
    print("No PDF were given\nExiting.")
    raise SystemExit()


# SETTINGS :
picture_DPI             =  200    # default  is  200
bw                      =  False  # store    as  black  and  white      or  not
add_image               =  True   # default  is  True
unix                    =  True   # on  unix,  use  pdftotext  to  preserve  layout,  otherwise  use  PyPDF2  but  text  extraction  is  worse
disable_multithreading  =  True   # if set to False, can lead to a bug

anki_profile = "Main"
ankiMediaFolder = f"/home/{args['username']}/.local/share/Anki2/" +\
        f"{anki_profile}/collection.media/"

num_cores = max(multiprocessing.cpu_count()-1, 1)
batch_size = 50  # for pdf2image
#########


def createBasicTemplate():
    r = requests.post('http://127.0.0.1:8765', json={
        "action": "createModel",
        "version": 6,
        "params": {
            "modelName": "PDF_per_page",
            "inOrderFields": ["DocumentPage", "Text"],
            "css": " .card {font-family: arial; font-size: 14px; text-align: left; color: black; background-color: white;}\n\
                    .title {text-align : center !important; font-size : 30px} \n\
                    .col1 {width:50% ; float:left ; text-align:left}\n\
                    .col2 {width:50% ; float:right ; text-align:left}\n\
                    .container {width:100% ;  display:table }\n",
            "cardTemplates": [
                {
                    "Front": "{{DocumentPage}}",
                    "Back": '<div class="title"> Side by Side </div>\n\
                            <div class = "container"> \n\
                                    <div class="col1"><u><b>Repeated page :</u></b> <br><br> {{DocumentPage}} <br>##<br>{{DocumentPage}}</div>\n\
                                    <div class="col2"><u><b>Text content :</u></b> <br><br> {{Text}} </div> \n\
                            </div>'
                }
            ]
        }
    })
    #print(str(r.json()))  # to debug
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
    if add_image is True:
        front = f'<img class="" src="{JPG_name}">'
    else:
        front = f"{JPG_name} (not embedded)"

    r = requests.post('http://127.0.0.1:8765', json={
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": "Imported from PDF",
                "modelName": "PDF_per_page",
                "fields": {
                    "DocumentPage": front,
                    "Text": back,
                },
                "tags": [
                    "Imported_From_PDF"
                ]
            }
        }
    })
    tqdm.write(str(r.json()))


print("Adding Template...")
createBasicTemplate()

print("Adding destination Deck...")
createImportDeck()


PDF_file = PyPDF2.PdfFileReader(open(args['PDF'], 'rb'))
PDF_name = str(args['PDF'].split("/")[-1])
if add_image is True:
    print(f"Extracting pages from {PDF_name}...\n")

    def JPG_name_gen():
        for i in range(len(PDF_file.pages)):
            yield f"{PDF_name}"

    def run_p2i(x, y):
        pdf2image.convert_from_path(args['PDF'],
                dpi            = picture_DPI,
                output_folder  = ankiMediaFolder,
                fmt            = "jpg",
                first_page     = x,
                last_page      = y,
                jpegopt={ "quality":      80,
                          "progressive":  True,
                          "optimize":     True },
                thread_count  = num_cores,
                transparent   = False,
                single_file   = False,
                size          = None,
                grayscale     = bw,
                output_file   = JPG_name_gen())

    if disable_multithreading is True:
        num_cores = 1
    length = len(PDF_file.pages)

    if length < batch_size:
        x = 1
        y = length
        run_p2i(x, y)
    else:
        try:
            x = 1
            y = batch_size
            z = 0
            while y <= length+batch_size:
                print(f"Currently at page #{z*batch_size}/{length}...")
                run_p2i(x, min(y, length))
                x = y
                y += batch_size
                z += 1
        except OSError as err:
            print(50*"#")
            print(50*"#")
            print(f"ERROR {err}")
            print("This usually happens to me because of multithreading over large files.")
            print("Retry while setting disable_multithreading to True")
            print("Or just retry without changing anything, I know it's so weird")
            print("Exiting.")
            print(50*"#")
            print(50*"#")
            raise SystemExit()


print("Extracting text...\n")

if unix is True:
    print("Running on unix, using pdftotext to extract text (better layout preservation)\n")
if unix is False:
    print("Not running on unix, using pypdf2 to extract text (worse layout preservation)\n")

i = 0
width = len(str(len(PDF_file.pages)))
for page in tqdm(PDF_file.pages):
    i += 1
    if unix is False:
        PDF_text = page.extractText()
        PDF_text = re.sub(r"\n+", "<br>", PDF_text)
        PDF_text = re.sub(r"<br>\s+<br>", "<br>", PDF_text)
    if unix is True:
        PDF_text = subprocess.run(["pdftotext", "-f", str(i), "-l",
                                    str(i), "-layout", "-nopgbrk",
                                    "-enc", "UTF-8", args['PDF'], "-"],
                             stdout=subprocess.PIPE, encoding='utf-8')
        PDF_text = PDF_text.stdout.replace("\n", "<br>")
    sendToAnki(f'{PDF_name}-{int(i):0{width}d}.jpg', PDF_text)

print(f"Done!\nDuration = {round(time.time() - start,1)}s")
