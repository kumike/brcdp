import argparse
import barcode
from barcode.writer import ImageWriter
from xhtml2pdf import pisa
import os
#import pisa ### патченная для запуска pdf и в линуксе.. было только для мака и винды.. дописал.. над автору заслать..
import cups
#from jinja2 import Template  #https://qna.habr.com/q/518464

parser = argparse.ArgumentParser()
parser.add_argument("-p", action="store_true", help="Печать штрихкода")
parser.add_argument("-g", action="store_true", help="Генерация штрихкодов")
parser.add_argument("-n", type=str, help="Номер штрихкода для печати")
parser.add_argument("-c", type=int, help="Количество нужных копий штрихкода")
#parser.add_argument("-f", type=str, action="store",default='html',help="Имя файла для сохранения,по умолчанию *.html, можно сохранить в *.pdf так -p pdf")
parser.add_argument("--text", type=str, help="Текст, подставится под кодом вместо цифр, небольше 24знаков")
parser.add_argument("--view", action="store_true", help="Предпросмотр pdf, откроецца в просмотрщике по умолчанию")

args = parser.parse_args()
p = args.p
n = args.n
c = args.c
#f = args.f
f = False
g = args.g
text = args.text
view = args.view

print('p = ',p)
print('n = ',n)
print('c = ',c)
print('f = ',f)
print('g = ',g)
print('text = ',text)

def makecodes(*args):
    sufix = 0
    for i in args[0]:
        try:
            ean = barcode.get('ean13', str(i), writer=ImageWriter())
            ean.default_writer_options['text_distance'] = 2 
            ean.default_writer_options['font_size'] = 18
            ean.default_writer_options['quiet_zone'] = 6.5
           #ean.default_writer_options['background'] = 'red'
            ### назначаем текст если опция тру
            if text is not None:
                ean.default_writer_options['write_text'] = False 
                ean.default_writer_options['text'] = text
                if len(text) > 23:
                    exit('Текста должно быть не больше 23 символа включая пробелы!!!')
            fname = ean.save('barcode0'+str(sufix))
            sufix += 1
        except barcode.errors.NumberOfDigitsError:
                exit('Это блять нихуя ни EAN13 штрихкод! нужно токо 12 цифр! небольше неменьше!!!')
        except barcode.errors.IllegalCharacterError:
                exit('EAN13 штрихКот может содержать только цифрЫ!!не больше 12 знаков!!')

if n is None: 
    exit('Опция -n абязательна! бо шош мне бля генерировать?')
else:
    codelist = [n]
    makecodes(codelist)

if g:
    if c is None:
        c = 70 ### 70 баркодов какраз страница А4 по 5 кодов в ряду
    #if p is False:
     #   p = True ###  и в принудиловку включаем печать если не включено при генерации кодов 
    codelist = [int(n)+i for i in range(c)]
    makecodes(codelist)

### если не задано количество штрихкодов, то по умолчанию отпечатать ток один.
if c is None:
    c = 1

### Генерируем html разметку
xhtml = '''<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
  <title></title>
  <style type="text/css">
    table {border-collapse: collapse;/* Убираем двойные границы между ячейками */}
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
### Генерация таблицы с баркодами
sufix = 0
for i in range(rowsc):
    xhtml += '  <tr>\n'
    if cellc != 0 and i == rowsc-1:
        cells = cellc
    else:
        cells = 5
    for ii in range(cells): ### 13 рядов по 4 кода = А4, width='167' в ряду 4шт, width='147' в ряду 5шт, 167 вроде читается лучше, width='167' height='88' 
        xhtml += '    <td><img src="barcode0'+str(sufix)+'.png"></td>\n'
        if g:
            sufix += 1
    xhtml += '  </tr>\n'
#xhtml += '<div><pdf:barcode value="BARCODE TEXT COMES HERE" type="code128" humanreadable="1" align="baseline" /></div></table>\n</body>\n</html>'
xhtml += '</table>\n</body>\n</html>'

### Генерируем pdf из html разметки
pdf = pisa.CreatePDF(xhtml, dest=open('print.pdf','w+b'))
if not pdf.err:
    pdf.dest.close()

if view:
    if p: ### если включен предпросмотр то выключаем печать в принудилку
        p = False
    os.system('xdg-open print.pdf')
    #pisa.startViewer('print.pdf') ### заработало.. там не было написано для линя ток к маку и винде.. дописал.. заработало

### Сохраняем в хтмл TODO доделать толковое сохранение всей веб страницы и её ресурсов.
if f == 'html':
    with open('barcode.html', 'w', encoding='utf-8') as f:
        f.write(xhtml)

### Печать файла TODO доделать выбор принтера и по возможности печати в винде..
def hwprintfile():
    try:
        conn = cups.Connection()
    except RuntimeError:
        exit()
           
    ### Выводим имя принтера в консоль
    #for printer in printers: 
         #print(printer, printers[printer]["device-uri"])
    
    ### получаем принтер установленный по умолчанию.. его может и не быть установлено..
    default_printer = conn.getDefault()
    if default_printer is None:
    	### Получаем список всех принтеров, подключенных к компьютеру
        printers = conn.getPrinters()
	    ### Получаем первый принтер со списка принтеров
        if len(printers) > 0:
            printer_name = list(printers.keys())[0]
        else:
            exit('Принтер блядь включи сначала!... бо нихуя нима принтера чёйто..')
    else:
        printer_name = default_printer

    #print(printer)

    ### Этим мы включаем печать
    conn.printFile(printer_name, 'print.pdf','',{})
    print('Пэчатайу в этот принтер:', printer_name)
    
if p:
    hwprintfile()
