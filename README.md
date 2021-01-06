# all help welcome, this is very functionnal but lots of small things could be done to make it a thousand time better, check out the todolist
# pdf2anki
*TLDR : load pdf into anki, page by page, with text included. It **doesn't** OCR text, it just copies the text from the pdf. If your PDF doesn't include text, check out [AnkiOCR](https://ankiweb.net/shared/info/450181164).*


## how does it work ?
***First read this page carefully. Please make sure you understand that right now anki's servers are free to use but they were not designed for thins kind of usage. PDFs like this can easily be millions of times heavier than simple text based cards. If you use this script be reasonnable and use another anki profile, this way it will not be automatically synced with the servers. Thank you.***


* Use `pdftk` to *burst* a pdf into single pages, use rename to batch rename the pages, for example `rename 's/^pg_9/PDF_lesson_cryptography_/' pg_0*` then set up the "settings" section of pdf2anki (especially the directory where the pdf should be found) then launch the script : `python3 ./pdf2anki.py` or with `./pdf2anki.py` after making it executable.
* It then uses `convert` to take the text from the pdf.
* then manually moves the pdf pages into the media folder of anki
* Anki-connect addon is then used to send cards to anki that contains the single page + the text
* this allows to search pdfs using multiple words 


## How to use ?
* put your pdf into a folder
* run in a terminal `pdftk largePDF.pdf burst`
* remove the large pdf file to only keep the "single page" files
* run `rename 's/^pg_0/My_TITLE_/' folder/path/pg.pdf`, this will be the header of your card
* change the path in the script to what corresponds to your setup
* run `python3 ./pdf2anki.py` (or in my case `python3.6`)
* if you have any issue, notify me by openning an issue on github. Try to uncomment the debug line to see the output `r.json()`.

## requirements
I use python3 and it works at least in anki 2.1.33, last time I checked. Don't hesitate to open an issue if this stops working. I tested this on ubuntu 18.04 but the code is not yet compatible on other OS, the code needs to be changed because for the moment you need the following unix executable :
* pdftk
* convert
You also need this anki addon :
* anki-connect

## Python Installation
`pip install -r requirements.txt`


## notes :
* If you want to use it but your PDF doesn't include text and is not written by hand, you will probably be interested in the addon [AnkiOCR](https://ankiweb.net/shared/info/450181164). Just run it after importing your pdf using this script. It might take a long time so check its settings to use multithreading correctly.
* please don't use this on super large pdf for no reason, or if you do : don't sync it, the creator of anki should not have to pay extra bandwidth for this not intended use so don't forget the "delete media" button.
* **why did I make this?** The idea was to make my PDF lessons searchable. I never found a way to look for a page in a pdf using several keywords at the same time. So I decided to import each page into anki and use it like that. The ocr part is just that sometimes there are pictures in the page and some data could be extracted by simply 'ocr'ing the page and adding it to a field.
* you should consider installing this addon to find text more easily : [highlight search results in the browser](https://ankiweb.net/shared/info/225180905)
* the way my code works, images are manually moved from the pdf folder to the anki media folder. I think anki-connect has a more elegant way of doing this but I didn't have the time to do it at the time. If you find a better way don't hesitate to do a PR. My method probably doesn't translate well to other OSs.
* to automate the bursting of the file you can use the following but don't forget that the number of cards added corresponds to the number of pages you have to add :

```
file=$1
name=${file%%.pdf}
pdftk $file burst output ${name}_page%d.pdf
```

## Acknowledgment : 
* shell script thanks to `Quentin Dupré`


## todo (most are very basic and quick, I mostly lack time so don't hesitate to help)
* stop using convert and pdftk and use something like this instead that works on all OSs https://www.roytuts.com/convert-pdf-to-image-using-python/ + https://github.com/adietz/PdfBurst/blob/master/burst.py
* write a better howto
* add a demo picture
* check if a card has already been imported earlier in the loop 
* make it optionnal to store the picture, the text could be enough and faster
* allow to specify picture quality
    * and grayscale or not, this could really make filesize go down
* clean up the code, inspired by  by https://github.com/kryzar/Stupid-Serguei-Scripts/blob/master/Angif.sh
    * also : use enumerate unstead of a stupid if
* parallelize the whole thing : it should be much much faster : https://pymotw.com/2/multiprocessing/basics.html
    * maybe thanks to the map function : https://stackoverflow.com/questions/1704401/is-there-a-simple-process-based-parallel-map-for-python
* when the machine learning technology is there : add OCR from written notes.
* solve the css formating template (in the template window in anki, the css is not parsed correctly)

