

class BaseException(Exception):
    default_msg: str
    
    def __init__(
        self,
        instance: object=None,
        msg: str=None,
        additional_msg: str=None
    ) -> None:
        if additional_msg:
            self.default_msg += additional_msg
            
        msg = msg or self.default_msg
        
        if instance:
            msg = f"{msg} (class: {instance.__class__.__name__})"
        
        super().__init__(msg)


class NonEmptyDirectoryError(BaseException):
    """Raised when the target directory for project initialization is not empty."""
    default_msg = 'Root directory must be empty'


class ConfigurationError(BaseException):
    default_msg = 'The configuration is missing. '

class DatabaseConfigurationError(BaseException):
    default_msg = (
        "Base database failed to connect. "
        "Please check your database or configuration."
    )
    
class EmptyArgumentError(BaseException):
    default_msg = (
        "No arguments were provided. Please refer to the help.\n"
        " $ boomba --help"
    )
    
class LogConfigurationError(BaseException):
    default_msg = "The log configuration has not been set."
    
class DirectoryNotFoundError(BaseException):
    default_msg = "There is no such directory."
    
class ModuleLocationError(BaseException):
    default_msg = (
        "The Location class can only be used "
        "within the apps of the pipeline. "
        "The current usage location is inappropriate. "
        "module Location : "
    )

class PipeNotFoundError(BaseException):
    default_msg = (
        "The Load class requires an app "
        "to be registered in the pipeline before use."
    )
    
class UndefinedMethodError(BaseException):
    default_msg = "Method not implemented. method="
    
class UndefinedAttributeError(BaseException):
    default_msg = "Missing required attribute: "
    
