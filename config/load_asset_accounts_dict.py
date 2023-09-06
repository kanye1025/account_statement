import  xlrd

asset_accounts_desc_dict = {}
personal_consumption_dict = {}
name_index_dict = {}
asset_accounts_dict = dict()
name_code_dict = dict()

def get_personal_consumption_dict():
    global name_index_dict,personal_consumption_dict
    if name_code_dict:return personal_consumption_dict,name_index_dict
    book = xlrd.open_workbook("config/20230925科目标签&居民消费支出分类（对公、对私）.xlsx")
    sheet = book.sheet_by_name("居民消费分类支出2013")
    
    index = 0
    cur_text = []
    cur_code = ""
    cur_name = ""
    for i in  range(2,sheet.nrows):
        row = sheet.row(i)
        parent_code = row[0].value.strip()
        
        if parent_code:
            continue
        code = row[1].value.strip()
        name = row[3].value.strip()
        if code:
            if cur_code:
                personal_consumption_dict[cur_name] =cur_name+":"+ ','.join(cur_text)
            cur_code = code
            
            cur_text = list()
            cur_name = name
            name_index_dict[name] = index
            index+=1
        elif name:
            cur_text.append(name)
    personal_consumption_dict[cur_name] = cur_name + ":" + ','.join(cur_text)
    return personal_consumption_dict,name_index_dict
        
    
def get_asset_accounts_dict():
    global  asset_accounts_dict ,name_code_dict
    if name_code_dict:return asset_accounts_dict ,name_code_dict
    book = xlrd.open_workbook("config/20230925科目标签&居民消费支出分类（对公、对私）.xlsx")
    for  public_private  in ("对公","对私"):
        sheet = book.sheet_by_name(public_private)
        asset_accounts_dict[public_private] = {}
        asset_accounts_dict[public_private]["收入"] = dict()
        asset_accounts_dict[public_private]["支出"] = dict()
        cur_code = ""
        cur_name = ""
        for i in  range(1,sheet.nrows):
            row = sheet.row(i)
            if "编号" in row[0].value :continue

            code = row[0].value.strip()
            name = row[1].value.strip()
            if code and name:
                cur_code = code
                cur_name = name
                name_code_dict[name] = code
            income_expenses = row[2].value.strip()
            if income_expenses =="/":
                continue
            use = row[3].value.strip()
            remark = row[4].value.strip()
            counterparty_industry = row[5].value.strip()
            accounting_entry =  row[6].value.strip()

            asset_accounts_dict[public_private][income_expenses][cur_name] = {"use":use,"remark":remark,"counterparty_industry":counterparty_industry,"accounting_entry":accounting_entry}
    
    personal_consumption_dict,personal_consumption_index = get_personal_consumption_dict()
    for name ,index in personal_consumption_index.items():
        code = "P"+str(index).zfill(2)
        use = personal_consumption_dict[name]
        asset_accounts_dict["对私"]["支出"][name]  = {"use":use,"remark":"","counterparty_industry":"","accounting_entry":"增加"}
        name_code_dict[name] = code
    del asset_accounts_dict["对私"]["支出"]["二级中类"]
    del name_code_dict["二级中类"]
    return asset_accounts_dict,name_code_dict

def get_asset_accounts_desc_dict():
    global asset_accounts_desc_dict
    if asset_accounts_desc_dict:return asset_accounts_desc_dict
    asset_accounts_dict, _ = get_asset_accounts_dict()
    for person_org,v1 in asset_accounts_dict.items():
        asset_accounts_desc_dict[person_org] = {}
        for income_expenditure ,v2 in v1.items():
            asset_accounts_desc_dict[person_org][income_expenditure] = {}
            for name,obj in v2.items():
                text = []
                if obj['use']:
                    text.append(f"资金的用途是:{obj['use']}")
                if obj['remark']:
                    text.append(f"备注是:{obj['remark']}")
                if obj['counterparty_industry']:
                    text.append(f"交易对方的行业是:{obj['counterparty_industry']}")
                asset_accounts_desc_dict[person_org][income_expenditure][name] =  ';'.join(text)
    return asset_accounts_desc_dict
if __name__ =="__main__":
    asset_accounts_dict,name_code_dict = get_asset_accounts_dict()
    get_asset_accounts_desc_dict()
    #get_personal_consumption_dict()