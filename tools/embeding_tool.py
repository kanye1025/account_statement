from config.config import CONF
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import numpy as np
class EmbedingToolBasic:
    embeding = HuggingFaceEmbeddings(model_name=CONF.embeding_model_path)
    #h_emb = embeding.embed_query(heads)
    @classmethod
    def detect_text_in_list(cls,query,candidates):
        q_emb = cls.embeding.embed_query(query)
        candidates_emb = cls.embeding.embed_documents(candidates)
        results = list()
        for i, e in enumerate( candidates_emb):
            s = np.dot(q_emb, e)
            results.append((  i,s))
        #results = sorted(results, key=lambda x: x[1], reverse=True)
        max_score = max([r[1] for r in results])
        results = filter(lambda x: x[1] == max_score, results)
        return list(results)
    
    @classmethod
    def get_embeding_dict(cls,text_dict,is_query = False):
        embeding_dict = {}
        for k,v in text_dict.items():
            if is_query:
                e = cls.embeding.embed_query(v)
            else:
                e = cls.embeding.embed_documents([v])[0]
            embeding_dict[k] = e
        return embeding_dict
    
    @classmethod
    def get_query_embeding(cls,query):
        return cls.embeding.embed_query(query)
    @classmethod
    def sim(cls,q,k):
        return  np.dot(q, k)
    @classmethod
    def classify_by_embeding_dict(cls,class_dict,text = None ,text_emb  = None):
        if not text_emb:
            text_emb = cls.get_query_embeding(text)
        ret = list()
        for k,e in class_dict.items():
            s = cls.sim(text_emb,e)
            ret.append((k,s))
        ret = sorted(ret,key=lambda x:x[1],reverse=True)
        return ret[0][0]
    
        
class EmbedingTool:
    head = "流水号/订单号,时间,收入,支出,备注/用途,余额/金额,对方账号,对方户名,收付款方式,开户机构/开户行,分类"
    agent_dict = {"bank": "银行,bank", "alipay": "支付宝,alipay", "wechat": "微信,wechat"}
    agent_embeding = EmbedingToolBasic.get_embeding_dict(agent_dict)
    field_dict = {
        "bank":{
            "交易日期":"交易日期",
            "交易金额":"交易金额",
            "收支类型": "收支类型，收/支",
            "余额":"账户余额",
            "备注（摘要）":"备注,摘要",
            "对方账号":"对方账号",
            "对方户名":"对方户名"
        },
        "wechat":{
            "交易日期":"交易日期,日期,时间",
            "交易类型": "交易类型,类型",
            "收/支/其他": "收支类型，收/支",
            "交易方式": "交易方式,方式",
            "交易金额": "交易金额,金额",
            "交易对方": "交易对方,对方账户,对方户名",
        },
        "alipay":{
            "收/支": "收支类型，收/支",
            "交易对方": "交易对方",
            "商品说明": "商品说明",
            "收/付款方式": "收/付款方式",
            "金额": "金额",
            "交易日期": "交易日期",
        }
    }
    field_embeding = {}
    for agent,key_dict in  field_dict.items():
        field_embeding[agent] = EmbedingToolBasic.get_embeding_dict(key_dict,is_query=True)
        
    @classmethod
    def get_head_index(cls,rows):
        row_texts = [','.join(row) for row in rows if row]
        results = EmbedingToolBasic.detect_text_in_list(cls.head,row_texts)
        return [r[0] for r in results]
        
    @classmethod
    def recog_agent(cls,text):
        return EmbedingToolBasic.classify_by_embeding_dict(class_dict=cls.agent_embeding,text = text)
    @classmethod
    def recog_field(cls,agent,head_dict):
        
        head_embeding_dict =  EmbedingToolBasic.get_embeding_dict(head_dict)
        embeding_dict = cls.field_embeding[agent]
        ret = {}
        for k,q in embeding_dict.items():
            head_index = EmbedingToolBasic.classify_by_embeding_dict(text_emb=q,class_dict=head_embeding_dict)
            ret[k] = head_index
        return ret
        
    
    