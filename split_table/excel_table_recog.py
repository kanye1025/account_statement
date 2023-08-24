import json
import os
from tools.embeding_tool import EmbedingTool
from config.config import CONF
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from openpyxl import load_workbook
import  xlrd
import numpy as np
class ExcelTableRecog:
    heads = "流水号/订单号,时间,收入,支出,备注/用途,余额/金额,对方账号,对方户名,收付款方式,开户机构/开户行,分类"
    #embeding = HuggingFaceEmbeddings(model_name=CONF.embeding_model_path)
    #h_emb = embeding.embed_query(heads)
    #h_emb = None
    #embeding = None
    def __init__(self,file_path):
        self.file_path = file_path
        _,ext = os.path.splitext(file_path)
        
        if ext ==".xls":
            booksheet = xlrd.open_workbook(file_path,formatting_info=True).sheets()[0]
            self.nrows = booksheet.nrows
            self.ncols = booksheet.ncols
            ret = [0]
            ret.extend([brk[0] for brk in booksheet.horizontal_page_breaks])
            ret.append(self.nrows)
            self.page_breaks = ret
        else:
            booksheet = xlrd.open_workbook(file_path).sheets()[0]
            self.nrows = booksheet.nrows
            self.ncols = booksheet.ncols
            wb = load_workbook(self.file_path, read_only=False)
            ws = wb.active
            ret = [0]
            ret.extend([brk.id for brk in ws.row_breaks.brk])
            ret.append(self.nrows)
            self.page_breaks = ret
        
        self.data = list()
        for i in range(booksheet.nrows):
            col = list()
            for j in range(booksheet.ncols):
                col.append(self.clear_value(booksheet.cell_value(i,j)))
            self.data.append(col)
        '''
        for col in datas:
            line = list()
            for v in col:
                if v:
                    line.append(v)
            line = ','.join(line)
            print(line)
        '''
    
        
        
    def clear_value(self,value):
        return str(value).strip().strip('\t')
    """
    def get_head_index(self):

        rows = list()
        for i in range(self.nrows):
            row = ','.join(self.data[i])
            rows.append(row)
        
        rows_emb = self.embeding.embed_documents(rows)
        results = list()
        for i,(row, e) in enumerate(zip(rows, rows_emb)):
            s = np.dot(self.h_emb, e)
            results.append((row, s,i))
        results = sorted(results, key=lambda x: x[1], reverse=True)
        max_score = results[0][1]
        results = filter(lambda x:x[1]==max_score,results)
        return list(results)
    """
    
    def get_col_index_range(self,head_index):
        col_index_range = [200, -1]
        for j in range(self.ncols):
            value =self.data[head_index][j]
            if value:
                col_index_range[0] = min(col_index_range[0], j)
                col_index_range[1] = max(col_index_range[1], j + 1)
        for j in range(col_index_range[0],col_index_range[1]):
            if not self.data[head_index][j] :
                raise Exception(f"head col {j} is empty")
        return col_index_range
    def get_row_index_range(self,head_index,col_index_range):
        for i in range(head_index+1,self.nrows):
            is_table_body = False
            for j in range(self.ncols):
                value = self.data[i][j]
                if j >=col_index_range[0] and j <col_index_range[1]:
                    if  value:#表格内只要有一个数据就行
                        is_table_body = True
                        continue
                else:
                    if value:#表格外不能有数据
                        is_table_body=False
                        break
            if not is_table_body:
                break
        row_index_range = [head_index,i]
        return row_index_range
    def get_table_data(self):
        heads = EmbedingTool.get_head_index(self.data)
        #heads = self.get_head_index()
        #heads = [1, 40, 54, 101, 158, 208, 307, 422, 503, 550, 602, 711]
        #heads = [24]
        col_range = self.get_col_index_range(heads[0])
        row_ranges = [self.get_row_index_range(head, col_range) for head in heads]
        page_sep = self.page_breaks
        row_infos = {}
        for table_index,row_range in enumerate(row_ranges):
            for row in range(row_range[0],row_range[1]):
                for page_index,p in enumerate(page_sep[:-1]):
                    if row <page_sep[page_index+1]:
                        row_order = '{:0>3d}'.format(page_index+1)+'_'+str(row-row_range[0]+1)
                        header_row =  row in heads
                        row_infos[row] = {'row_order':row_order,"header_row":header_row}
                        break
        #for row,row_info in row_infos.items():
        #    print(row,row_info)
        """
        or page_index in range(page_sep-1):
            for row in range(page_sep[page_index],page_sep[page_index+1]):
                pass
        """
        ret_obj = {}
        ret_obj["res1"] = {}
        ret_obj["res1"]["outside_infos"] = list()
        ret_obj['res2'] = list()
        for row in range(self.nrows):
            if row in row_infos:#表内
                row_info = row_infos[row]
                row_obj = {}
                row_obj.update(row_info)
                
                for col,v in enumerate(self.data[row]):
                    key = f"{row+1}.{col+1}"
                    row_obj[key] = v
                ret_obj['res2'].append(row_obj)
            else:               #表外
                line =list()
                for value in self.data[row]:
                    if value:
                        line.append(value)
                if line:
                    line = '\t'.join(line)
                    ret_obj["res1"]["outside_infos"].append({"txt":line})
        ret_obj['doc_tpye']="excel"
        ret_obj['page_sum'] = len(page_sep)-1
        return ret_obj
    def get_tabel_row_info(self):
        pass
    
    
        
        
    def print_table_data(self,row_index_range,col_index_range):
        for i in range(row_index_range[0],row_index_range[1]):
            line = list()
            for j in range(col_index_range[0],col_index_range[1]):
                line.append(self.data[i][j])

            print('\t'.join(line))
            
if __name__ =="__main__":
    #etr = ExcelTableRecog("data/input/test.xls")
    #etr = ExcelTableRecog("data/input/2022攀农业银行1-9月流水.xls")
    etr = ExcelTableRecog("data/input/张凌玮.xlsx")
    #etr = ExcelTableRecog("data/alipay_record_20230727_112459.xlsx")
    obj = etr.get_table_data()
    with open('data/out.json','w',encoding='utf-8') as f:
        json_str = json.dump(obj,f,ensure_ascii=False)
    #print(json_str)
    #heads = etr.get_head_index(book_sheet)
    #heads = [1,40,54,101,158,208,307,422,503,550,602,711]
    #print(etr.get_page_seps())
    #col_range = etr.get_col_index_range( heads[0])
    #for head in heads:
    #    print(head[2])
    #for head in heads:
    #    row_range = etr.get_row_index_range(head,col_range)
    #    etr.print_table_data( row_range,col_range)