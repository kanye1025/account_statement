from tools.embeding_tool import *
class EmbedingToolInfo:
    inited = False
    
    @classmethod
    def init(cls):
        if not cls.inited:
            cls.inited = True
            EmbedingToolBasic.init()

            
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
    def person_or_org(cls, text):
        return EmbedingToolBasic.classify_by_embeding_dict(cls.person_organization_embeding, text)
    
    @classmethod
    def get_account_label(cls, pay_type, text):
        if pay_type not in cls.account_label_embeding: return ""
        class_embeding = cls.account_label_embeding[pay_type]
        return EmbedingToolBasic.classify_by_embeding_dict(class_embeding, text=text)
    
    @classmethod
    def get_bank_type(cls, head_dict):
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        
        match_fields = set()
        for _, embeding_list in cls.bank_field_type_split_embeding.items():
            """
            for emb in embeding_list:
                match_field = EmbedingToolBasic.classify_by_embeding_dict(text_emb=emb,class_dict=head_embeding_dict)
                match_fields.add(head_dict[match_field])
            """
            fields = set([head_dict[index] for index in EmbedingToolBasic.detect_texts_in_texts(head_embeding_dict,
                                                                                                {i: emb for i, emb in
                                                                                                 enumerate(
                                                                                                     embeding_list)}).values()
                          if index])
            match_fields.update(fields)
        match_fields = ','.join(list(match_fields))
        
        bank_type = EmbedingToolBasic.classify_by_embeding_dict(text=match_fields,
                                                                class_dict=cls.bank_field_type_join_embeding)
        return bank_type
    
    @classmethod
    def get_alipay_type(cls, head_dict):
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
    def recog_field(cls, agent, head_dict):
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        embeding_dict = cls.field_embeding[agent]
        ret = EmbedingToolBasic.detect_texts_in_texts(head_embeding_dict, embeding_dict)
        return ret