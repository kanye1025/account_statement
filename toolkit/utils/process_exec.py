from multiprocessing import  Process,Lock,Pipe,Queue

import inspect
from typing import (
    Any, Callable, ContextManager, Iterable, Mapping, Optional, Dict, List,
    Union, Sequence, Tuple
)
import time
class ExecProcess(Process):
    def __init__(self,proc_class = None):
        super(ExecProcess, self).__init__()
        self.method_dict = dict()
        self.lock = Lock()
        self.proc_class = proc_class
        #self.pipe_out, self.pipe_in = Pipe()
        self.q_msg = Queue(maxsize=1)
        self.q_ret = Queue(maxsize=1)
        
    def run(self):
        
        while self.is_alive():
            
            recv = self.q_msg.get()
            method,args, kwargs= recv
            ret = self.method_dict[method](self.proc_class,*args, **kwargs)
            self.q_ret.put(ret)
            
    
class process_exec(object):
    '''
    '''
    def __init__(self,process ):
        self.process = process
    def __call__(self,function):
        self.process.method_dict[function.__name__] = function
        def _exec(cls,*args, **kwargs):
            with self.process.lock:
                send = (function.__name__,args, kwargs)
                self.process.q_msg.put(send)
                ret = self.process.q_ret.get()
                return ret
        return _exec
        
        #return FunctionWapper(function,self.process)


