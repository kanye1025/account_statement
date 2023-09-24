from split_table.pdf_table_recog import PDFTableRecog
from split_table.excel_table_recog import ExcelTableRecog
import os
from io import BytesIO
class TableRecog:
    def __init__(self, file_path,byte = None):
        _,ext = os.path.splitext(file_path)
        if ext == '.pdf':
            if byte:
                self.recog = PDFTableRecog(BytesIO(byte))
            else:
                self.recog = PDFTableRecog(file_path)
        elif ext in ('.xls','.xlsx'):
            self.recog = ExcelTableRecog(file_path,byte)
        else:
            raise Exception(f"wrong file ext {ext}")
    def get_table_data(self):
        return self.recog.get_table_data()
    
    
if __name__ =="__main__":
    
    file_path  = 'data/input/1672046917570_1364021.pdf'
    from tools.embeding_tool import *
    EmbedingToolBasic.init()
    EmbedingTool.init()
    obj = TableRecog(file_path).get_table_data()
    print(obj)
    