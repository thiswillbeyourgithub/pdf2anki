# all help welcome, this is very functionnal but lots of small things could be done to make it a thousand time better, check out the todolist
# pdf2anki
short version : load pdf into anki, page by page, with text included, planned OCR


## how does it work / how to use?
***First read this page carefully. Please make sure you understand that right now anki's servers are free to use but they were not designed for thins kind of usage. PDFs like this can easily be millions of times heavier than simple text based cards. If you use this script be reasonnable and use another anki profile, this way it will not be automatically synced with the servers. Thank you.***


Use `pdftk` to *burst* a pdf into single pages, use rename to batch rename the pages, for example `rename 's/^pg_9/PDF_lesson_cryptography_/' pg_0*` then set up the "settings" section of pdf2anki (especially the directory where the pdf should be found) then launch the script : `python3 ./pdf2anki.py` or with `./pdf2anki.py` after making it executable.
* It then uses `convert` to take the text from the pdf.
* then manually moves the pdf pages into the media folder of anki
* Anki-connect addon is then used to send cards to anki that contains the single page + the text
* this allows to search pdfs using multiple words 

## requirements
I use python3 and anki 2.1.22, tested it works. Don't hesitate to open an issue if this stops working. I tested this on ubuntu 18.04 and I expected
* pdftk
* convert
* anki-connect (addon for anki)

## Python Installation
`pip install -r requirements.txt`


## notes :
* please don't use this on super large pdf for no reason, or if you do : don't sync it, the creator of anki should not have to pay extra bandwidth for this not intended use so don't forget the "delete media" button.
* **why did I make this?** The idea was to make my PDF lessons searchable. I never found a way to look for a page in a pdf using several keywords at the same time. So I decided to import each page into anki and use it like that. The ocr part is just that sometimes there are pictures in the page and some data could be extracted by simply 'ocr'ing the page and adding it to a field.
* you should install this addon [highlight search results in the browser](https://ankiweb.net/shared/info/225180905)
* the way my code works, images are manually moved from the pdf folder to the anki media folder. I think anki-connect has a more elegant way of doing this but I didn't have the time to do it at the time. If you find a better way don't hesitate to do a PR. My method probably doesn't translate well to other OSs.
* to automate the bursting of the file you can use the following :

        file=$1
        name=${file%%.pdf}
        pdftk $file burst output ${name}_page%d.pdf

## Acknowledgment : 
* shell script thanks to `Quentin Dupré`


## todo (most are very basic and quick, I mostly lack time so don't hesitate to help)
* write a better howto
* add a demo picture
* make it optionnal to store the picture
* allow to specify picture quality
    * and grayscale or not, this could really make filesize go down
* shell script that automate the pdftk + rename part
    * make it so that it uses only one folder for the whole thing
    * make it take the pdf as an argument
* **add OCR functionnality using PyTesseract or something like that**
* clean up the code, inspired by  by https://github.com/kryzar/Stupid-Serguei-Scripts/blob/master/Angif.sh
    * also : use enumerate unstead of a stupid if
* solve the css formating template (in the template window in anki, the css is not parsed correctly)
* add time to complete estimation
* parallelize the whole thing : it should be much much faster : https://pymotw.com/2/multiprocessing/basics.html
    * maybe thanks to the map function : https://stackoverflow.com/questions/1704401/is-there-a-simple-process-based-parallel-map-for-python
* when the technology is there : add OCR from written notes.

