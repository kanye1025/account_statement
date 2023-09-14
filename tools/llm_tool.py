from transformers import AutoModel, AutoTokenizer
from config.config import CONF
from config import dicts
import torch
#from peft import PeftModel
from copy import deepcopy
import re
from collections import Counter

import json

class ChatGLM:
    @classmethod
    def init(cls):
        # peft_model = "/root/autodl-tmp/FinGPT_v31_ChatGLM2_Sentiment_Instruction_LoRA_FT"
        cls.tokenizer = AutoTokenizer.from_pretrained(CONF.llm_model_path, trust_remote_code=True)
        cls.model = AutoModel.from_pretrained(CONF.llm_model_path, trust_remote_code=True)
        # model = PeftModel.from_pretrained(model, peft_model)
        if torch.cuda.is_available() and CONF.GPU:
            cls.model = cls.model.cuda()
            cls.device = torch.device("cuda")
            print("use gpu ")
        else:
            cls.model = cls.model.float()
            cls.device = torch.device("cpu")
            print("use cpu")
        cls.model.eval()
    @classmethod
    def predict(cls, txt, max_length=256, temperature=0.75,do_sample = True,**kwargs):
        inputs = cls.tokenizer([txt], return_tensors="pt").to(cls.device)
        gen_kwargs = {"max_length":  max_length, "do_sample": do_sample,
                      "temperature": temperature, **kwargs}
        outputs = cls.model.generate(**inputs, **gen_kwargs)
        outputs = outputs.tolist()[0][len(inputs["input_ids"][0]):]
        response = cls.tokenizer.decode(outputs)
        response = cls.process_response(response)
        '''
        if top_p:
            response, history = cls.model.generate(cls.tokenizer, txt, top_p=top_p, max_length=max_length,do_sample = do_sample)
        else:
            response, history = cls.model.generate(cls.tokenizer, txt, temperature=temperature, max_length=max_length,do_sample = do_sample)
        '''
        return response

    @classmethod
    def process_response(cls, response):
        response = response.strip()
        response = response.replace("[[训练时间]]", "2023年")
        punkts = [
            [",", "，"],
            ["!", "！"],
            [":", "："],
            [";", "；"],
            ["\?", "？"],
        ]
        for item in punkts:
            response = re.sub(r"([\u4e00-\u9fff])%s" % item[0], r"\1%s" % item[1], response)
            response = re.sub(r"%s([\u4e00-\u9fff])" % item[0], r"%s\1" % item[1], response)
        return response
    @classmethod
    def predict_respond_json(cls, txt,  max_length=8196, temperatures=[0.01,0.35,0.75,1]):
        txt = "问:"+txt+"\n\n答:好的，根据上面的信息提取的json数据为\n```{"
        for temperature in temperatures:
            try:
                respond = cls.predict(txt,max_length=max_length,temperature = temperature,do_sample = True)
                respond = '{'+respond
                obj = cls.analysis_json_obj(respond)
                return obj
            except Exception as e :
                print(e.args)
                continue
        raise Exception(f"wrong respond:  text:{txt}")

    @classmethod
    def predict_respond_json2(cls, txt,json_pre, max_length=8196, temperatures=[0.01, 0.35, 0.75, 1]):
        txt = txt+json_pre
        for temperature in temperatures:
            try:
                respond = cls.predict(txt, max_length=max_length, temperature=temperature, do_sample=False)
                respond = json_pre + respond
                obj = cls.analysis_json_obj(respond)
                return obj
            except Exception as e:
                print(e.args)
                continue
        raise Exception(f"wrong respond:  text:{txt}")
    @classmethod
    def analysis_json_obj(cls, respond):
        try:
            p = r"\{[\s\S]*\}"
            response = re.search(p, respond)
            response = response.group()
            return json.loads(response)
        except Exception as e:
            raise Exception(f"wrong respond:{respond}")
class LLMTool:
    
    recog_befor_info_des = {}
    recog_befor_info_des["bank"] = {
"银行名称":"银行或开户行名称，若干汉字，通常会包含'银行'或者'信用'，有时带'支行'",
"银行账号":"银行账号，通常是一串数字",
"账户名":"账户名，通常是人名或公司、机构名，中文汉字",
"账户名类型":"账户名类型，如果账户名是人名，就返回'个人'，如果是公司、机构名就返回'公司'",
"开始日期":"开始日期，流水开始的日期，非必须",
"结束日期":"结束日期，流水结束的日期，非必须"
}
    recog_befor_info_des["alipay"] = {
"支付宝账户":"支付宝账户名，通常是一串英文字母或者阿拉伯数字，或者二者混合",
"姓名":"人名或者公司、机构名,中文汉字",
"身份证号码":"身份证号码,通常是一串数字，也可能是一串数字+x结尾,不一定有",
"姓名类型":"账户类型,如果账户名是人名，就返回个人，如果是公司、机构名就返回公司",
"开始日期":"开始日期，流水开始的日期，不一定有",
"结束日期":"结束日期，流水结束的日期，不一定有"
}
    recog_befor_info_des["wechat"] = {
"微信账号":"微信账号，通常是一串英文字母或者阿拉伯数字，或者二者混合",
"姓名":"人名或者公司、机构名,中文汉字",
"身份证号码":"身份证号码,通常是一串数字，也可能是一串数字+x结尾,不一定有",
"姓名类型":"账户类型,如果账户名是人名，就返回个人，如果是公司、机构名就返回公司",
"开始日期":"开始日期，流水开始的日期，不一定有",
"结束日期":"结束日期，流水结束的日期，不一定有"
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
    
    @classmethod
    def init(cls):
        ChatGLM.init()
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
            resobj = ChatGLM.predict_respond_json(message,1024,temperatures=[temperature,temperature*2,temperature*4])
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
            resobj = ChatGLM.predict_respond_json(message, max_length=1024,temperatures = [temperature])
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
    