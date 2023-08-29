import os
import sys
import base64
import fire

sys.path.append(os.getcwd())
import json
import requests

'''
def form_recognition(file_path,ip='127.0.0.1',port=8000):
    url = f"http://{ip}:{port}/form_recognition"
    _,file_name = os.path.split(file_path)
    with open(file_path ,'rb') as f:
        #file_data = f.read()
        #file_data = str(base64.b64encode(file_data))
        #headers = {"content-type": "application/json"}
        #headers = {"Content-Type": "multipart/form-data"}
        data = {"file_name":file_name}
        res = requests.post(url, data=data,files={"file":f})
        return res.text
'''
def form_recognition(file_path,ip='127.0.0.1',port=8000):
    url = f"http://{ip}:{port}/form_recognition"
    _,file_name = os.path.split(file_path)
    with open(file_path ,'rb') as f:
        file_data = f.read()
        file_data = base64.b64encode(file_data)
        data = {'info':file_name,'data':file_data}
        res = requests.post(url, data=data)
        return res.text
if __name__ == "__main__":
    fire.Fire()