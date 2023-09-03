from tools.embeding_tool import *
class EmbedingToolTable:
    inited = False
    
    @classmethod
    def init(cls):
        if not cls.inited:
            cls.inited = True
            EmbedingToolBasic.init()
            cls.agent_embeding = EmbedingToolBasic.get_embeding_dict(dicts.agent_dict)
            
            cls.head_embeding = EmbedingToolBasic.get_query_embeding(dicts.head)
    
    @classmethod
    def get_head_index(cls, rows):
        row_texts = [','.join(row) for row in rows if row]
        results = EmbedingToolBasic.detect_text_in_list(cls.head_embeding, row_texts)
        return [r[0] for r in results]
    
    @classmethod
    def recog_agent(cls, text):
        return EmbedingToolBasic.classify_by_embeding_dict(class_dict=cls.agent_embeding, text=text)
    
    