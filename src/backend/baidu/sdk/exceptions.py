from src.const.exceptions import Error

class BaiduError(Error):
    pass

class BaiduUploadError(BaiduError):
    pass

class BaiduUploadPrecreateError(BaiduUploadError):
    pass

class BaiduUploadBlockError(BaiduUploadError):
    pass

class BaiduUploadCreateError(BaiduUploadError):
    pass

class BaiduMakeDirectoryError(BaiduError):
    pass

class BaiduListDirectoryError(BaiduError):
    pass

class BaiduGetFileError(BaiduError):
    pass

