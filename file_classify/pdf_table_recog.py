
import pdfplumber
from tools.embeding_tool_table import EmbedingToolTable as EmbedingTool
import base64
import fitz
class PDFTableRecog:
    
    def __init__(self,byte):
        EmbedingTool.init()
        self.pdf = pdfplumber.open(byte)
        self.byte = byte
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
        texts_before = ""
        for t in text:
            if t == query_text:
                return texts_before
            texts_before+=t
        raise Exception("not match ")
    
        
    
    def classify(self):
        
        texts_before_table = ""
        tables = list()

        page = self.pdf.pages[0]
        
        table = self.clear_table(page.extract_table())
        if not table:
            ret_obj = {
                "agent_type":          "",
                "file_format":         "ImagePDF",
                "stamp_layer":         False,
                "digital_certificate": False,
                "imformation":         "",
                "image":               [],
                "file":                ""}
            return ret_obj
        

        
        text = page.extract_text()
        
        head = EmbedingTool.get_head_index(table)[0]
        
        texts_before_table+=self.get_text_before_table(text, table[0])
        tables.append(table[head:])
        rows_before_head = table[:head]
        for row in rows_before_head:
            texts_before_table+=' '.join(row)
        if "支付宝" in texts_before_table:
            agent = 'alipay'
        elif "微信" in texts_before_table:
            agent = "wechat"
        else:
            agent = "bank"
        

        ret_obj = {
            "agent_type":          agent,
            "file_format":         "TextPDF",
            "stamp_layer":         False,
            "digital_certificate": False,
            "imformation":         "",
            "image":               [],
            "file":                ""}
        is_exists_im = False
        pdf = fitz.open(stream = self.byte)  # PyMuPdf安装后，包的名字叫fitz
        for p in pdf:  # 遍历pdf的每一页
            ims = p.get_images()  # 获取当前页的图片，返回一个list
            if ims:
                images = list()
                for im in ims:  # 遍历每张图片
                    image = pdf.extract_image(im[0])
                    rate =  float(image['width'])/float(image['height'])
                    if rate>4 or rate <0.25: #比例不对的图片可能是控件背景
                        continue
                    if not is_exists_im:
                        images.append(str(base64.b64encode(image['image']),encoding= 'utf-8'))
                        
                    pdf._deleteObject(im[0])  # 删除图片
                if images:
                    is_exists_im = True
                    ret_obj["image"] = images

        if is_exists_im:
            ret_obj["stamp_layer"] = True
            b = pdf.write()
            ret_obj["file"] = str(base64.b64encode(b),encoding='utf-8')
        return ret_obj
        
        
        
