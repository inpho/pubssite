#!/usr/bin/python
import cgi
import cgitb
import sys

cgitb.enable()

print("Content-Type: text/html")
print("")

try:
    from stanford_bib_single import *
except Exception as e:
    print("Error importing bibliography scraping script\n")
    print("</br>")
    print(e)
    print("</br>")
else:
    form = cgi.FieldStorage()

    print("Enter sepdir:")
    print("<form><input type=\"text\" name=\"sepdir\"></form>")

    if "sepdir" not in form:
        print("Enter something above.")
    else:
        sepdir = form.getfirst("sepdir")
        print(sepdir)
        sb = Scraped_Bib(sepdir)
        path = '\"/cgi-bin/' + sepdir + '.csv\"'
        print("<a href=" + path + ">Download</a>")
