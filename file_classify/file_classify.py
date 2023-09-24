from pdf_table_recog import PDFTableRecog
from excel_table_recog import ExcelTableRecog
from tools.embeding_tool_table import EmbedingToolTable
import os
from io import BytesIO

class FileClassify:
    def __init__(self,file_path,byte):
        _, ext = os.path.splitext(file_path)
        if ext == '.pdf':
            if byte:
                self.recog = PDFTableRecog(BytesIO(byte))
        elif ext in ('.xls', '.xlsx'):
            self.recog = ExcelTableRecog( byte)
        else:
            raise Exception(f"wrong file ext {ext}")
        
    def classify(self):
        return self.recog.classify()
    
    
if __name__ =="__main__":
    #file_path = "data/input/test.xls"
    #file_path= "data/input/2022攀农业银行1-9月流水.xls"
    #file_path = "data/input/微信支付账单(20230427-20230727).xlsx"
    #file_path = "data/input/1672046917570_1364021.pdf"
    file_path = "data/input/支付宝1.pdf"
    # etr = ExcelTableRecog("data/input/甘玉兰化妆品2022.7-2022.9明细.xls")
    # etr = ExcelTableRecog("data/input1/攀德中国银行流水2021年.xlsx")
    # etr = ExcelTableRecog("data/alipay_record_20230727_112459.xlsx")
    EmbedingToolTable.init()
    with open(file_path ,'rb') as f:
        file_data = f.read()
        etr = FileClassify(file_path,file_data)
        obj = etr.classify()
        print(obj)