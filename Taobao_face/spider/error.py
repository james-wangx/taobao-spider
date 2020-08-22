class TITLEERROR(Exception):
    """
    自定义异常，以验证网页标题
    """

    def __init__(self, Errorinfo):
        self.errorinfo = Errorinfo

    def __str__(self):
        return self.errorinfo


if __name__ == '__main__':
    try:
        title = 'python'
        if title != 'java':
            raise Exception(f'网页标题错误，标题：{title}')
    except Exception as e:
        print(e)
        print('结束')
