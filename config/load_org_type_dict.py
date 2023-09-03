import  xlrd

def get_org_type_dict():
    sheet = xlrd.open_workbook("config/国民经济分类20190531.xlsx").sheets()[0]
    parents_desc = {}
    code_name_dict = {}
    leaf_desc = {}
    current_type1 = ""
    current_type2 = ""
    current_type3 = ""
    current_type4 = ""
    current_dest = list()
    include = True
    for i in range(1,sheet.nrows):
        row = sheet.row(i)
        type_123 = str(row[0].value).split('.')[0].strip()
        type_4 = str(row[1].value).split('.')[0].strip()
    
        text = row[3].value + row[4].value
        
        if type_4:
            row_type = "type_4"
        elif type_123:
            row_type = f"type_{len(type_123)}"
            parents_desc[type_123] = text
        else:
            row_type = "desc"
            
        if row_type !="desc" and current_type4:
            leaf_desc[current_type4] = '\n'.join(current_dest)
            if not current_type4:
                pass
            
            
        if row_type == "type_1":
            current_type1 = type_123
            #current_dest.append(text)
        elif row_type == "type_2":
            current_type2 = type_123
            #current_dest.append(text)
        elif row_type == "type_3":
            current_type3 = type_123
            #current_dest.append(text)
        elif row_type == "type_4":
            current_type4 = current_type1+type_4
            code_name_dict[current_type4] = text
            current_dest = [parents_desc[current_type1],parents_desc[current_type2],parents_desc[current_type3], text]
            include = True
        elif row_type == "desc":
            if "不包括" in row[3].value and len(row[3].value.replace("不包括",'')) <5:
                include = False
                continue
            if include:
                if "不包括" in  row[3].value:
                    text = row[3].value.split("不包括")[0]+row[4].value
                current_dest.append( text)
    return code_name_dict,leaf_desc
    
if __name__ =="__main__":
    get_org_type_dict()
    

        
    
    
    
        