from transformers import AutoModel, AutoTokenizer
from peft import PeftModel

class ChatGLM:
    
    peft_model = "root/autodl-tmp/FinGPT_v31_ChatGLM2_Sentiment_Instruction_LoRA_FT"
    tokenizer = AutoTokenizer.from_pretrained("/root/autodl-tmp/chatglm2-6b-int4", trust_remote_code=True)
    model = AutoModel.from_pretrained("/root/autodl-tmp/chatglm2-6b-int4", trust_remote_code=True).cuda()
    model = PeftModel.from_pretrained(model, peft_model)
    model.eval()
    @classmethod
    def predict(cls,txt,top_p = None,max_length=256,temperature=0.75):
        if top_p:
            response, history = cls.model.chat(cls.tokenizer, txt,top_p = top_p,max_length = max_length)
        else:
            response, history = cls.model.chat(cls.tokenizer, txt, temperature=temperature, max_length=max_length)
        return response