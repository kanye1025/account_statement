# coding=utf-8
import json
from tools.embeding_tool_info import EmbedingToolInfo as EmbedingTool
from tools.llm_tool import LLMTool
from collections import Counter
from config import dicts
import Levenshtein
import datetime
from collections import defaultdict
from tools.embeding_tool import *
class RecogInfo:
    date_formats = ["%Y-%m-%d%H:%M:%S",
                    "%Y-%m-%d",
                    #"%Y-%m-%d%H:%M:%S.%f",
                    "%Y/%m/%d%H:%M:%S",
                    "%Y/%m/%d",
                    #"%Y/%m/%d%H:%M:%S.%f",
                    "%Y%m%d",
                    "%Y%m%d%H%M%S",
                    "%Y%m%d%H:%M:%S",
                    
                    ]
    def __init__(self,obj):
        EmbedingTool.init()
        self.obj = obj
        self.texts = '\n'.join([i['txt'] for i in obj['res1']['outside_infos']])
        if not self.texts.replace('\n', '').replace(' ', '').replace('\t', ''):
            self.texts = None
    def str_to_float(self,s):
        s = s.replace(',','')
        return float(s)
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
    def recog_field_sub_type(self,head_list):
        head_list = [head.replace("支取","支出") for head in head_list]
        def get_index(field):
            for index,head in enumerate(head_list):
                if field in head:return index
            return -1
        zhichu_index = get_index("支出")
        shouru_index = get_index("收入")
        if zhichu_index!= -1 and  shouru_index!=-1:
            if zhichu_index!=shouru_index:
                return "IE_split"
            else:
                return "IE_type"
        if get_index("收支")!=-1 or get_index("收/支")!=-1 or get_index("收\支") !=-1:
            return "IE_type"
        if get_index("付款") != -1 and get_index("收款")!=-1:
            return "IE_role"
        else:
            return "IE_sign"
    
    def recog_field(self,agent_type,head_dict,head_value_dict):
        """
        for k,v in head_dict.items():
            if "日期" in v:
                head_dict[k]+=",日期"
            if "时间" in v:
                head_dict[k]+=",时间"
        """
        sub_type = agent_type +"_"+ self.recog_field_sub_type(head_value_dict.keys())
        if agent_type == 'bank':
            field_index_dict = EmbedingTool.recog_field(sub_type, head_dict)
        elif agent_type == "alipay":
            field_index_dict = EmbedingTool.recog_field(sub_type, head_dict)

        else:
            field_index_dict = EmbedingTool.recog_field(agent_type, head_dict)
        return field_index_dict, sub_type
    
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
        elif bank_type == "bank_IE_split":
            if not row_obj["支出"] or not self.str_to_float(row_obj["支出"]):
                row_obj["收支类型"] = "收入"
                row_obj["交易金额"] = row_obj["收入"]
            elif not row_obj["收入"] or not self.str_to_float(row_obj["收入"]):
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
            if not row_obj["支出"] or not self.str_to_float(row_obj["支出"]):
                row_obj["收/支"] = "收入"
                row_obj["金额"] = row_obj["收入"]
            elif not row_obj["收入"] or not self.str_to_float(row_obj["收入"]):
                row_obj["收/支"] = "支出"
                row_obj["金额"] = row_obj["支出"]
            else:
                raise Exception("收入，支出同时存在")
            row_obj["交易对方"] = ""
            del row_obj["收入"]
            del row_obj["支出"]
        elif alipay_type == "alipay_IE_type":
            pass
        else:
            raise Exception(f"unknow bank_type {alipay_type}")
        row_obj["金额"] = row_obj["金额"].replace('-', '').replace(',','')
        return row_obj
    def clear_head(self,head_dict):
        c = Counter()
        for row in self.obj["res2"]:
            if not row["header_row"]:
                #判断这一列是不是全是空值
                c.update([k.split('.')[1] for k,v in row.items() if '.' in k and v.replace('-','').replace('——','')
                         .replace('_','').strip()])
        valid_keys = set(c.keys())
        ret = {}
        for k,v in head_dict.items():
            if k in valid_keys:
                ret[k] = v
        return ret
    def gen_head_description(self,head_dict):
        sample_dict = dict()

        for row in self.obj["res2"]:
            if not row["header_row"]:
                for k,v in row.items() :
                    if '.' in k:
                        k = k.split('.')[1]
                        if k  in head_dict and k not in sample_dict  :
                            v = v.replace('-', '').replace('——', '').replace(' ','').strip()
                            if not v: continue
                            if v in sample_dict.values(): continue
                            sample_dict[k]=v
                if len(sample_dict) == len(head_dict):
                    break
        ret_obj = {}
        for j,(k,head) in enumerate(head_dict.items()):
            if  k in sample_dict:
                ret_obj[head] = sample_dict[k]
            
        return ret_obj
    
    def person_or_org(self,text):
        
        score_dict = {k:v for k,v in EmbedingToolBasic.classify_by_embeding_dict(EmbedingTool.person_organization_embeding, text,top_k = 2)}
        if len(text)<=3 and "支付" not in text and "微信" not in text and "财付通" not in text:
            score_dict["PERSON"] +=0.1
        return sorted([(k,v)for k,v in score_dict.items()],key=lambda x:x[1],reverse=True)[0][0]
        
    def get_org_type(self,agent_type,row_obj):
        
        counterparty_key = "对方户名" if agent_type == "bank" else "交易对方"
        counterparty = row_obj[counterparty_key]
        if not counterparty: return "",""
        #if EmbedingTool.person_or_org(counterparty) != "ORG":
        if self.person_or_org(counterparty) != "ORG":
            return "",""

        #counterparty = counterparty.replace()
        return EmbedingTool.get_org_type(counterparty)

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
        head_dict = self.clear_head(head_dict)
        head_value_dict = self.gen_head_description(head_dict)
        field_index_dict,sub_type = self.recog_field(agent_type,head_dict,head_value_dict)
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
                row_obj[field] =res2_row[index2].replace(' ','') if col_index else ""
            
            if agent_type == 'bank' and not res2_row["header_row"]:
                row_obj = self.trans_bank_row(sub_type,row_obj,account,id)
            elif agent_type == 'alipay' and not res2_row["header_row"]:
                row_obj = self.trans_alipay_row(sub_type, row_obj, account, id)
            

            #code_name_filed = dicts.field_code_name_dict[agent_type]
            #row_obj = {code_name_filed[code]:v for code,v in row_obj.items()}
            #row_obj = {name:row_obj[code] if code in row_obj else "" for code,name in code_name_filed.items() }
            
            row_obj["科目标签"] = self.predict_account_label(row_obj) if not res3_row["header_row"] else "科目标签"
            row_obj["分录方向"] = self.get_accounting_entry(row_obj) if not res3_row["header_row"] else "分录方向"
            row_obj["机构属性代码"],row_obj["机构属性名称"] = self.get_org_type(agent_type,row_obj) if not res3_row["header_row"] else ("机构属性代码","机构属性名称")
            
            field_list = list(dicts.field_code_name_dict[agent_type].values())
            field_list.extend(["科目标签","分录方向"])
            
            for i,key in enumerate(field_list):
                index3 = row2_index + '.' + str(i + 1)
                if res2_row["header_row"]:
                    res3_row[index3] = key
                else:
                    res3_row[index3] = row_obj[key]
                    if key == "交易日期":
                        res3_row[index3] = self.normalize_date_format(res3_row[index3])
                    elif "金额" in key or "余额" in key:

                        res3_row[index3] = self.normalize_money_format(res3_row[index3])
                        
            self.obj["res3"].append(res3_row)
    
    def get_before_info(self):
        if self.texts:
            obj = LLMTool.recog_before_info(self.agent,self.texts)
            if not obj["account_type"]:
                obj["account_type"] = self.person_or_org(obj["account_name"])
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
            
    def get_accounting_entry(self,row_obj):
        pay_type = dicts.pay_type_dict[self.agent]
        if not row_obj[pay_type] or row_obj[pay_type]=="其他":
            return ""
        if not row_obj["科目标签"] :return ""
        key = f"""{row_obj["科目标签"]},{row_obj[pay_type]}"""
        return dicts.accounting_entry_dict[key]
    def predict_account_label(self,row_obj):
        if self.agent =="bank":
            pay_type = row_obj["收支类型"]
            text = row_obj["备注（摘要）"]+' '+row_obj["对方户名"]
        elif self.agent =="alipay":
            pay_type = row_obj["收/支"]
            text = row_obj["交易对方"]+' '+row_obj["商品说明"]
        elif self.agent == "wechat":
            pay_type = row_obj["收/支/其他"]
            text = row_obj["交易类型"] +' '+row_obj["交易对方"]+ ' '+row_obj["交易方式"]
        
        return EmbedingTool.get_account_label(pay_type,text)
    
    def get_recoged_obj(self):
        self.get_agent()
        self.get_before_info()
        self.field_align()
        return self.obj
    
    def normalize_date_format(self,date_str):
        date_str = date_str.split(".")[0]
        for format_str in self.date_formats:
            try:
                dt = datetime.datetime.strptime(date_str,format_str)
                date_str = dt.strftime("%Y/%m/%d")
                return date_str
            except:
                pass
        try:
            date =  float(date_str)
            date = datetime.datetime(year=1899,month=12,day=30)+datetime.timedelta(days=date)
            return date.strftime("%Y/%m/%d")
        except:
            pass
        raise Exception(f"cannot normalize date format: {date_str}")
        
    def normalize_money_format(self,money_str):
        money_str = money_str.replace(',','')
        
        try:
            money =  float(money_str)
            return money
        except:
            raise Exception(f"money normalize failed: {money_str}")
if __name__ == "__main__":
    file_path = "data/output/甘玉兰化妆品2022.7-2022.9明细.xls.txt"
    #file_path = "data/output/支付宝1.pdf.txt"
    #file_path = "data/output/李佳蔚.xlsx.txt"
    EmbedingToolBasic.init()
    EmbedingTool.init()
    with open(file_path,'r',encoding="utf-8") as f:
        with open ('data/out.json','w',encoding='utf-8') as fo:
            obj = json.load(f)
            obj = RecogInfo(obj).get_recoged_obj()
            json.dump(obj['res3'],fo,ensure_ascii=False)
    