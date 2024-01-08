import flask
import fire
import json
import os
from flask import request
import traceback
import logging
import base64
from tools.embeding_tool_table import EmbedingToolTable as EmbedingTool
from recog_info.info_recog import RecogInfo
from config.config import CONF
from io import BytesIO
from error.error import Error
import torch
app = flask.Flask(__name__)


ROOT_PATH = '/'

def _label_generation(obj):

    obj = RecogInfo(obj).get_recoged_obj()

    res = {"success":True,"data":obj}
    return res


@app.route(ROOT_PATH+'label_generation/', methods=[ 'POST','GET'])
def label_generation():
    try:

        res = _label_generation(request.json)
        return json.dumps(res,ensure_ascii=False)
    except Error as e:
        msg = traceback.format_exc()
        logging.error("res1 ERROR request:" + str(request.data) + '  traceback:' + msg)
        res = {"success":False,"error-code":e.code,"message":e.msg}
        return json.dumps(res,ensure_ascii=False)
    except Exception as e:
        msg = traceback.format_exc()
        logging.error("res1 ERROR request:" + str(request.data)+'  traceback:'+msg)
        return {"success":False,"error-code": -1, "message": msg}

def run(port = 8000,device = None):

    if device not in (None,'GPU','CPU'):
        raise Exception(f"device must in {'GPU','CPU'} not {device}")
    if device:
        CONF.GPU = device == "GPU"
    print(f"{port=},GPU={CONF.GPU}")

    torch.multiprocessing.set_start_method('spawn')
    RecogInfo.init()
    app.run(debug=False, processes=0, threaded=True, host='0.0.0.0', port=port)
    
if __name__ =="__main__":
    fire.Fire(run)