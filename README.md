# MobilePDFScanner

## About
This is a little week-end project that I imagined when I had to scan a document via email but I didn't have a scanner at home. 
I decided to build a small program that would run on my computer :computer: to properly scan a document to a PDF file that I could then send via email.
It basically tries to find the document in the image, crop it/ transform it accordingly and save it as a PDF, so I came basically came up with a portable scanner !

** FEEL FREE TO USE IT **

## Requirements
I used basic operations of **OpenCV**, **Numpy** as well as **PIL** libraries to manage images.

## Usage
Go to the repo folder and run the *main.py* with the path of the photograph to process. 
You can also choose the output location and name.
```
$ python main.py ./photos/20210424_184347.jpg ./output.pdf
```
And then just follow the terminal indications and answer !

It first tries to automatically find the sheet by a little of image processing.
If the corners are placed correctly but not in the right place, you can rotate them around your sheet (Command : 'c' when asked).
If the solution found doesn't match your expectations, you can still choose to place the corners manually on the OpenCV window following the order that is proposed to you.
In the end, a PDF file is saved at the indicated location. :smiley:

## Improvements possible
Some features could be added to this useful program :
- Allow to move a point without having to start again from scratch
- Show the line between the previous point and the mouse to place easily the next one (and visualize the parts that will be on the PDF document.

## Notes
I wrote this program on MacOS Big Sur, I didn't test it on Windows or Linux but there shouldn't be too much trouble.