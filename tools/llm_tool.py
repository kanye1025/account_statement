from transformers import AutoModel, AutoTokenizer
from peft import PeftModel
import re

import json

class ChatGLM:
    peft_model = "/root/autodl-tmp/FinGPT_v31_ChatGLM2_Sentiment_Instruction_LoRA_FT"
    tokenizer = AutoTokenizer.from_pretrained("/root/autodl-tmp/chatglm2-6b-int4", trust_remote_code=True)
    model = AutoModel.from_pretrained("/root/autodl-tmp/chatglm2-6b-int4", trust_remote_code=True).cuda()
    #model = PeftModel.from_pretrained(model, peft_model)
    model.eval()
    
    @classmethod
    def predict(cls, txt, top_p=None, max_length=256, temperature=0.75):
        if top_p:
            response, history = cls.model.chat(cls.tokenizer, txt, top_p=top_p, max_length=max_length)
        else:
            response, history = cls.model.chat(cls.tokenizer, txt, temperature=temperature, max_length=max_length)
        return response
class LLMTool:
    recog_before_info_prompts = {}
    recog_before_info_prompts["bank"] = """
    请在下列文本信息中识别银行名称，银行账号，账户名，账户类型（公司/个人），
    并以如下json格式返回
    ```json
    {
    "银行名称":"",
    "银行账号":"",
    "账户名":"",
    "账户类型":""
    }
    文本信息开始【
    {text}
    】文本信息结束
    请只返回json数据
    """
    
    recog_before_info_prompts["alipay"] = """
    请在下列文本信息中识别支付宝账户，姓名，身份证号码，账户类型（对公/对私），
    并以如下json格式返回
    ```json
    {
    "支付宝账户":"",
    "姓名":"",
    "身份证号码":"",
    "账户类型":""
    }
    文本信息开始【
    {text}
    】文本信息结束
    请只返回json数据
    """
    
    recog_before_info_prompts["wechat"] = """
    请在下列文本信息中识别微信账号，姓名，身份证号，账户类型（对公/对私），
    并以如下json格式返回
    ```json
    {
    "微信账号":"",
    "姓名":"",
    "身份证号":"",
    "账户类型":""
    }
    文本信息开始【
    {text}
    】文本信息结束
    请只返回json数据
    """
    
    before_info_keys = {
        "bank":[
            ("bank_name","银行名称"),
            ("accout_num", "银行账号"),
            ("account_name", "账户名"),
            ("account_type", "账户类型"),
        ],
        "alipay": [
            ("accout_num", "支付宝账户"),
            ("account_name", "姓名"),
            ("idcard_num", "身份证号码"),
            ("account_type", "账户类型"),
        ],
        "wechat": [
            ("accout_num", "微信账号"),
            ("account_name", "姓名"),
            ("idcard_num", "身份证号"),
            ("account_type", "账户类型")
        ]
    }
    @classmethod
    def recog_before_info(cls,agent_type,text):
        account_type_dict = {
            "个人":"对私",
            "公司":"对公",
            "":""
        }
        prompt = cls.recog_before_info_prompts[agent_type]
        message = prompt.replace("{text}",text)
        respond = ChatGLM.predict(message,top_p=0.75,max_length=8096)
        resobj = cls.analysis_json_obj(respond)
        key_pairs = cls.before_info_keys[agent_type]
        obj = {}
        for code,name in key_pairs:
            if name in resobj:
                obj[code] = resobj[name]
                if code == "account_type":
                    obj[code] = account_type_dict[obj[code]]
        return obj
        
    @classmethod
    def analysis_json_obj(cls,respond):
        p = r"\{[\s\S]*\}"
        response = re.search(p, respond)
        response = response.group()
        return json.loads(response)
        
    