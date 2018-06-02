#!/usr/bin/python
import cgi
import cgitb
import sys

cgitb.enable()

fileName = ''
f = cgi.FieldStorage()
for i in f.keys():
    if i=='filename':
        fileName = str(f[i].value)

if (not fileName == '') and (fileName[-4:] == '.txt' or fileName[-4:] == '.csv'):
    path = 'bibs/' + fileName
    try:
        fn = open(path, 'rb')
    except Exception as e:
        print("Content-Type: text/html")
        print("")
        print(e)
        print("</br>")
    else:
        print("Content-Type: text/plain;")
        print("Content-Disposition: attachment; filename=" + fileName)
        print("")
        while True:
            data = fn.read(4096)
            sys.stdout.write(data)
            if not data:
                break
