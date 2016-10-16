# endcoding = utf-8
'''
author : vex1023
email : vex1023@qq.com
'''


ERROR_TEMPLATE = '''{"error_code": "%s", "error_msg": "%s", "reason": "%s"}'''


class APIError(Exception):
    '''
    交易错误和代码定义
    '''
    ERROR_CODE = '0'
    ERROR_MSG = 'Success'

    def __init__(self, reason):
        super(TraderError, self).__init__(ERROR_TEMPLATE % (self.ERROR_CODE, self.ERROR_MSG, reason))

class InternalError(APIError):
    ERROR_CODE = '999'
    ERROR_MSG = 'Internal Error'

    pass


