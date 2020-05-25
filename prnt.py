import cups
from xhtml2pdf import pisa
#from jinja2 import Template  #https://qna.habr.com/q/518464
import argparse
import barcode
from barcode.writer import ImageWriter

parser = argparse.ArgumentParser()
parser.add_argument("-p", action="store_true", help="Печать штрихкода")
parser.add_argument("-n", type=str, help="Номер штрихкода для печати")
parser.add_argument("-c", type=int, help="Количество нужных копий штрихкода")
parser.add_argument("-f", type=str, action="store",default='html',help="Имя файла для сохранения,по умолчанию *.html, можно сохранить в *.pdf так -p pdf")
parser.add_argument("--text", type=str, help="Текст, подставится под кодом вместо цифр, небольше 24знаков")

args = parser.parse_args()
p = args.p
n = args.n
c = args.c
f = args.f
text = args.text

print('p = ',p)
print('n = ',n)
print('c = ',c)
print('f = ',f)
print('text = ',text)
print('type text = ',type(text))

if type(n) is None:
    exit() 
else:
    print(len(n))
    if len(n) != 12:
        print('Это блять нихуя ни EAN13 штрихкод! нужно токо 12 цифр! небольше неменьше!!!')
    #    exit()
    else:
        print('ШтрихКот ok!')

#EAN = barcode.get_barcode_class('ean13')
#ean = EAN(u'123456789123',writer=ImageWriter())
try:
	ean = barcode.get('ean13', n, writer=ImageWriter())
	ean.default_writer_options['text_distance'] = 2 
	ean.default_writer_options['font_size'] = 18
	ean.default_writer_options['quiet_zone'] = 6.5
#	ean.default_writer_options['background'] = 'red'
	### назначаем текст если опция тру
	if text is not None:
	    ean.default_writer_options['write_text'] = False 
	    ean.default_writer_options['text'] = text
	    if len(text) > 23:
	    	exit('Текста должно быть не больше 23 символа включая пробелы!!!')
#	    else:	
#	    	print('text OK:',text)
	fname = ean.save('barcode')

except barcode.errors.NumberOfDigitsError:
	exit()

xhtml = '''<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
  <title></title>
  <style type="text/css">
    table {border-collapse: collapse}
    table,td {border: 1px solid black; padding:0;}
    td {width:147px;}
    img {display:block; margin-left:auto; margin-right:auto; width:147px;}
  </style>
</head>
<body>
<table>\n'''

### расчёт количества рядов и остатков в ряду где меньше 5
rowsc = c//5
cellc = c - rowsc*5
### если остаток не ноль то для него накинуть ищо рядок
if cellc != 0:
    rowsc += 1
    
print('rowsc = ',rowsc)
print('cellc = ',cellc)
#exit()

for i in range(rowsc):
    xhtml += '  <tr>\n'
    if cellc != 0 and i == rowsc-1:
        cells = cellc
    else:
        cells = 5
    for ii in range(cells): # это 13 рядов по 4 баркода, 13 строк какраз А4, width='167' в ряду 4шт width='147' в ряду 5шт 167 вроде читается лучше
        xhtml += '    <td><img src="barcode.png"></td>\n'
#        xhtml += '    <td align="center" width="107" height="88"><img src="barcode.png" width="167" height="88"></td>\n'
#        xhtml += '<td><img src="barcode.png" width="167" height="88"></td>'+'\n'
    xhtml += '  </tr>\n'

xhtml += '</table>\n</body>\n</html>'

### Сохраняем в хтмл 
if f == 'html':
    with open('barcode.html', 'w', encoding='utf-8') as f:
        f.write(xhtml)

#outfilename = "print.pdf"
#resultfile = open(outfilename,'w+b')
pdf = pisa.CreatePDF(xhtml, dest=open('print.pdf','w+b'))
if not pdf.err:
    pdf.dest.close()

### Печать файла
def hwprintfile():
    try:
        conn = cups.Connection()
    except RuntimeError:
        exit()
    ### Получаем список всех принтеров, подключенных к компьютеру
    printers = conn.getPrinters()
    for printer in printers: 
        # Выводим имя принтера в консоль
        print(printer, printers[printer]["device-uri"])

    ### Получаем первый принтер со списка принтеров
    printer_name = list(printers.keys())[0]
    #printer = conn.getDefault()
    #print(printer)

    ### Этим мы включаем печать
    conn.printFile(printer_name, 'print.pdf','',{})
    
if p is True:
    hwprintfile()

