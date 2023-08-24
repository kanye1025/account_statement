# coding=utf-8
import json
from tools.embeding_tool import EmbedingTool
class RecogInfo:
    def __init__(self,obj):
        self.obj = obj
        self.texts = '\n'.join([i['txt'] for i in obj['res1']['outside_infos']])
    
    def get_agent(self):
        agent = EmbedingTool.recog_agent(self.texts)
        self.obj['res1']['agent_type'] = agent
        
    
    def get_recoged_obj(self):
        self.get_agent()
        
if __name__ == "__main__":
    jtext = """
    """
    obj = json.loads(jtext)
    ri = RecogInfo(obj)
    ri.get_agent()
    print(ri.obj)