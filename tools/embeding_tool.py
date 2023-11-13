from config.config import CONF
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import numpy as np
from config import  dicts
import torch
class EmbedingToolBasic:
    embeding = None
    @classmethod
    def init(cls):
        if not cls.embeding :
            cls.device = 'cuda' if CONF.GPU else 'cpu'
            cls.embeding = HuggingFaceEmbeddings(model_name=CONF.embeding_model_path, model_kwargs={'device': cls.device})

            
    @classmethod
    def detect_text_in_list(cls,query,candidates):
        if type(query) == str:
            
            q_emb = cls.embeding.embed_query(query)
        else:
            q_emb = query
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

        q = torch.from_numpy(np.asarray(q,dtype=float)).to(cls.device)
        k = torch.from_numpy(np.asarray(k,dtype=float)).to(cls.device)
        similarity = torch.cosine_similarity(q, k,dim=0)
        return similarity.item()

    @classmethod
    def sims(cls, q, ks):
        q = torch.from_numpy(np.asarray(q, dtype=float)).to(cls.device)
        k = torch.from_numpy(np.asarray(ks, dtype=float)).to(cls.device)
        similarity = torch.cosine_similarity(q, k, dim=1)
        return similarity.item()
        #return  np.dot(q, k) / (np.linalg.norm(q) * np.linalg.norm(k))
        #return  np.dot(q, k)
    '''
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
    '''

    @classmethod
    def classify_by_embeding_dict(cls, class_dict, text=None, text_emb=None, top_k=None):
        if not text_emb:
            text_emb = cls.get_query_embeding(text)
        keys = class_dict.keys()
        embedings = list(class_dict.values())
        q = torch.from_numpy(np.asarray(text_emb, dtype=float)).to(cls.device)
        ks = torch.from_numpy(np.asarray(embedings, dtype=float)).to(cls.device)
        #similarities = torch.cosine_similarity(q, ks, dim=1).tolist()
        similarities = torch.cosine_similarity(q, ks, dim=-1).tolist()
        ret = zip(keys,similarities)
        
        
        if not top_k:
            ret = sorted(ret, key=lambda x: x[1], reverse=True)
            return ret[0][0]
        else:
            ret = sorted(ret, key=lambda x: x[1], reverse=True)[:top_k]
            return ret

    @classmethod
    def tags_by_embeding_list(cls, tags,embedings, text=None, text_emb=None, top_k=None):
        if not text_emb:
            text_emb = cls.get_query_embeding(text)
        
        
        q = torch.from_numpy(np.asarray(text_emb, dtype=float)).to(cls.device)
        ks = torch.from_numpy(np.asarray(embedings, dtype=float)).to(cls.device)
        similarities = torch.cosine_similarity(q, ks, dim=1).tolist()
    
        ret = zip(tags, similarities)
    
        if not top_k:
            ret = sorted(ret, key=lambda x: x[1], reverse=True)
            return ret[0][0]
        else:
            ret = sorted(ret, key=lambda x: x[1], reverse=True)[:top_k]
            return ret
        
    @classmethod
    def detect_texts_in_texts(cls, embeding_dict_super,embeding_dict_sub,th = 0.0 ):
        pre_dict = {}
        for sub_key,q_embeding in embeding_dict_sub.items():
            pre_dict[sub_key] = cls.classify_by_embeding_dict(embeding_dict_super,text_emb = q_embeding,top_k=3)
        sort_dict = {}
        for q,r in pre_dict.items():
            k,s = r[0]
            if s <th:
                continue
            if k not in sort_dict or sort_dict[k][1]<s:
                sort_dict[k] = (q,s)
        ret_dict = {k:'' for k in embeding_dict_sub.keys()}
        for k ,(q,s)in sort_dict.items():
            ret_dict[q] = k
            del pre_dict[q]
            
        sort_dict = {}
        for q, r in pre_dict.items():
            k, s = r[1]
            if s <th:
                continue
            if k in ret_dict.values():
                continue
            if k not in sort_dict or sort_dict[k][1] < s:
                sort_dict[k] = (q, s)
        for k ,(q,s)in sort_dict.items():
            ret_dict[q] = k
            del pre_dict[q]

        sort_dict = {}
        for q, r in pre_dict.items():
            k, s = r[2]
            if s <th:
                continue
            if k in ret_dict.values():
                continue
            if k not in sort_dict or sort_dict[k][1] < s:
                sort_dict[k] = (q, s)
        for k, (q, s) in sort_dict.items():
            ret_dict[q] = k
            del pre_dict[q]
        return ret_dict
        
                
                
                
        
        
    


