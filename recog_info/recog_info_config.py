import pandas as pd
from collections import defaultdict
from config.load_asset_accounts_dict import get_personal_consumption_dict
def load_label_config():
    df_book  = pd.ExcelFile('config/20231206会计分录&科目标签.xlsx')
    lable_conf = defaultdict(dict)
    dir_conf = defaultdict(dict)
    personal_consumption_dict, name_index_dict = get_personal_consumption_dict()
    for key in ('对私','对公'):
        df = df_book.parse(f'会计分录识别（{key}）')
        df.fillna('',inplace=True)
        for  in_or_ex,remark,trade_type,trade_code,trade_des,s_tag,s_dir in zip(
                df["收支类型"],df["摘要/备注/附言"],df["商品分类"],df["商品分类代码"],df["商品说明"],df["科目标签-S"],df["分录方向-S"]):
            text = list()
            if remark:text.append(remark)
            if trade_des:text.append(trade_des)
            trade_type = f'{trade_code} {trade_type}'
            #lable_conf[(key,in_or_ex)][s_tag] = {"remark":remark,"using":using,"industry":industry}
            lable_conf[(key, in_or_ex)][trade_type] = (','.join(text),(s_dir,s_tag))
        '''
        for k,using in personal_consumption_dict.items():
            num = name_index_dict[k]+1
            num = str(num).rjust(2, '0')
            lable_conf[(key,'支出')][f'P03{num}{k}']={"remark":"","using":using,"industry":"消费类商品和服务的商家机构"}
            dir_conf[(key, '支出')][f'P03{num}{k}'] = "增加"
        del lable_conf[(key,'支出')]["P03-P26消费支出"]
        '''
        

    return lable_conf


if __name__ == '__main__':
    print(load_label_config())
        

