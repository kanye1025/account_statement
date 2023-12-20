# coding=utf-8
#import os
#import sys
#sys.path.append(os.getcwd())
import json
from tools.embeding_tool_info import EmbedingToolInfo as EmbedingTool
from tools.llm_tool import LLMTool
from config.load_asset_accounts_dict import get_asset_accounts_dict
from collections import Counter
from recog_info.sample_writer import SampleWriter
import Levenshtein
from multiprocessing import Pool
import datetime
from multiprocessing import cpu_count
from collections import defaultdict
from tools.embeding_tool import *
from copy import  deepcopy
from recog_info.prompt import Prompts
from recog_info.recog_info_config  import load_label_config
from config.load_asset_accounts_dict import get_personal_consumption_dict
from functools import lru_cache
class process_row:
    def __init__(self,ri):
        self.ri = ri
    def __call__(self, res2_row):
        res3_row = {}
        res3_row["row_order"] = res2_row["row_order"]
        row2_index = res2_row["row_order"].split('_')[1]
        res3_row["header_row"] = res2_row["header_row"]
        row_obj = {}
        
        for field, col_index in self.ri.field_index_dict.items():
            index2 = row2_index + '.' + col_index
            row_obj[field] = res2_row[index2].replace(' ', '') if col_index else ""
        
        if self.ri.agent_type == 'bank' and not res2_row["header_row"]:
            row_obj = self.ri.trans_bank_row(self.ri.sub_type, row_obj, self.ri.account, id)
        elif self.ri.agent_type == 'alipay' and not res2_row["header_row"]:
            row_obj = self.ri.trans_alipay_row(self.ri.sub_type, row_obj, self.ri.account, id)
        
 
        
        
        if not res3_row["header_row"] :
            _,trader_nature = self.ri.get_org_type(self.ri.agent_type, row_obj)

            row_data = {}
            for k, v in res2_row.items():
                if '.' in k:
                    k = k.split('.')[1]
                    field_name = self.ri.head[k]
                    row_data[field_name] = self.ri.normalize_digit_str(v)
                # row = self.get_fields(row_data)

                # row['交易对手账户']["账户类型"] = self.get_account_class(row["交易对手账户"]["户名"])
            #print(self.get_label(json.dumps(row_data, ensure_ascii=False)))
            text = ""
            if self.ri.agent == "bank":
                pay_type = row_obj["收支类型"]
            elif self.ri.agent == "alipay":
                pay_type = row_obj["收/支"]
            elif self.ri.agent == "wechat":
                pay_type = row_obj["收/支/其他"]
            if pay_type not in ("收入","支出"):
                pay_type = self.ri.recog_income_or_expenses(row_obj)

            account_label = {}
            row_label = {}
            trade_type, s_dir, s_tag =self.ri.predict_account_labelv2(row_obj,pay_type,trader_nature,row_data)
            row_label['product type'] = trade_type
            account_label["accounting_item"],account_label["accouting_entry"] =s_tag,s_dir
            if self.ri.account_class ==  "理财账户":
                account_label["N-accounting_item"] = "Z02理财资产"
            elif self.ri.account_class ==  "信用账户":
                account_label["N-accounting_item"] = "F04信用卡"
            else:
                account_label["N-accounting_item"] = "Z08账户余额"

            if account_label["N-accounting_item"] == "F0401信用卡":
                account_label["N-accouting_entry"] = "减少"  if pay_type == "收入"  else "增加"
            else:
                account_label["N-accouting_entry"] = "减少" if pay_type == "支出" else "增加"


            res2_row['account_label'] = account_label


            row_label["header_row"] = res2_row['header_row']
            row_label["trader_nature"] = trader_nature
            row_label["in_spend_type"] = pay_type
            res2_row["row_label"] = row_label


            # = self.ri.get_accounting_entry(row_obj,res2_row["accounting_item"])

        field_list = list(dicts.field_code_name_dict[self.ri.agent_type].values())

        
        for i, key in enumerate(field_list):
            index3 = row2_index + '.' + str(i + 1)
            if res2_row["header_row"]:
                res3_row[index3] = key
            else:
                res3_row[index3] = row_obj[key]
                if key == "交易日期":
                    res3_row[index3] = self.ri.normalize_date_format(res3_row[index3])
                elif "金额" in key or "余额" in key:
                    if  "余额"  in key and  not res3_row[index3]:
                        continue
                    res3_row[index3] = self.ri.normalize_money_format(res3_row[index3])
        
        for k,v in row_obj.items():
            if "备注" in k:
                i+=1
                index3 = row2_index + '.' + str(i + 1)
                if res2_row["header_row"]:
                    res3_row[index3] = k
                else:
                    res3_row[index3] = row_obj[k]
        del res2_row['header_row']
        return res2_row,res3_row



