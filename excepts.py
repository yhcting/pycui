class CUIBaseException(Exception):
    def __init__(self, msg=''):
        super(CUIBaseException, self).__init__(msg)


class CUIInvalidArgumentException(CUIBaseException):
    def __init__(self, msg=''):
        super(CUIInvalidArgumentException, self).__init__(msg)
