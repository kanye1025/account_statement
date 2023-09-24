import os
import sys
import base64
import fire

sys.path.append(os.getcwd())
import json
import requests


def file_classify(file_path,ip='127.0.0.1',port=8000):
    url = f"http://{ip}:{port}/file_classify"
    _,file_name = os.path.split(file_path)
    with open(file_path ,'rb') as f:
        file_data = f.read()
        file_data = base64.b64encode(file_data)
        data = {'info':file_name,'data':file_data}
        res = requests.post(url, data=data)
        obj = json.loads(res.text)
        if obj['success']:
            if obj['file']:
                with open('file.pdf','wb') as f:
                    f.write(base64.b64decode(obj['file'].encode('utf-8')))
            if obj['image']:
                for i,image_data in enumerate(obj['image'] ):
                    with open(f'image{i}.png','wb') as f:
                        f.write(base64.b64decode(image_data.encode('utf-8')))
            del obj['file']
            del obj['image']
            print(obj)
        else:
            print('wrong',obj['code'])
if __name__ == "__main__":
    fire.Fire()