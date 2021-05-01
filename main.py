# -*- coding: utf-8 -*-
"""
Created by Jean-lou Quetin

24/04/2021
"""

import sys
import cv2
import os
from PdfManager import PDFSaver


if __name__ == '__main__':
    
    if len(sys.argv) <2:
        args = "Arguments are :\n"
        imloc = "- Image location : for instance './photos/test.jpg'\n"
        outloc = "- Ouput location/name : for instance 'out.pdf'"
        print(args+imloc+outloc)
        exit()

    orig = cv2.imread(sys.argv[1])
   
    if len(sys.argv) > 2:
        pdf_path_name = os.path.join(os.path.abspath(os.path.dirname(__file__)), sys.argv[2])
    else:
        pdf_path_name =  os.path.join(os.path.abspath(os.path.dirname(__file__)), r'out.pdf')

    pdfCreator = PDFSaver()
    res = pdfCreator.createPDF(orig)
    pdfCreator.save_to_pdf(pdf_path_name, res)

