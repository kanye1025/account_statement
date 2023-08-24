from openpyxl import Workbook,load_workbook
from openpyxl.worksheet.pagebreak import Break

wb = load_workbook("data/张凌玮.xlsx",read_only=False)
ws = wb.active
#row_number = 20  # 需要插入分页符的行号
#page_break = Break(id=row_number)  # 创建分页对象
#ws.page_breaks.append(page_break)  # 插入分页符
ws.page_breaks