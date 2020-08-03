with open ('markdownrows.txt') as f:
    content = f.readlines()

rows = []

cells = content[0].split('|')
cells = ['<th style="text-align:center">{}</th>'.format(cell.strip()) for cell in cells]
rows.append(cells)

for c in content[2:]:
    cells = c.split('|')
    cells = ['<td style="text-align:center">{}</td>'.format(cell.strip()) for cell in cells]
    rows.append(cells)

#htmltable.txt contains the html table rows
file = open('htmlrows.txt', 'w+')
file.write('<table>')
for r in rows:
    file.write('<tr>')
    for c in r:
        file.write('{}'.format(c))
    file.write('</tr>')
file.write('</table>')
file.close()