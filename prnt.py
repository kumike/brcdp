import cups
from xhtml2pdf import pisa
from jinja2 import Template
import argparse
import barcode
from barcode.writer import ImageWriter


parser = argparse.ArgumentParser(description='A tutorial of argparse!')
parser.add_argument("-p", action="store_true")
parser.add_argument("-n", type=str, help="Номер штрихкода для печати")
parser.add_argument("-c", type=int, help="Количество нужных копий штрихкода")
parser.add_argument("-f", type=str, action="store",default='html',help="Имя файла для сохранения,по умолчанию *.html, можно сохранить в *.pdf так -p pdf")
parser.add_argument("--text", type=str, help="Текст, подставится под кодом вместо цифр, небольше 24знаков")


args = parser.parse_args()
p = args.p
n = args.n
c = args.c
f = args.f
#text = args.text

print('p = ',p)
print('n = ',n)
print('c = ',c)
print('f = ',f)
#print('text = ',text)

if type(n) is None:
    exit() 
else:
    print(len(n))
    if len(n) != 3:
        print('Это блять нихуя ни EAN13 штрихкод! нужно токо 12 цифр! небольше неменьше!!!')
    #    exit()
    else:
        print('ШтрихКот ok!')

#EAN = barcode.get_barcode_class('ean13')
#ean = EAN(u'123456789123',writer=ImageWriter())

ean = barcode.get('ean13', n, writer=ImageWriter())
ean.default_writer_options['text_distance'] = 2 
ean.default_writer_options['font_size'] = 18
ean.default_writer_options['quiet_zone'] = 6.5
fname = ean.save('barcode')



xhtml = '''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
        <title></title>
    <style type="text/css">
        table {border: 1px solid black}
    </style>
</head>
<body lang="ru-RU">'''

i = 0
while i <= c: # это 13 рядов по 4 баркода, 13 строк какраз А4
    xhtml += '<table><tr><td><img src="barcode.png" width="167" height="88"></td>'+'\n'
    xhtml += '<td><img src="barcode.png" width="167" height="88" border="0"></td>'+'\n'
    xhtml += '<td><img src="barcode.png" width="167" height="88" border="0"></td>'+'\n'
    xhtml += '<td><img src="barcode.png" width="167" height="88" border="0"></td></tr></table>'+'\n'
    i += 1
xhtml += '</body></html>'

if f == 'html':
    with open('barcode.html', 'w', encoding='utf-8') as f:
        f.write(xhtml)

#print(xhtml)

outfilename = "print.pdf"
resultfile = open(outfilename,'w+b')
pdf = pisa.CreatePDF(xhtml, dest=resultfile)
if not pdf.err:
    pdf.dest.close()

try:
    conn = cups.Connection()
except RuntimeError:
    exit()
# Получаем список всех принтеров, подключенных к компьютеру
printers = conn.getPrinters()
for printer in printers: 
# Выводим имя принтера в консоль
    print(printer, printers[printer]["device-uri"])

# Получаем первый принтер со списка принтеров
printer_name = list(printers.keys())[0]
##printer = conn.getDefault()
##print(printer)

# Этим мы включаем печать
def hwprintfile():
    conn.printFile(printer_name, 'print.pdf','',{})
    
if p is True:
    hwprintfile()


