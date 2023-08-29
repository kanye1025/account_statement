from config.config import CONF
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import numpy as np
from config import  dicts
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
    def get_embeding_list(cls,text_list,is_query = False):
        if is_query:
            return [cls.embeding.embed_query(text) for text in text_list]
        else:
            return cls.embeding.embed_documents(text_list)
            
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
        return  np.dot(q, k) / (np.linalg.norm(q) * np.linalg.norm(k))
        #return  np.dot(q, k)
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
    agent_embeding = EmbedingToolBasic.get_embeding_dict(dicts.agent_dict)
    
    field_embeding = {}
    for agent,key_dict in  dicts.field_dict.items():
        field_embeding[agent] = EmbedingToolBasic.get_embeding_dict(key_dict,is_query=True)
    account_label_embeding= {}
    for pay_type,label_dict in dicts.account_label_dict.items():
        account_label_embeding[pay_type] = EmbedingToolBasic.get_embeding_dict(label_dict)
        
    bank_field_type_split_embeding = {k: EmbedingToolBasic.get_embeding_list(v,is_query=True) for k,v in dicts.bank_field_type_split.items()}
    bank_field_type_join_embeding = EmbedingToolBasic.get_embeding_dict(dicts.bank_field_type_join)
    alipay_field_type_split_embeding = {k: EmbedingToolBasic.get_embeding_list(v, is_query=True) for k, v in
                                      dicts.alipay_field_type_split.items()}
    alipay_field_type_join_embeding = EmbedingToolBasic.get_embeding_dict(dicts.alipay_field_type_join)

    @classmethod
    def get_account_label(cls,pay_type,text):
        class_embeding = cls.account_label_embeding[pay_type]
        return EmbedingToolBasic.classify_by_embeding_dict(class_embeding,text=text)
    @classmethod
    def get_bank_type(cls,head_dict):
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        match_fields = set()
        for _ ,embeding_list in cls.bank_field_type_split_embeding.items():
            for emb in embeding_list:
                match_field = EmbedingToolBasic.classify_by_embeding_dict(text_emb=emb,class_dict=head_embeding_dict)
                match_fields.add(head_dict[match_field])
        match_fields = ','.join(list(match_fields))
        bank_type = EmbedingToolBasic.classify_by_embeding_dict(text=match_fields,class_dict=cls.bank_field_type_join_embeding)
        return bank_type
        
    @classmethod
    def get_alipay_type(cls,head_dict):
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        match_fields = set()
        for _, embeding_list in cls.alipay_field_type_split_embeding.items():
            for emb in embeding_list:
                match_field = EmbedingToolBasic.classify_by_embeding_dict(text_emb=emb, class_dict=head_embeding_dict)
                match_fields.add(head_dict[match_field])
        match_fields = ','.join(list(match_fields))
        alipay_type = EmbedingToolBasic.classify_by_embeding_dict(text=match_fields,
                                                                class_dict=cls.alipay_field_type_join_embeding)
        return alipay_type
    @classmethod
    def get_head_index(cls,rows):
        row_texts = [','.join(row) for row in rows if row]
        results = EmbedingToolBasic.detect_text_in_list(dicts.head,row_texts)
        return [r[0] for r in results]
        
    @classmethod
    def recog_agent(cls,text):
        return EmbedingToolBasic.classify_by_embeding_dict(class_dict=cls.agent_embeding,text = text)

    @classmethod
    def recog_field(cls,agent,head_dict):
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        embeding_dict = cls.field_embeding[agent]
        
        ret = {}
        for k,q in embeding_dict.items():
            head_index = EmbedingToolBasic.classify_by_embeding_dict(text_emb=q,class_dict=head_embeding_dict)
            ret[k] = head_index
        return ret
        
    
    