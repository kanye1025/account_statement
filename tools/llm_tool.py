
from config import dicts
from functools import lru_cache
#from peft import PeftModel
from copy import deepcopy
from .chatglm import ChatGLM
from .baichuan import Baichuan
from config.load_asset_accounts_dict import get_asset_accounts_desc_dict

from collections import Counter

import json

class LLMTool:
    
    recog_befor_info_des = {}
    recog_befor_info_des["bank"] = {
"银行名称":"银行或开户行名称，若干汉字，通常会包含'银行'或者'信用'，有时带'支行'",
"银行账号":"银行账号，通常是一串数字",
"账户名":"账户名，通常是人名或公司、机构名，中文汉字",
"账户名类型":"账户名类型，如果账户名是人名，就返回'个人'，如果是公司、机构名就返回'公司'",
"开始日期":"流水的开始日期，通常与结束日期一起出现，在结束日期前面，非必须",
"结束日期":"流水的结束日期，通常与开始日期一起出现，在开始日期后面，非必须"
}
    recog_befor_info_des["alipay"] = {
"支付宝账户":"支付宝账户名，通常是一串英文字母或者阿拉伯数字,或者二者混合,也可能是邮箱地址",
"姓名":"人名或者公司、机构名,中文汉字",
"身份证号码":"身份证号码,通常是一串数字，也可能是一串数字+x结尾,不一定有",
"姓名类型":"账户类型,如果账户名是人名，就返回个人，如果是公司、机构名就返回公司",
"开始日期":"流水的开始日期，通常与结束日期一起出现，在结束日期前面，非必须",
"结束日期":"流水的结束日期，通常与开始日期一起出现，在开始日期后面，非必须"
}
    recog_befor_info_des["wechat"] = {
"微信账号":"微信账号，通常是一串英文字母或者阿拉伯数字，或者二者混合",
"姓名":"人名或者公司、机构名,中文汉字",
"身份证号码":"身份证号码,通常是一串数字，也可能是一串数字+x结尾,不一定有",
"姓名类型":"账户类型,如果账户名是人名，就返回个人，如果是公司、机构名就返回公司",
"开始日期":"流水的开始日期，通常与结束日期一起出现，在结束日期前面，非必须",
"结束日期":"流水的结束日期，通常与开始日期一起出现，在开始日期后面，非必须"
}

    recog_before_info_prompt = """
信息提取任务：
已知字段名和对应的字段说明
字段说明开始【
{des}
】字段说明结束

请根据字段说明在下述文本信息中提取上述字段：

文本信息开始【
{text}
】文本信息结束

提取后的信息按照如下json格式返回
```json格式
{json}
```
未识别字段返回"未识别"
"""

    recog_before_info_prompt2 = """问：
已知，【{key}】是指{des}
现在有一段文字：
{text}
那么，这段文字中的【{key}】是什么？如果没有就回答【未知】
答：文字里的【{key}】是【"""
    
    before_info_keys = {
        "bank":[
            ("bank_name","银行名称"),
            ("account_num", "银行账号"),
            ("account_name", "账户名"),
            ("account_type", "账户名类型"),
            ("begin_date", "开始日期"),
            ("end_date", "结束日期"),
        ],
        "alipay": [
            ("account_num", "支付宝账户"),
            ("account_name", "姓名"),
            ("idcard_num", "身份证号码"),
            ("account_type", "姓名类型"),
            ("begin_date", "开始日期"),
            ("end_date", "结束日期"),
        ],
        "wechat": [
            ("account_num", "微信账号"),
            ("account_name", "姓名"),
            ("idcard_num", "身份证号码"),
            ("account_type", "姓名类型"),
            ("begin_date", "开始日期"),
            ("end_date", "结束日期"),
        ]
    }
    
    before_info_code_dicts = {agent:{name:code for code,name in d}    for agent,d in before_info_keys.items()}
    filed_recog_prompt = """给定一些标签id和标签的说明，
{field_text}
请从以下原json数据中，提取标签对应的值，并返回如下json格式
```
{json_format}
```

以下是原json数据
```
{table_text}
```
请返回提取后的json
"""

    account_label_prompt = """已知交易流水的类型标签和说明（格式为 标签类型-->标签说明）：
{des}
请判断下列交易流水信息的标签类型，并返回如下json
```{
"标签类型":""
}```
取值只能为{key}中的一个,
流水信息：
{text}

"""
    asset_accounts_desc_dict = get_asset_accounts_desc_dict()
    baichuan = Baichuan()
    @classmethod
    def init(cls):
        #ChatGLM.init()
        pass
    @classmethod
    def recog_field(cls,agent_type,head_value_dict):
        value_head_dict = {v:h for h,v in head_value_dict.items()}
        field_dict = deepcopy(dicts.field_dict[agent_type])
        ret_obj = {}
        prompt = deepcopy(cls.filed_recog_prompt)
        temperature = 0.01
        field_count = len(field_dict)
        for i in range(field_count*2):
            if not len(field_dict):
                break
            if temperature>5:
                break
            #table_text = '\n'.join([f"{v}:{k}" for k, v in value_head_dict.items()])
            table_text = json.dumps(head_value_dict,ensure_ascii=False)
            field_text = '\n'.join([f"{k} :表示{v}" for k, v in field_dict.items()])
            json_format = {k:"" for k in field_dict}
            json_format = json.dumps(json_format,ensure_ascii=False)
            message = prompt.replace("{table_text}",table_text).replace("{field_text}",field_text).replace("{json_format}",json_format)
            #ret = ChatGLM.predict(message,max_length=8096,temperature =temperature,do_sample=False)
            #resobj = ChatGLM.predict_respond_json(message,1024,temperatures=[temperature,temperature*2,temperature*4])
            resobj = cls.baichuan.predict_respond_json(message,1024,temperatures=[temperature,temperature*2,temperature*4])
            c = Counter()
            for v in resobj.values():
                c.update({v:1})
            
            find_count = 0
            for k,v in resobj.items():
                if v in c and c[v]>1:
                    continue
                if k in field_dict :
                    if v in value_head_dict:
                        h = value_head_dict[v]
                    elif v in head_value_dict:
                        h = v
                        v = head_value_dict[h]
                    else:
                        continue
                    ret_obj[k] = h
                    del field_dict[k]
                    del value_head_dict[v]
                    del head_value_dict[h]
                    find_count+=1
            if find_count == 0:
                temperature*=5
            else:
                temperature = 0.01
        for   k in field_dict.keys():
            ret_obj[k] = ""
        return ret_obj

    @classmethod
    def recog_before_info(cls, agent_type, text):
        account_type_dict = {
            "个人": "对私",
            "公司": "对公",
            "个人名": "对私",
            "公司名": "对公",
            "机构名": "对公",
            "对私": "对私",
            "对公": "对公",
            "":   ""
        }
        recog_befor_info_des = {cls.before_info_code_dicts[agent_type][k]:v  for k,v in cls.recog_befor_info_des[agent_type].items()}
        obj = {k:"" for k,v in cls.before_info_keys[agent_type]}
        temperature = 0.01
        for i in range(5):
            if not recog_befor_info_des:
                break
            prompt = deepcopy(cls.recog_before_info_prompt)
            message = prompt.replace("{text}", text).\
                replace("{des}",json.dumps(recog_befor_info_des,ensure_ascii=False)).\
                replace("{json}",json.dumps({k:"" for k,v in recog_befor_info_des.items()},ensure_ascii=False))
            #print("begin predict base info")
            #resobj = ChatGLM.predict_respond_json(message, max_length=1024,temperatures = [temperature])
            resobj = cls.baichuan.predict_respond_json(message, max_length=1024, temperatures=[temperature])
            #print("end predict base info")

            for code in cls.before_info_keys[agent_type]:
                if code in resobj:
                    if not resobj[code] or resobj[code] in ("未识别","unknow","xxx","未知"):
                        continue
                    obj[code] = resobj[code]
                    del recog_befor_info_des[code]
                    if code == "account_type" :
                        if obj["account_type"] in account_type_dict:
                            obj["account_type"] = account_type_dict[obj["account_type"]]
                        else:
                            obj[code] = ""
            temperature*=2.5
        return obj
    @classmethod
    def recog_before_info2(cls, agent_type, text):
        account_type_dict = {
            "人名": "对私",
            "个人":  "对私",
            "公司":  "对公",
            "机构":   "对公",
            "个人名": "对私",
            "公司名": "对公",
            "机构名": "对公",
            "对私":  "对私",
            "对公":  "对公",
            "":    ""
        }
        
        obj = {}
        for key,des in cls.recog_befor_info_des[agent_type].items():
            prompt = deepcopy(cls.recog_before_info_prompt2)
            message = prompt.replace("{text}", text).replace("{key}",key).replace("{des}",des)
            
            #res = ChatGLM.predict(message, max_length=1024, temperature=0.01,do_sample=False)
            res = cls.baichuan.predict(message, max_length=1024, temperature=0.01, do_sample=False)
            res = res.split("】")[0]
            if res in  ("未知","unknown"):
                res = ""
            obj[key] = res
        obj = {cls.before_info_code_dicts[agent_type][k]:v for k,v in obj.items()}
        
        
        
        if obj["account_type"] in account_type_dict:
            obj["account_type"] = account_type_dict[obj["account_type"]]
        else:
            obj[key] = ""
        
        return obj
    
    @classmethod
    @lru_cache(None)
    def get_account_labelv2(cls, person_org,pay_type, text):
        if pay_type not in ("收入","支出"):return ""
        person_org = "对私" if person_org =="对私" else "对公"  #unknown 也当对公处理
        account_label_des = cls.asset_accounts_desc_dict[person_org][pay_type]
        des = '\n'.join([f"{k}-->{v}"for k,v in account_label_des.items()])
        prompt = deepcopy(cls.account_label_prompt)
        message = prompt.replace("{text}", text).replace("{des}", des).replace("{key}",str([i for i in account_label_des.keys()]))
        #obj = ChatGLM.predict_respond_json(message)
        obj = cls.baichuan.predict_respond_json2(message,'{"标签类型":',temperatures=[0.01,0.3,0.75])
        print(f"{[person_org,pay_type,text]}-->{obj['标签类型']}")
        if obj["标签类型"] not in account_label_des.keys():
            return ""
        return obj["标签类型"]