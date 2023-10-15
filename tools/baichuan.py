import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.utils import GenerationConfig
from config.config import CONF
import os
import torch
#from peft import PeftModel
from copy import deepcopy
import re
from collections import Counter

import json

class Baichuan:
    
    def __init__(self):
        
        self.tokenizer = AutoTokenizer.from_pretrained(CONF.llm_model_path, use_fast=False,
                                                       trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(CONF.llm_model_path, device_map="auto",
                                                          torch_dtype=torch.bfloat16, trust_remote_code=True)
        self.model.generation_config = GenerationConfig.from_pretrained(CONF.llm_model_path)
        
        
        # model = PeftModel.from_pretrained(model, peft_model)
        if torch.cuda.is_available() and CONF.GPU:
            self.model = self.model.cuda()
            self.device = torch.device("cuda")
            print("use gpu ")
        else:
            self.model = self.model.float()
            self.device = torch.device("cpu")
            print("use cpu")
        self.model.eval()
   
    
    
    def predict_respond_json(self, txt,  max_length=8196, temperatures=[0.01,0.35,0.75,1],do_sample = True):
        txt = "问:" + txt + "\n\n答:好的，提取的json数据为\n```{"
        for temperature in temperatures:
            try:
                respond = self.predict(txt,temperature = temperature,do_sample = do_sample)
                respond = '{' + respond
                obj = self.analysis_json_obj(respond)
                return obj
            except Exception as e :
                print(e.args)
                continue
        raise Exception(f"wrong respond:  text:{txt}")
    
    def predict_respond_json2(self, txt, pre, max_length=8196, temperatures=[0.01,0.35,0.75,1],do_sample = True):
        txt = "问:" + txt + "\n\n答:好的，提取的json数据为\n```"+pre
        for temperature in temperatures:
            try:
                respond = self.predict(txt,temperature = temperature,do_sample = do_sample)
                respond = pre + respond
                obj = self.analysis_json_obj(respond)
                return obj
            except Exception as e :
                print(e.args)
                continue
        raise Exception(f"wrong respond:  text:{txt}")
    
    def analysis_json_obj(self, respond):
        try:
            p = r"\{[\s\S]*\}"
            response = re.search(p, respond)
            response = response.group()
            return json.loads(response)
        except Exception as e:
            raise Exception(f"wrong respond:{respond}")
        
    def predict(self, txt, max_length=256, temperature=0.75,do_sample = True,**kwargs):
        inputs = self.tokenizer([txt], return_tensors="pt").to(self.device)
        if max_length<10:
            max_length = int(len(inputs['input_ids'][0])*max_length)
        gen_kwargs = {
            #"max_length":  max_length,
            "do_sample": do_sample,
                      "temperature": temperature, **kwargs}
        outputs = self.model.generate(**inputs, **gen_kwargs)
        outputs = outputs.tolist()[0][len(inputs["input_ids"][0]):]
        response = self.tokenizer.decode(outputs)
        response = self.process_response(response)
        return response
    
    
    def process_response(self, response):
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