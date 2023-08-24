import json

import pdfplumber
from tools.embeding_tool import EmbedingTool
import numpy as np
class PDFTableRecog:

    def __init__(self,file_path):
        self.file_path = file_path
        self.pdf = pdfplumber.open(file_path)
    def clear_table(self,table):
        if  table:
            for i,row in enumerate(table):
                for j ,col in enumerate(row):
                    if col ==None:
                        table[i][j] = ''
        return table
    
    def get_highest_cols(self,cols):
        
        cols = [ col.split('\n') for col in cols if col]
        cols = [ (col,len(col)) for col in cols]
        max_line_num = max([ col[1] for col in cols])
        cols = filter(lambda x:x[1] == max_line_num,cols)
        return [col[0] for col in cols]
        
    def get_text_before_table(self,text,cols):
        text = text.split('\n')
        cols = self.get_highest_cols(cols)
        query_text = ' '.join([col[0] for col in cols if col])
        texts_before = list()
        for t in text:
            if t == query_text:
                return texts_before
            texts_before.append(t)
        raise Exception("not match ")
    
    def get_text_after_table(self,text,cols):
        text = text.split('\n')
        cols = self.get_highest_cols(cols)
        query_text = ' '.join([col[-1] for col in cols])
        texts_after = list()
        after = False
        for t in text:
            if after:
                texts_after.append(t)
            if not after and t== query_text:
                after = True
            
        return texts_after
        
    
    def get_table_data(self):
        texts = list()
        tables = list()
        ret_obj = {}
        ret_obj["res1"] = {}
        ret_obj["res1"]["outside_infos"] = list()
        ret_obj['res2'] = list()
        #首页
        page = self.pdf.pages[0]
        table = self.clear_table(page.extract_table())
        
        text = page.extract_text()
        
        head = EmbedingTool.get_head_index(table)[0]
        texts.extend(self.get_text_before_table(text, table[0]))
        tables.append(table[head:])
        rows_before_head = table[:head]
        for row in rows_before_head:
            texts.append(' '.join(row))
            
        
        #中间页
        if len(self.pdf.pages)>2:
            for page in self.pdf.pages[1:-2]:
                table = self.clear_table(page.extract_table())
                if table:
                    tables.append(table)
            
        #尾页

        page = self.pdf.pages[-1]
        table = self.clear_table(page.extract_table())
        text = page.extract_text()
        if table:
            tables.append(table)
            texts.extend(self.get_text_after_table(text,table[-1]))
        else:
            texts.extend(text.split('\n'))
            
        
        for text in texts:
            ret_obj["res1"]["outside_infos"].append({'txt':text})
        for page_index,table in enumerate(tables):
            for row_index,row in enumerate(table):
                row_order = '{:0>3d}'.format(page_index + 1) + '_' + str(row_index + 1)
                header_row = True if page_index == 0 and row_index == 0 else False
                row_obj = {'row_order': row_order, "header_row": header_row}
                for col_index,v in enumerate(row):
                    if not v:
                        v = ''
                    k = f'{row_index+1}.{col_index+1}'
                    row_obj[k] = v.replace('\n','')
                ret_obj['res2'].append(row_obj)
        ret_obj['doc_tpye'] = "epdf"
        ret_obj['page_sum'] = len(self.pdf.pages)
        return ret_obj
        
if __name__ == '__main__':
    ptr = PDFTableRecog("data/微信交易明细.pdf")
    obj = ptr.get_table_data()
    with open('data/out.json','w',encoding='utf-8') as f:
        json_str = json.dump(obj,f,ensure_ascii=False)