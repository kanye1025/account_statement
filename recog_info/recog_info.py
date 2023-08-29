# coding=utf-8
import json
from tools.embeding_tool import EmbedingTool
from tools.llm_tool import LLMTool
from collections import Counter
from config import dicts
import Levenshtein
import datetime
class RecogInfo:
    date_formats = ["%Y-%m-%d%H:%M:%S",
                    "%Y-%m-%d",
                    "%Y-%m-%d%H:%M:%S.%f",
                    "%Y/%m/%d%H:%M:%S",
                    "%Y/%m/%d",
                    "%Y/%m/%d%H:%M:%S.%f",
                    ]
    def __init__(self,obj):
        self.obj = obj
        self.texts = '\n'.join([i['txt'] for i in obj['res1']['outside_infos']])
        if not self.texts.replace('\n', '').replace(' ', '').replace('\t', ''):
            self.texts = None
        
    def get_agent(self):
        
        if not self.texts:
            agent = 'bank'
        else:
            if "支付宝" in self.texts:
                agent = 'alipay'
            elif "微信" in self.texts:
                agent = "wechat"
            else:
                agent = "bank"
            #agent = EmbedingTool.recog_agent(self.texts)
        self.obj['res1']['agent_type'] = agent
        self.agent = agent
    def recog_field(self,agent_type,head_dict):
        if agent_type == 'bank':
            sub_type = EmbedingTool.get_bank_type(head_dict)
            field_index_dict = EmbedingTool.recog_field(sub_type, head_dict)
        elif agent_type =="alipay":
            sub_type = EmbedingTool.get_alipay_type(head_dict)
            field_index_dict = EmbedingTool.recog_field(sub_type, head_dict)
            
        else:
            sub_type = None
            field_index_dict = EmbedingTool.recog_field(agent_type, head_dict)
        return field_index_dict,sub_type
    
    def statistic_main_account(self,field_index_dict):
        payer_account_index = field_index_dict["付款人"]
        payer_id_index = field_index_dict["付款账号"]
        payee_account_index = field_index_dict["收款人"]
        payee_id_index = field_index_dict["收款账号"]
        account_counter = Counter()
        id_counter = Counter()
        for row in self.obj["res2"]:
            if not row["header_row"]:
                row_index = row["row_order"].split('_')[1]
                account_counter.update([row[row_index + '.' + payer_account_index],
                                        row[row_index + '.' + payee_account_index]])
                id_counter.update([row[row_index + '.' + payer_id_index],
                                   row[row_index + '.' + payee_id_index]])
        return account_counter.most_common(1)[0][0],id_counter.most_common(1)[0][0]
    def trans_bank_row(self,bank_type,row_obj,account,id):
        if bank_type == "bank_IE_sign":
            if '-' in row_obj["交易金额"]:
                row_obj["收支类型"] = "支出"
            else:
                row_obj["收支类型"] = "收入"
        elif bank_type in ("bank_IE_split_amount" ,"bank_IE_split_remaining"):
            if not row_obj["支出"] or not float(row_obj["支出"]):
                row_obj["收支类型"] = "收入"
                row_obj["交易金额"] = row_obj["收入"]
            elif not row_obj["收入"] or not float(row_obj["收入"]):
                row_obj["收支类型"] = "支出"
                row_obj["交易金额"] = row_obj["支出"]
            else:
                raise Exception("收入，支出同时存在")
            del row_obj["收入"]
            del row_obj["支出"]
        elif bank_type == "bank_IE_role":
            if row_obj["付款人"] == account:
                row_obj["收支类型"] = "支出"
                row_obj["对方账号"] =row_obj["收款人"]
                row_obj["对方户名"] =row_obj["收款账号"]
            elif row_obj["收款人"] == account:
                row_obj["收支类型"] = "收入"
                row_obj["对方账号"] = row_obj["付款人"]
                row_obj["对方户名"] = row_obj["付款账号"]
            else:
                raise Exception("main account wrong")
            del row_obj["收款人"]
            del row_obj["付款人"]
            del row_obj["付款账号"]
            del row_obj["收款账号"]
        elif bank_type =="bank_IE_type":
            pass
        else:
            raise Exception(f"unknow bank_type {bank_type}")
        row_obj["交易金额"] = row_obj["交易金额"].replace('-','').replace(',','')
        return row_obj
    def trans_alipay_row(self,alipay_type,row_obj,account,id):
        if alipay_type == "alipay_IE_split":
            if not row_obj["支出"] or not float(row_obj["支出"]):
                row_obj["收/支"] = "收入"
                row_obj["金额"] = row_obj["收入"]
            elif not row_obj["收入"] or not float(row_obj["收入"]):
                row_obj["收/支"] = "支出"
                row_obj["金额"] = row_obj["支出"]
            else:
                raise Exception("收入，支出同时存在")
            row_obj["交易对方"] = ""
            row_obj["收/付款方式"] = ""
            del row_obj["收入"]
            del row_obj["支出"]
        elif alipay_type == "alipay_IE_type":
            pass
        else:
            raise Exception(f"unknow bank_type {alipay_type}")
        row_obj["金额"] = row_obj["金额"].replace('-', '').replace(',','')
        return row_obj
    def clear_field(self,head_dict):
        c = Counter()
        for row in self.obj["res2"]:
            if not row["header_row"]:
                c.update([k.split('.')[1] for k,v in row.items() if '.' in k and v.strip()])
        valid_keys = set(c.keys())
        ret = {}
        for k,v in head_dict.items():
            if k in valid_keys:
                ret[k] = v
        return ret
                        
    def field_align(self):
        agent_type = self.obj["res1"]['agent_type']
        self.obj["res3"] = list()
        head_dict = dict()
        for row in self.obj["res2"]:
            if row["header_row"] == True:
                for k,v in row.items():
                    if '.' in k:
                        _,col_index =k.split('.')
                        head_dict[col_index] = v
            break
        if not head_dict:
            raise Exception("not find any header_row")
        head_dict = self.clear_field(head_dict)
        field_index_dict,sub_type = self.recog_field(agent_type,head_dict)
        if sub_type =="bank_IE_role":
            account,id = self.statistic_main_account(field_index_dict)
        else:
            account,id = None,None
        for res2_row in self.obj["res2"]:
            res3_row = {}
            res3_row["row_order"] = res2_row["row_order"]
            row2_index = res2_row["row_order"].split('_')[1]
            res3_row["header_row"] = res2_row["header_row"]
            row_obj = {}
            for field, col_index in field_index_dict.items():
                index2 = row2_index + '.' + col_index
                row_obj[field] =res2_row[index2]
            if agent_type == 'bank' and not res2_row["header_row"]:
                row_obj = self.trans_bank_row(sub_type,row_obj,account,id)
            elif agent_type == 'alipay' and not res2_row["header_row"]:
                row_obj = self.trans_alipay_row(sub_type, row_obj, account, id)
                
            for i,key in enumerate(dicts.field_dict[agent_type].keys()):
                index3 = row2_index + '.' + str(i + 1)
                if res2_row["header_row"]:
                    res3_row[index3] = key
                else:
                    res3_row[index3] = row_obj[key].replace(' ',"")
                    if key == "交易日期":
                        res3_row[index3] = self.normalize_date_format(res3_row[index3])
            self.obj["res3"].append(res3_row)
            
    def get_before_info(self):
        if self.texts:
            obj = LLMTool.recog_before_info(self.agent,self.texts)
            if self.agent == "bank" :
                if obj["bank_name"] in dicts.bank_code_dict:
                    obj["bank_name"] = dicts.bank_code_dict[obj["bank_name"]]
                else:
                    l = [(k,code,Levenshtein.distance(obj["bank_name"], k))for k ,code in dicts.bank_code_dict.items()]
                    min_distance = min([d for (_,_,d) in l])
                    for k,code,d in l:
                        if d == min_distance:
                            obj["bank_name"] = code
            self.obj['res1'].update(obj)
            
        
    def get_recoged_obj(self):
        self.get_agent()
        self.get_before_info()
        self.field_align()
        return self.obj
        
    def normalize_date_format(self,date_str):
        
        for format_str in self.date_formats:
            try:
                dt = datetime.datetime.strptime(date_str,format_str)
                date_str = dt.strftime("%Y/%m/%d")
                return date_str
            except:
                pass
        raise Exception(f"cannot normalize date format: {date_str}")
        
        
        #def
if __name__ == "__main__":
    #file_path = "data/output/张凌玮.xlsx.txt"
    file_path = "data/output/支付宝1.pdf.txt"
    #file_path = "data/output/李佳蔚.xlsx.txt"
    with open(file_path,'r',encoding="utf-8") as f:
        with open ('data/out.json','w',encoding='utf-8') as fo:
            obj = json.load(f)
            obj = RecogInfo(obj).get_recoged_obj()
            json.dump(obj['res3'],fo,ensure_ascii=False)
    