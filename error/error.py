class Error(Exception):
    def __init__(self,code,msg):
        self.code = code
        self.msg = msg
