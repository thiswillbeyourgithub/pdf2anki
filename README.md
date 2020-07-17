# pdf2anki
short version : load pdf into anki, page by page, with text included, planned OCR


## how does it work?
Use `pdftk` to *burst* a pdf into single pages, use rename to batch rename the pages, for example `rename 's/^pg_9/PDF_lesson_cryptography_/' pg_0*` then set up the "settings" section of pdf2anki (especially the directory where the pdf should be found) then launch the script : `python3 ./pdf2anki.py`
    * It then uses `convert` to take the text from the pdf.
    * then manually moves the pdf pages into the media folder of anki
    * Anki-connect addon is then used to send cards to anki that contains the single page + the text
    * this allows to search pdfs using multiple words 

## requirements
I use python3 and anki 2.1.22, tested it works. Don't hesitate to open an issue if this stops working.
    * pdftk
    * convert
    * anki-connect (addon for anki)


## notes :
    * please don't use this on super large pdf for no reason, or if you do : don't sync it, the creator of anki should not have to pay extra bandwidth for this not intended use so don't forget the "delete media" button.


## todo (most are very basic and quick, I mostly lack time so don't hesitate to help)
    * shell script that automate the pdftk + rename part
        * make it so that it uses only one folder for the whole thing
        * make it take the pdf as an argument
    * **add OCR functionnality using cuneiform or something like that**
    * clean up the code, inspired by  by https://github.com/kryzar/Stupid-Serguei-Scripts/blob/master/Angif.sh
    * make it optionnal to store the picture
    * allow to specify picture quality
    * solve the css formating template (in the template window in anki, the css is not parsed correctly)
    * use enumerate unstead of a stupid if
    * add time to complete estimation
    * parallelize the whole thing : it should be much much faster : https://pymotw.com/2/multiprocessing/basics.html
        * maybe thanks to the map function : https://stackoverflow.com/questions/1704401/is-there-a-simple-process-based-parallel-map-for-python

