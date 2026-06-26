class FileValidationError(Exception):
    pass


class UnsupportedFileType(FileValidationError):
    pass


class FileTooLarge(FileValidationError):
    pass
