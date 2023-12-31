from tools.embeding_tool import *
from config.load_org_type_dict import get_org_type_dict
from config.load_asset_accounts_dict import get_asset_accounts_desc_dict
from toolkit.utils.process_exec import ExecProcess,process_exec
from toolkit.utils.data_file import DataFile
from recog_info.recog_info_config import load_label_config
from config.config import CONF
import os
from copy import deepcopy
import inspect
import re
#process =  ExecProcess()
class EmbedingToolInfo:
    
    def __init__(self):
        self.inited = False
    def save_embeding(self):
        attributes = inspect.getmembers(self, lambda x: not inspect.isfunction(x) and not inspect.ismethod(
            x) and not inspect.isbuiltin(x))
        attributes = list(filter(lambda x: not x[0].startswith('__'), attributes))
        obj = {k:v for k,v in attributes}
        DataFile.save_picke(obj,CONF.recog_info_embeding_path)
    

    def load_embeding(self):
        obj = DataFile.load_pickle(CONF.recog_info_embeding_path)
        for k,v in obj.items():
            self.__setattr__(k,v)
    
    
    def init(self,load_or_save):
        EmbedingToolBasic.init()
        if load_or_save:
            self.load_embeding()
        else:
            self.init_embeding()
            self.save_embeding()
    def init_embeding(self):

        print("init")
        if not self.inited:
            self.inited = True
            
            EmbedingToolBasic.init()
    
            self.field_embeding = {}
            for agent, key_dict in dicts.field_dict.items():
                self.field_embeding[agent] = EmbedingToolBasic.get_embeding_dict(key_dict, is_query=True)
            
            self.bank_field_type_split_embeding = {k: EmbedingToolBasic.get_embeding_list(v, is_query=True) for k, v in
                                                  dicts.bank_field_type_split.items()}
            self.bank_field_type_join_embeding = EmbedingToolBasic.get_embeding_dict(dicts.bank_field_type_join)
            self.alipay_field_type_split_embeding = {k: EmbedingToolBasic.get_embeding_list(v, is_query=True) for k, v in
                                                    dicts.alipay_field_type_split.items()}
            self.alipay_field_type_join_embeding = EmbedingToolBasic.get_embeding_dict(dicts.alipay_field_type_join)
            
            self.person_organization_embeding = EmbedingToolBasic.get_embeding_dict(dicts.person_organization_dict)
            self.org_code_name_dict,org_code_desc_dict = get_org_type_dict()
            self.org_type_embeding = EmbedingToolBasic.get_embeding_dict(org_code_desc_dict)
            _,label_des = load_label_config()
            self.label_embeding_dict = dict()
            self.head_embeding = EmbedingToolBasic.get_query_embeding(dicts.head)
            for k,d in label_des.items():
                self.label_embeding_dict[k] = EmbedingToolBasic.get_embeding_dict(d)
            '''
            asset_accounts_desc_dict = get_asset_accounts_desc_dict()
            self.asset_accounts_embeding_dict = {}
            self.asset_accounts_tags_embeding_list = {}
            
            for person_org, v1 in asset_accounts_desc_dict.items():
                self.asset_accounts_embeding_dict[person_org] = {}
                self.asset_accounts_tags_embeding_list[person_org] = {}
                for income_expenditure, v2 in v1.items():
                    #self.asset_accounts_embeding_dict[person_org][income_expenditure] = EmbedingToolBasic.get_embeding_dict(v2)
                    
                    self.asset_accounts_tags_embeding_list[person_org][income_expenditure] = ([],[])
                    for k,v in v2.items():
                        sub_strs = re.split(r'([，。,.;；、\n])', v)
                        sub_strs = [i for i in sub_strs if i and i not in "，。,.;；、\n"]
                        embedings = EmbedingToolBasic.get_embeding_list(sub_strs)
                        self.asset_accounts_tags_embeding_list[person_org][income_expenditure][0].extend([k]*len(sub_strs))
                        self.asset_accounts_tags_embeding_list[person_org][income_expenditure][1].extend(embedings)
        '''
        print('inited')

    def label_recall(self,personal,in_or_ex,text,top_k=3):
        e_dict = self.label_embeding_dict[(personal,in_or_ex)]
        return EmbedingToolBasic.classify_by_embeding_dict(e_dict,text,top_k=top_k)

    def person_or_org(self,text):
        try:
            score_dict = {k: v for k, v in
                          EmbedingToolBasic.classify_by_embeding_dict(self.person_organization_embeding, text,
                                                                      top_k=2)}
        except Exception as e:
            print(os.getpid())
            pass
        if len(text) <= 3 and "支付" not in text and "微信" not in text and "财付通" not in text:
            score_dict["PERSON"] += 0.1
        if "公司" in text or "银行" in text :
            score_dict["ORG"] +=0.1
        return sorted([(k, v) for k, v in score_dict.items()], key=lambda x: x[1], reverse=True)[0][0]
    
    

    def get_org_type(self,text):
        
        code = EmbedingToolBasic.classify_by_embeding_dict(self.org_type_embeding,text=text)
        return code,self.org_code_name_dict[code]



    def get_account_labelv2(self, person_org,pay_type, text):
        if pay_type not in ("收入","支出"):return ""
        person_org = "对私" if person_org =="对私" else "对公"  #unknown 也当对公处理
        class_embeding = self.asset_accounts_embeding_dict[person_org][pay_type]
        ret =  EmbedingToolBasic.classify_by_embeding_dict(class_embeding, text=text)
        #asset_accounts_desc_dict = get_asset_accounts_desc_dict()
        #print(f'{text}->{person_org}:{pay_type}:{ret}:{asset_accounts_desc_dict[person_org][pay_type][ret]}')
        return ret

    def get_account_labelv3(self, person_org, pay_type, text):
        if pay_type not in ("收入", "支出"): return ""
        person_org = "对私" if person_org == "对私" else "对公"  # unknown 也当对公处理
        tags,embedings = self.asset_accounts_tags_embeding_list[person_org][pay_type]
    
        ret = EmbedingToolBasic.tags_by_embeding_list(tags,embedings, text=text)
        
        return ret
    def get_bank_type(self, head_dict):
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        
        match_fields = set()
        for _, embeding_list in self.bank_field_type_split_embeding.items():
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
                                                                class_dict=self.bank_field_type_join_embeding)
        return bank_type
    

    def get_alipay_type(self, head_dict):
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        match_fields = set()
        
        for _, embeding_list in self.alipay_field_type_split_embeding.items():
            for emb in embeding_list:
                match_field = EmbedingToolBasic.classify_by_embeding_dict(text_emb=emb, class_dict=head_embeding_dict)
                match_fields.add(head_dict[match_field])
        match_fields = ','.join(list(match_fields))
        alipay_type = EmbedingToolBasic.classify_by_embeding_dict(text=match_fields,
                                                                  class_dict=self.alipay_field_type_join_embeding)
        return alipay_type


    def get_head_index(self, rows):
        row_texts = [','.join([str(v) for k ,v in row.items() if '.'  in k]) for row in rows]
        results = EmbedingToolBasic.detect_text_in_list(self.head_embeding, row_texts)
        return [r[0] for r in results]

    def recog_field(self, agent, head_dict):
        head_dict = deepcopy(head_dict)
        
        for k,v in head_dict.items():
            tmp_v = list()
            for w in v:
                if w.encode('utf-8').isalpha():
                    continue
                tmp_v.append(w)
            head_dict[k] = ''.join(tmp_v)
            
        datetime_dict = {k:v for k,v in head_dict.items() if "时间" in v or "日期" in v}
        head_dict = {k: v for k, v in head_dict.items() if "时间" not in v and "日期"  not in v}
        
        head_dict = {k: v.replace("账号","卡号").replace("账户","户名")  for k, v in head_dict.items() if "开户行" not in v }
        head_embeding_dict = EmbedingToolBasic.get_embeding_dict(head_dict)
        embeding_dict = self.field_embeding[agent]
        ret = EmbedingToolBasic.detect_texts_in_texts(head_embeding_dict, embeding_dict,th=0.4)
        if datetime_dict:
            datetime_emb_dict = EmbedingToolBasic.get_embeding_dict(datetime_dict)
            date_key = EmbedingToolBasic.classify_by_embeding_dict(datetime_emb_dict,"交易日期,记录日期,支付日期,时间")
            ret["交易日期"] = date_key
        else:
            ret["交易日期"] = ""
        return ret
    




    def close(self):
        pass
        #process.close()
        
