import flask
import fire
import json
import os
import sys
sys.path.append(os.getcwd())
from flask import request
import traceback
import logging
import base64
from tools.embeding_tool_table import EmbedingToolTable as EmbedingTool
from file_classify import  FileClassify
from config.config import CONF
from io import BytesIO
app = flask.Flask(__name__)


ROOT_PATH = '/'

def _file_classify(file_path,file_data):
    _,ext = os.path.splitext(file_path)
    if ext not in ('.pdf','.xls','.xlsx'):
        return {"code":402,"success":False}
    
    obj = FileClassify(file_path,file_data).classify()
    

    return {"code":400,'success':True,'data':obj}


@app.route(ROOT_PATH+'file_classify/', methods=[ 'POST','GET'])
def file_classify():
    try:
        file_path = request.form["info"]
        file_data = request.form["data"]
        file_data =  base64.b64decode(file_data)
        res = _file_classify(file_path,file_data)
        return json.dumps(res,ensure_ascii=False)
    except Exception as e:
        msg = traceback.format_exc()
        logging.error("file_classify ERROR request:" + str(request.data)+'  traceback:'+msg)
        return {"code": -1, "success": False}

def run(port = 8000,device = None):
    if device not in (None,'GPU','CPU'):
        raise Exception(f"device must in {'GPU','CPU'} not {device}")
    if device:
        CONF.GPU = device == "GPU"
    print(f"{port=},GPU={CONF.GPU}")

    EmbedingTool.init()
    app.run(debug=False, processes=0, threaded=True, host='0.0.0.0', port=port)
    
if __name__ =="__main__":
    fire.Fire(run)