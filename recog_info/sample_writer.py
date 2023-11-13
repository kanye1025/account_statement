import pandas as pd
from collections import defaultdict
class SampleWriter:
    def __init__(self):
        self.samples = defaultdict(list)
        self.heads = dict()
    def add_head(self,file_name,head):
        self.heads[file_name] = head
    def add_sample(self,file_name,label,person_org,income_or_expenses,data):
        self.samples[file_name].append((label,person_org,income_or_expenses,data))

    def to_excel(self,file_path):
        with pd.ExcelWriter(file_path) as writer:
            for file_name,head in self.heads.items():
                head_all = ['人工标签','机器标签','账户类型','收支类型']
                head_all.extend(head)
                data = defaultdict(list)

                for sample in self.samples[file_name]:
                    data['人工标签'].append('')
                    data['机器标签'].append(sample[0])
                    data['账户类型'].append(sample[1])
                    data['收支类型'].append(sample[2])
                    for k in head:
                        data[k].append(sample[3][k] if k in sample[3] else '')
                data = pd.DataFrame(data)
                data.to_excel(writer,sheet_name=file_name)
