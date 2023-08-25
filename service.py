import flask
import fire
import json
import os
from flask import request
import traceback
import logging
from split_table.table_recog import TableRecog

app = flask.Flask(__name__)


ROOT_PATH = '/'

def _res1(data):
    _,ext = os.path.splitext(data['file_path'])
    if ext not in ('.pdf','.xls','.xlsx'):
        return {"code":301,"message":"Type error"}
    obj = TableRecog(data['file_path']).get_table_data()
    res = {"code":300,"message":"Success","data":obj}
    return res

    
    
@app.route(ROOT_PATH+'res1/', methods=[ 'POST','GET'], strict_slashes=False)
def res1():
    try:
        data = json.loads(request.data)
        res = _res1(data)
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