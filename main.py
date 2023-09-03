import os
import json
from tools.embeding_tool import *
from split_table.table_recog import TableRecog
from recog_info.recog_info import RecogInfo
from tqdm import tqdm
import traceback
input_dir = "data/input"
output_dir ="data/output"
output_dir2 = "data/output2"
EmbedingToolBasic.init()
EmbedingTool.init()

'''
for filename in tqdm(os.listdir(input_dir)):
    try:
        input_path = os.path.join(input_dir,filename)
        obj = TableRecog(input_path).get_table_data()
        output_path = os.path.join(output_dir,filename+'.txt')
        with open(output_path,'w',encoding='utf-8') as f:
            json.dump(obj,f,ensure_ascii=False)
    except Exception as e:
        print(filename)
        traceback.print_exc()

exit(0)
'''
for filename in tqdm(os.listdir(output_dir)):
    try:
        input_path = os.path.join(output_dir,filename)
        with open(input_path,'r',encoding='utf-8') as f:
            obj = json.load(f)
            obj = RecogInfo(obj).get_recoged_obj()
            output_path = os.path.join(output_dir2,filename+'.txt')
            with open(output_path,'w',encoding='utf-8') as f:
                json.dump(obj,f,ensure_ascii=False)
    except Exception as e:
        print(filename)
        traceback.print_exc()