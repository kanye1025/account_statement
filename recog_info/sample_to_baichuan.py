import pandas as pd
from recog_info_config import load_label_config
from prompt import Prompts
from toolkit.utils.data_file import DataFile
from config.load_asset_accounts_dict import get_personal_consumption_dict
label_config = load_label_config()

df_book  = pd.read_excel('data/samples.xlsx',sheet_name=None)
consumption_dict, consumption_index_dict = get_personal_consumption_dict()
def process_row(row):
    tag = ''
    person_org = ''
    income_or_expenses = ''
    row_data = {}
    for k,v in row.items():
        if k == '人工标签':
            #tag = v
            pass
        elif k == '机器标签':
            tag = v
        elif k =='账户类型':
            person_org = v
        elif k == '收支类型':
            income_or_expenses = v
        else:
            row_data[k] = v
    account_label_dict = label_config[(person_org,income_or_expenses)]
    des = '\n'.join([f"{k}-->{v[0]}" for k, v in account_label_dict.items()])
    if 'P03' in tag:
        tag_ = tag
        tag = 'P03消费支出'
    else:
        tag_ = ''
    prompt = Prompts.create_prompt(Prompts.account_label_prompt,{"text":'\n'.join(f'{k}:{v}'for k,v in row_data.items() if v ),
                                            "des":des,
                                            "key": str([i for i in account_label_dict.keys()])})
    if tag_:
        text = '\n'.join([f'{k}:{v}' for k, v in row.items()])
        prompt_ = Prompts.create_prompt(Prompts.consume_label_prompt,
                                       {"text": text, "key": str([i for i in consumption_index_dict.keys()])})



    else:
        prompt_ = ''
    return (prompt,tag,prompt_,tag_)

i = 0
with DataFile.create_file_to_wirte('data/baichuan_samples.jsonl') as f:
    for df in df_book.values():
        df.drop(columns = ["Unnamed: 0"],inplace = True)
        df.fillna('',inplace = True)
        df["sample"] = df.apply(lambda row:process_row(row),axis = 1)
        for prompt,tag ,prompt_,tag_ in df["sample"]:
            i+=1
            obj = {}
            obj['id'] = str(i)
            obj['conversations'] = list()
            obj['conversations'].append({"from":"human","value":prompt})
            obj['conversations'].append({"from": "assiant", "value": '好的，提取的json数据为\n```{"标签类型":"'+tag+'"}'})
            DataFile.write_obj_to_json_file_line(f,obj)
            if prompt_ and tag_:
                i += 1
                obj = {}
                obj['id'] = str(i)
                obj['conversations'] = list()
                obj['conversations'].append({"from": "human", "value": prompt_})
                obj['conversations'].append(
                    {"from": "assiant", "value": '好的，提取的json数据为\n```{"消费类型":"' + tag + '"}'})
                DataFile.write_obj_to_json_file_line(f, obj)