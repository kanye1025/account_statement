from transformers import AutoModel, AutoTokenizer
import torch
from config.config import CONF
import re
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