def _init_(i):
    
    RecogInfo.et.init(True)
    import os
    
    print(f"thread {i} {os.getpid()} init {RecogInfo.et.inited}")
    
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
                    "%Y年%m月%d日",
                    
                    ]
    et = EmbedingTool()
    llm = LLMTool.llm
    lable_conf = load_label_config()
    consumption_dict, consumption_index_dict = get_personal_consumption_dict()
    @classmethod
    def init(cls):
        
        LLMTool.init()
        sub_count = min(cpu_count(), CONF.max_worker)
        
        cls.et.init(CONF.load_embeding)
        #cls.pool = Pool(sub_count)
        #cls.pool.map(_init_,range(sub_count))

        
    
        
    def __init__(self,obj,file_name = None,sample_writer = None):
        self.obj = obj
        self.texts = '\n'.join([i['txt'] for i in obj['res1']['outside_infos']])
        if not self.texts.replace('\n', '').replace(' ', '').replace('\t', ''):
            self.texts = None
        self.file_name = file_name
        self.sample_writer = sample_writer

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
            #agent = self.et.recog_agent(self.texts)
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
        if get_index("借方") != -1 and get_index("贷方")!=-1:
            return "IE_split_debit_credit"
        
        return "IE_sign"
    
    def recog_field(self,agent_type,head_dict,head_value_dict):
        
        sub_type = agent_type +"_"+ self.recog_field_sub_type(head_value_dict.keys())
        if agent_type == 'bank':
            field_index_dict = self.et.recog_field(sub_type, head_dict)
        elif agent_type == "alipay":
            field_index_dict = self.et.recog_field(sub_type, head_dict)

        else:
            field_index_dict = self.et.recog_field(agent_type, head_dict)
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
        elif bank_type in ("bank_IE_split","bank_IE_split_debit_credit"):
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
        
        if "对方开户行" in row_obj:
            del row_obj["对方开户行"]
        if "付款开户行" in row_obj:
            del row_obj["付款开户行"]
        if "收款开户行" in row_obj:
            del row_obj["收款开户行"]
        
        
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
                        if k  in head_dict and k not in sample_dict:
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
    
    
        
    def get_org_type(self,agent_type,row_obj):
        
        counterparty_key = "对方户名" if agent_type == "bank" else "交易对方"
        counterparty = row_obj[counterparty_key]
        if not counterparty: return "",""
        #if self.et.person_or_org(counterparty) != "ORG":
        person_org = self.et.person_or_org(counterparty)
        if person_org=='PERSON':
            return "","个人"
        if person_org != "ORG":
            return "",""

        #counterparty = counterparty.replace()
        return self.et.get_org_type(counterparty)
    def normalize_digit_str(self,s):
        if ',' in s:
            s_ = s.replace(',','')
            try:
                float(s_)
                return s_
            except:
                return s
        else:
            return s
    def field_align(self):
        self.agent_type = self.obj["res1"]['agent_type']
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
        self.field_index_dict,self.sub_type = self.recog_field(self.agent_type,head_dict,head_value_dict)
        
        if self.agent == "bank":
            remark_indexes = list()
            for k,v in self.field_index_dict.items():
                if '备注' in k and v:
                    remark_indexes.append(v)
            for i in range(5):
                del self.field_index_dict[f"备注{i+1}"]
            if len(remark_indexes) == 1:
                self.field_index_dict["备注"]=remark_indexes[0]
            elif len(remark_indexes)>1:
                for i in range(len(remark_indexes)):
                    self.field_index_dict[f"备注{i+1}"] = remark_indexes[i]
        
        head_dict_tmp = deepcopy(head_dict)
        for k,v in self.field_index_dict.items():
            if v:
                #print(k,head_dict_tmp[v])
                del head_dict_tmp[v]
            #else:
            #    print(k,v)
        #print(head_dict_tmp.values())
        
        #return
        
        
        if self.sub_type =="bank_IE_role":
            self.account,self.id = self.statistic_main_account(self.field_index_dict)
        else:
            self.account,self.id = None,None

        head_row = self.obj['res2'][0]
        i = 0
        head = dict()
        while True:
            i += 1
            key = f'1.{i}'
            if key in head_row:
                head[str(i)] = head_row[key]
            else:
                break

        # head = self.clear_head(head)
        for k, v in head.items():
            v = v.replace('[', "").replace(']', "").replace('{', "").replace('}', "").replace('.', "").replace('(',
                                                                                                               "").replace(
                ')', "")
            tmp_v = list()
            for w in v:
                if w.encode('utf-8').isalpha():
                    continue
                tmp_v.append(w)
            head[k] = ''.join(tmp_v).strip()



        self.head = head
        if self.sample_writer:
            self.sample_writer.add_head(self.file_name,head.values())
        p = process_row(self)
        #rets = [p(self.obj["res2"][i]) for i in  range(0,len(self.obj["res2"][:30]),3)    ]#todo
        rets = [p(self.obj["res2"][i]) for i in  range(0,len(self.obj["res2"]))    ]
        #rets = self.pool.map(process_row(self),self.obj["res2"])
        res2_row,res3_row = zip(*rets)
        self.obj["res2"] = res2_row
        self.obj["res3"] = res3_row
        '''
        for res2_row in self.obj["res2"]:
            res3_row = process_row(res2_row)
            self.obj["res3"].append(res3_row)
        '''

    account_class_dict = {
        "理财账户": ["余额宝", "零钱通", "理财", "基金", "信托"],
        "信用账户": ["信用", "花呗", "亲情卡"]
    }

    def get_account_class(self, account_name):
        for k, v in self.account_class_dict.items():
            for n in v:
                if n in account_name:
                    return k
        # return "借记账户"
        return ""

    def get_consume_label(self, row):

        text = '\n'.join([f'{k}:{v}'for k,v in row.items() if v])
        des = '\n'.join([f"{k}-->{v}" for k, v in self.consumption_dict.items()])
        prompt = Prompts.create_prompt(Prompts.consume_label_prompt,
                                       {"text": text,"des":des, "key": str([i for i in self.consumption_index_dict.keys()])})

        obj = self.llm.predict_respond_json2(prompt, """{"消费类型":""")
        # print(f"{obj['消费类型']}")
        if obj["消费类型"] not in self.consumption_index_dict:
            return "P03消费支出"
        num = str(self.consumption_index_dict[obj["消费类型"]]).rjust(2, '0')
        return f"""P03{num}{obj["消费类型"]}"""

    @lru_cache(None)
    def get_label(self, pay_type,trader_nature,row_str):
        row = json.loads(row_str)

        if pay_type not in ("收入", "支出"):
            return "",""
        row['对方所属行业'] = trader_nature
        person_org = self.obj['res1']["account_type"]

        person_org = "对私" if person_org == "对私" else "对公"  # unknown 也当对公处理
        account_label_dict = self.lable_conf[(person_org, pay_type)]
        des = '\n'.join([f"{k}-->{v[0]}" for k, v in account_label_dict.items()])


        text = '\n'.join([f'{k}:{v}' for k,v in row.items() if v and '支出' not in v and '收入' not in v ])

        text = text.replace("货款", "货物款")
        prompt = Prompts.create_prompt(Prompts.account_label_prompt,
                                       {"text": text, "des": des, "key": str([i for i in account_label_dict.keys()])})
        print(person_org,pay_type)
        print(text)
        obj = self.llm.predict_respond_json2(prompt, """{"标签类型":""")

        # print(f"{[person_org,pay_type,text]}-->{obj['标签类型']}")
        if obj["标签类型"] not in account_label_dict:
            return "","","",""
        '''
        if obj["标签类型"] == "P03消费支出":
            ret = self.get_consume_label(row)
            print(ret)
            print('-' * 20)
            if self.sample_writer:
                self.sample_writer.add_sample(self.file_name, ret, person_org, pay_type, row)
            return ret, "增加"
        '''
        print(obj)
        print('-' * 20)
        if self.sample_writer:
            self.sample_writer.add_sample(self.file_name,obj["标签类型"],person_org,pay_type,row)
        ( s_dir, s_tag) = account_label_dict[obj["标签类型"]][1]
        return obj["标签类型"],  s_dir, s_tag
    def get_before_info(self):
        if self.texts:
            obj = LLMTool.recog_before_info2(self.agent,self.texts)
            if not obj["account_type"]:
                if obj["account_num"].startswith("62"):
                    obj["account_type"] = '对私'
                elif not obj["account_name"]:
                    obj["account_type"] ="unknown"
                else:
                    obj["account_type"] = "对私" if   self.et.person_or_org(obj["account_name"]) =="PERSON" else "对公"
            if self.agent == "bank" and obj["bank_name"]:
                if obj["bank_name"] in dicts.bank_code_dict:
                    obj["bank_name"] = dicts.bank_code_dict[obj["bank_name"]]
                else:
                    l = [(k,code,Levenshtein.distance(obj["bank_name"], k))for k ,code in dicts.bank_code_dict.items()]
                    min_distance = min([d for (_,_,d) in l])
                    for k,code,d in l:
                        if d == min_distance:
                            obj["bank_name"] = code
            self.obj['res1'].update(obj)
            if "begin_date" in self.obj['res1']:
                self.obj['res1']["begin_date"] = self.normalize_date_format(self.obj['res1']["begin_date"])
            if "end_date" in self.obj['res1']:
                self.obj['res1']["end_date"] = self.normalize_date_format(self.obj['res1']["end_date"])

            self.account_class = self.get_account_class(obj["account_name"]) if obj["account_name"] else ""
        else:
            self.obj['res1']["account_type"] = "unknown"
            self.account_class = ""
    

            
    def get_accounting_entry(self,row_obj,accounting_item):
        account_type = "对公" if self.obj['res1']["account_type"] =="unknown" else self.obj['res1']["account_type"]
        pay_type_key = dicts.pay_type_dict[self.agent]
        pay_type = row_obj[pay_type_key]
        if not pay_type or pay_type=="其他":
            return ""
        if not accounting_item :return ""
        return self.lable_conf[(account_type, pay_type)][accounting_item][1]
        #asset_accounts_dict, name_code_dict = get_asset_accounts_dict()

        #return asset_accounts_dict[account_type][pay_type][accounting_item]['accounting_entry']
    


    def predict_account_labelv2(self, row_obj,pay_type,trader_nature,row_data):


        return self.get_label(pay_type,trader_nature,json.dumps(row_data,ensure_ascii=True))
        #return LLMTool.get_account_labelv2(self.obj['res1']["account_type"], pay_type, text)
    

    def recog_income_or_expenses(self,row):
        text = '\n'.join([f'{k}:{v}'for k,v in row.items() if v and v !='其他'])
        prompt = Prompts.create_prompt(Prompts.income_or_expenses_prompt,{"text":text})
        obj = self.llm.predict_respond_json(prompt)
        return obj.get('收支类型','')
    def get_recoged_obj(self):
        self.get_agent()
        self.get_before_info()
        self.field_align()
        del self.obj['res1']['outside_infos']
        return self.obj
    
    def normalize_date_format(self,date_str):
        date_str = date_str.replace(" ","")
        if not date_str:return ""
        
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
        print(f"cannot normalize date format: {date_str}")
        return ""
    def normalize_money_format(self,money_str):
        money_str = money_str.replace(',','')
        
        try:
            money =  float(money_str)
            return money
        except:
            raise Exception(f"money normalize failed: {money_str}")
if __name__ == "__main__":
    import os
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64"
    #file_path = "data/output/攀德中国银行流水2021年.xlsx.txt"
    file_path = "data/output/支付宝1.pdf.txt"
    #file_path = "data/output/2022攀农业银行1-9月流水.xls.txt"
    #file_path = "data/output/1671079320085_1588774.pdf.txt"
    #file_path = "data/output/支付宝流水.pdf.xlsx.txt"
    #file_path = "data/output/李佳蔚.xlsx.txt"
    #file_path = "data/outputa/建行.xls.txt"
    #file_path = "data/output/张凌玮.xlsx.txt"
    file_path = "data/output/微信交易明细.pdf.txt"
    #torch.multiprocessing.set_start_method('spawn')
    #self.et.init()
    CONF.max_worker = 1
    RecogInfo.init()
    
    with open(file_path,'r',encoding="utf-8") as f:
        with open ('data/out.json','w',encoding='utf-8') as fo:
            obj = json.load(f)
            obj = RecogInfo(obj).get_recoged_obj()
            json.dump(obj,fo,ensure_ascii=False)
    