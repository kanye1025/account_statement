import os
import json
from split_table.table_recog import TableRecog
from tqdm import tqdm
import traceback
input_dir = "data/input"
output_dir ="data/output"
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
