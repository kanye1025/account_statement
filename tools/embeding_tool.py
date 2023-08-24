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
    def get_embeding_dict(cls,text_dict):
        embeding_dict = {}
        for k,v in text_dict.items():
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
    def classify_by_embeding_dict(cls,text,class_dict):
        text_emb = cls.get_query_embeding(text)
        ret = list()
        for k,e in class_dict.items():
            s = cls.sim(text_emb,e)
            ret.append((k,s))
        ret = sorted(ret,key=lambda x:x[1],reverse=True)
        return ret[0][0]
    
        
class EmbedingTool:
    head = "流水号/订单号,时间,收入,支出,备注/用途,余额/金额,对方账号,对方户名,收付款方式,开户机构/开户行,分类"
    recog_embeding = None
    @classmethod
    def get_head_index(cls,rows):
        row_texts = [','.join(row) for row in rows if row]
        results = EmbedingToolBasic.detect_text_in_list(cls.head,row_texts)
        return [r[0] for r in results]
        
    @classmethod
    def recog_agent(cls,text):
        if not cls.recog_embeding:
            d = {"bank":"银行,bank","alipay":"支付宝,alipay","wechat":"微信支付,wechat"}
            cls.recog_embeding = EmbedingToolBasic.get_embeding_dict(d)
        return EmbedingToolBasic.classify_by_embeding_dict(text,cls.recog_embeding)
        