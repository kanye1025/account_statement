from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import  xlrd
import numpy as np

data  = xlrd.open_workbook("data/甘玉兰化妆品2022.7-2022.9明细.xls")

table = data.sheets()[0]
values = set()
embeding = HuggingFaceEmbeddings(model_name="../../text2vec-large-chinese")
heads = "流水号/订单号,时间,收入,支出,备注/用途,余额/金额,对方账号,对方户名,收付款方式,开户机构/开户行,分类"

h_emb = embeding.embed_query(heads)
cols = list()
for i in range(table.nrows):
    col = list()
    for j in range(table.ncols):
        value = str(table.cell_value(i, j))
        col.append(value)
    col = ','.join(col)
    cols.append(col)
    
cols_emb = embeding.embed_documents(cols)
results = list()
for col,e in zip(cols,cols_emb):
    s = np.dot(h_emb,e)
    results.append((col,s))
results = sorted(results,key=lambda x:x[1],reverse=True)
for c,s in results[:2]:
    print(c,s)

