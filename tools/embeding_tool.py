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
    
    
class EmbedingTool:
    head = "流水号/订单号,时间,收入,支出,备注/用途,余额/金额,对方账号,对方户名,收付款方式,开户机构/开户行,分类"
    @classmethod
    def get_head_index(cls,rows):
        row_texts = [','.join(row) for row in rows if row]
        results = EmbedingToolBasic.detect_text_in_list(cls.head,row_texts)
        return [r[0] for r in results]
        