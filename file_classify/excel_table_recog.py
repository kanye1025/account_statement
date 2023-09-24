
import os
from tools.embeding_tool_table import EmbedingToolTable as EmbedingTool


import  xlrd

class ExcelTableRecog:
    
    
    def __init__(self,byte):
        self.book = xlrd.open_workbook(file_contents=byte)
        self.booksheet = self.book.sheets()[0]
        
     
        self.nrows = self.booksheet.nrows
        self.ncols = self.booksheet.ncols

            
        self.data = list()
        for i in range(self.booksheet.nrows):
            col = list()
            for j in range(self.booksheet.ncols):
                value = str(self.booksheet.cell_value(i,j))
                col.append(value)
            self.data.append(col)
   
    def classify(self):
        
        heads = EmbedingTool.get_head_index(self.data)
        texts = ""
        for row in range(self.nrows):
            if row < heads[0]:                #只取首页表前面的信息
                for value in self.data[row]:
                    if value:
                        texts+=value

        if "支付宝" in texts:
            agent = 'alipay'
        elif "微信" in texts:
            agent = "wechat"
        else:
            agent = "bank"
        ret_obj = {
            "agent_type":          agent,
            "file_format":         "excel",
            "stamp_layer":         False,
            "digital_certificate": False,
            "imformation":         "",
            "image":               [],
            "file":                ""}
        
        return ret_obj

    
        

            
if __name__ =="__main__":
    #etr = ExcelTableRecog("data/input/test.xls")
    #etr = ExcelTableRecog("data/input/2022攀农业银行1-9月流水.xls")
    #etr = ExcelTableRecog("data/input/甘玉兰化妆品2022.7-2022.9明细.xls")
    etr = ExcelTableRecog("data/input1/攀德中国银行流水2021年.xlsx")
    #etr = ExcelTableRecog("data/alipay_record_20230727_112459.xlsx")
    obj = etr.classify()
    print(obj)
