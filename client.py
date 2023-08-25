import os
import sys
import fire
sys.path.append(os.getcwd())
import json
import requests


def res1(file_path,ip='127.0.0.1',port=8000):
    url = f"http://{ip}:{port}/res1"
    headers = {"content-type": "application/json"}
    
    res = requests.post(url, json={'file_path': file_path}, headers=headers)
    
    res = json.loads(res.text)
    print(res)

if __name__ == "__main__":
    fire.Fire()