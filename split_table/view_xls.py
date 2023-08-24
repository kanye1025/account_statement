import  xlrd
data  = xlrd.open_workbook("data/张凌玮.xlsx")

for table_index,table in enumerate(data.sheets()):
    print(f"page {table_index}---")
    for i in range(table.nrows):
        col = list()
        for j in range(table.ncols):
            value = str(table.cell_value(i, j))
            if value:
                col.append(value)
        col = ','.join(col)
        print(col)