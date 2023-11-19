import os
import sys
import base64
import fire

sys.path.append(os.getcwd())
import json
import requests


def label_generation(json_path,ip='127.0.0.1',port=8000):
    url = f"http://{ip}:{port}/label_generation"
    with open(json_path, 'r') as f:
        json_data = json.load(f)
        res = requests.post(url, json=json_data)
        return res.text
if __name__ == "__main__":
    fire.Fire()