import flask
import fire
import json
import os
from flask import request
import traceback
import logging
import base64
from split_table.table_recog import TableRecog
from config.config import CONF
from io import BytesIO
app = flask.Flask(__name__)


ROOT_PATH = '/'
'''
def _form_recognition(file_path):
    _,ext = os.path.splitext(file_path)
    if ext not in ('.pdf','.xls','.xlsx'):
        return {"code":301,"message":"Type error"}
    #data['file_data'] =   bytes(data['file_data'], encoding = "utf-8")

    obj = TableRecog(file_path).get_table_data()
    res = {"code":300,"message":"Success","data":obj}
    return res
'''
def _form_recognition(file_path,file_data):
    _,ext = os.path.splitext(file_path)
    if ext not in ('.pdf','.xls','.xlsx'):
        return {"code":301,"message":"Type error"}
    #data['file_data'] =   bytes(data['file_data'], encoding = "utf-8")

    obj = TableRecog(file_path,file_data).get_table_data()
    res = {"code":300,"message":"Success","data":obj}
    return res


@app.route(ROOT_PATH+'form_recognition/', methods=[ 'POST','GET'])
def form_recognition():
    try:
        file_path = request.form["info"]
        file_data = request.form["data"]
        file_data =  base64.b64decode(file_data)
        res = _form_recognition(file_path,file_data)
        return json.dumps(res,ensure_ascii=False)
    except Exception as e:
        msg = traceback.format_exc()
        logging.error("res1 ERROR request:" + str(request.data)+'  traceback:'+msg)
        return {"code": -1, "message": msg}

def run(port = 8000):
    print(port)
    app.run(debug=False, processes=0, threaded=True, host='0.0.0.0', port=port)
    
if __name__ =="__main__":
    fire.Fire(run)