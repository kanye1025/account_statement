from config.config import CONF
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import numpy as np
from config import  dicts

class EmbedingToolBasic:
    

    @classmethod
    def init(cls):
        cls.device = 'cuda' if CONF.GPU else 'cpu'
        cls.embeding = HuggingFaceEmbeddings(model_name=CONF.embeding_model_path, model_kwargs={'device': cls.device})
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
    def classify_by_embeding_dict(cls,class_dict,text = None ,text_emb  = None,top_k =None):
        if not text_emb:
            text_emb = cls.get_query_embeding(text)
        ret = list()
        for k,e in class_dict.items():
            s = cls.sim(text_emb,e)
            ret.append((k,s))
        if not top_k:
            ret = sorted(ret,key=lambda x:x[1],reverse=True)
            return ret[0][0]
        else:
            ret = sorted(ret, key=lambda x: x[1], reverse=True)[:top_k]
            return ret
    @classmethod
    def detect_texts_in_texts(cls, embeding_dict_super,embeding_dict_sub):
        pre_dict = {}
        for sub_key,q_embeding in embeding_dict_sub.items():
            pre_dict[sub_key] = cls.classify_by_embeding_dict(embeding_dict_super,text_emb = q_embeding,top_k=2)
        sort_dict = {}
        for q,r in pre_dict.items():
            k,s = r[0]
            if k not in sort_dict or sort_dict[k][1]<s:
                sort_dict[k] = (q,s)
        ret_dict = {k:'' for k in embeding_dict_sub.keys()}
        for k ,(q,s)in sort_dict.items():
            ret_dict[q] = k
            del pre_dict[q]
            
        sort_dict = {}
        for q, r in pre_dict.items():
            k, s = r[1]
            if k not in sort_dict or sort_dict[k][1] < s:
                sort_dict[k] = (q, s)
        for k ,(q,s)in sort_dict.items():
            ret_dict[q] = k
            del pre_dict[q]
        return ret_dict
        
                
                
                
        
        
    
class EmbedingTool:
    
    
    @classmethod
    def init(cls):
        cls.agent_embeding = EmbedingToolBasic.get_embeding_dict(dicts.agent_dict)
    
        cls.field_embeding = {}
        for agent, key_dict in dicts.field_dict.items():
            cls.field_embeding[agent] = EmbedingToolBasic.get_embeding_dict(key_dict, is_query=True)
        cls.account_label_embeding = {}
        for pay_type, label_dict in dicts.account_label_dict.items():
            cls.account_label_embeding[pay_type] = EmbedingToolBasic.get_embeding_dict(label_dict)
    
        cls.bank_field_type_split_embeding = {k: EmbedingToolBasic.get_embeding_list(v, is_query=True) for k, v in
                                          dicts.bank_field_type_split.items()}
        cls.bank_field_type_join_embeding = EmbedingToolBasic.get_embeding_dict(dicts.bank_field_type_join)
        cls.alipay_field_type_split_embeding = {k: EmbedingToolBasic.get_embeding_list(v, is_query=True) for k, v in
                                            dicts.alipay_field_type_split.items()}
        cls.alipay_field_type_join_embeding = EmbedingToolBasic.get_embeding_dict(dicts.alipay_field_type_join)
    
        cls.person_organization_embeding = EmbedingToolBasic.get_embeding_dict(dicts.person_organization_dict)
    
    @classmethod
    def person_or_org(cls,text):
        return EmbedingToolBasic.classify_by_embeding_dict(cls.person_organization_embeding,text)
    @classmethod
    def get_account_label(cls,pay_type,text):
        class_embeding = cls.account_label_embeding[pay_type]
        return EmbedingToolBasic.classify_by_embeding_dict(class_embeding,text=text)
    @classmethod
    def get_bank_type(cls,head_dict):
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        
        match_fields = set()
        for _ ,embeding_list in cls.bank_field_type_split_embeding.items():
            """
            for emb in embeding_list:
                match_field = EmbedingToolBasic.classify_by_embeding_dict(text_emb=emb,class_dict=head_embeding_dict)
                match_fields.add(head_dict[match_field])
            """
            fields = set([head_dict[index] for index in EmbedingToolBasic.detect_texts_in_texts(head_embeding_dict,{i:emb for i,emb in  enumerate(embeding_list)} ).values() if index])
            match_fields.update(fields)
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
    '''
    @classmethod
    def recog_field(cls,agent,head_dict):
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        embeding_dict = cls.field_embeding[agent]
        
        ret = {}
        for k,q in embeding_dict.items():
            head_index = EmbedingToolBasic.classify_by_embeding_dict(text_emb=q,class_dict=head_embeding_dict)
            ret[k] = head_index
        return ret
    '''
    @classmethod
    def recog_field(cls, agent, head_dict):
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        embeding_dict = cls.field_embeding[agent]
        ret = EmbedingToolBasic.detect_texts_in_texts(head_embeding_dict,embeding_dict)
        return ret
        