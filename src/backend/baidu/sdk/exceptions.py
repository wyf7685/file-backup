from src.const.exceptions import BackendError


class BaiduError(BackendError):
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
