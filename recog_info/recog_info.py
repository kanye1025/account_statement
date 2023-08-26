# coding=utf-8
import json
from tools.embeding_tool import EmbedingTool
from tools.llm_tool import LLMTool
class RecogInfo:
    def __init__(self,obj):
        self.obj = obj
        self.texts = '\n'.join([i['txt'] for i in obj['res1']['outside_infos']])
    
    def get_agent(self):
        agent = EmbedingTool.recog_agent(self.texts)
        self.obj['res1']['agent_type'] = agent
        self.agent = agent
        
    def field_align(self):
        agent_type = self.obj["res1"]['agent_type']
        self.obj["res3"] = list()
        head_dict = dict()
        for row in self.obj["res2"]:
            if row["header_row"] == True:
                for k,v in row.items():
                    if '.' in k:
                        _,col_index =k.split('.')
                        head_dict[col_index] = v
            break
        if not head_dict:
            raise Exception("not find any header_row")
        field_index_dict = EmbedingTool.recog_field(agent_type,head_dict)
        for res2_row in self.obj["res2"]:
            res3_row = {}
            res3_row["row_order"] = res2_row["row_order"]
            row2_index = res2_row["row_order"].split('_')[1]
            res3_row["header_row"] = res2_row["header_row"]
            for i,(field,col_index) in enumerate(field_index_dict.items()):
                index2 = row2_index+'.'+col_index
                index3 = row2_index+'.'+str(i+1)
                res3_row[index3] = res2_row[index2]
            self.obj["res3"].append(res3_row)
            
    def get_before_info(self):
        text_before = '\n'.join([d['txt'] for d in self.obj['res1']['outside_infos'] ])
        obj = LLMTool.recog_before_info(self.agent,text_before)
        self.obj['res1'].update(obj)
        
    def get_recoged_obj(self):
        self.get_agent()
        self.get_before_info()
        self.field_align()
        return self.obj
        
        
if __name__ == "__main__":
    
    with open("data/output/微信交易明细.pdf.txt",'r',encoding="utf-8") as f:
        obj = json.load(f)
    
        obj = RecogInfo(obj).get_recoged_obj()
    
        print(json.dumps(obj,ensure_ascii=False))
    