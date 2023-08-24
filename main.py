import os
import json
from split_table.table_recog import TableRecog
input_dir = "data/input"
output_dir ="data/output"
for filename in os.listdir(input_dir):
    input_path = os.path.join(input_dir,filename)
    obj = TableRecog(input_path).get_table_data()
    output_path = os.path.join(output_dir,filename+'.txt')
    with open(output_path,'w',encoding='utf-8') as f:
        json.dump(obj,f,ensure_ascii=False)
