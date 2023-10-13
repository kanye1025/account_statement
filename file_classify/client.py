import os
import sys
import base64
import fire

sys.path.append(os.getcwd())
import json
import requests


def file_classify(file_path,ip='127.0.0.1',port=8000):
    url = f"http://{ip}:{port}/file_classify"
    parent_path,file_name = os.path.split(file_path)
    with open(file_path ,'rb') as f:
        file_data = f.read()
        file_data = base64.b64encode(file_data)
        data = {'info':file_name,'data':file_data}
        res = requests.post(url, data=data)
        obj = json.loads(res.text)
        if obj['success']:
            data = obj['data']
            if data['file']:
                file_name,ext = os.path.splitext(file_name)
                trans_file_name = file_name+'_trans'+ext
                trans_file_path = os.path.join(parent_path,trans_file_name)
                with open(trans_file_path,'wb') as f:
                    f.write(base64.b64decode(data['file'].encode('utf-8')))
            if data['image']:
                for i,image_data in enumerate(data['image'] ):
                    trans_file_path = os.path.join(parent_path, file_name+'_image'+str(i)+'.png')
                    with open(trans_file_path,'wb') as f:
                        f.write(base64.b64decode(image_data.encode('utf-8')))
            del data['file']
            del data['image']
        print(obj)
if __name__ == "__main__":
    fire.Fire()