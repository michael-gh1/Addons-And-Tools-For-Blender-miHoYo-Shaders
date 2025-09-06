import bpy
import functools
import inspect
import logging
import os
from typing import Callable, Any
import json


class Logger:
    """Logger class to manage logging to files."""

    def __init__(self, log_file_path: str, log_level: int = logging.INFO, console_output: bool = False):
        """
        Initialize the logger.

        Args:
            log_file_path: Path to the log file
            log_level: Logging level (default: INFO)
            console_output: Whether to also output logs to console
        """
        self.log_file_path = log_file_path
        self.log_level = log_level

        # Create directory for log file if it doesn't exist
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Configure logger
        self.logger = logging.getLogger(f"logger_{log_file_path}")
        self.logger.setLevel(log_level)
        self.logger.handlers.clear()  # Clear existing handlers to avoid duplicates

        # Create file handler
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(log_level)

        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(file_handler)

        # Add console handler if requested
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)


def log_function(custom_log_path: str = None, log_level: int = logging.INFO, console_output: bool = False) -> Callable:
    """
    Decorator to log function calls with arguments and return values.

    Args:
        log_file_path: Path to the log file
        log_level: Logging level (default: INFO)
        console_output: Whether to also output logs to console

    Returns:
        Decorator function
    """
    # Get caller's filename
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    caller_filename = os.path.basename(module.__file__).replace(
        '.py', '') if module.__file__ else 'unknown_module'

    log_file_path = custom_log_path or \
        os.path.join(bpy.utils.user_resource('CONFIG'),
                     'csw_logs', f'{caller_filename}.log')
    logger_instance = Logger(log_file_path, log_level, console_output).logger

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logging_enabled = hasattr(bpy, 'context') and hasattr(bpy.context, 'scene') and not bpy.context.scene.character_setup_wizard_logging_enabled
            if logging_enabled:
                return func(*args, **kwargs)

            func_name = func.__name__
            arg_object = args[0]
            args_start_with_self = hasattr(arg_object, '__class__')

            if args_start_with_self:
                module_name = arg_object.__class__.__module__
                class_name = arg_object.__class__.__qualname__

            try:
                result = func(*args, **kwargs)
                log_message = build_log_message(
                    module_name = module_name,
                    class_name = class_name,
                    func_name=func_name,
                    func_args=args[1:] if args_start_with_self else args,
                    func_kwargs=kwargs,
                    return_value=result,
                )
                logger_instance.info(log_message)
                return result
            except Exception as e:
                log_message = build_log_message(
                    module_name = module_name,
                    class_name = class_name,
                    func_name=func_name,
                    func_args=args[1:] if args_start_with_self else args,
                    func_kwargs=kwargs,
                    exception=str(e),
                )
                logger_instance.exception(log_message)
                raise
        return wrapper
    return decorator


def build_log_message(module_name: str, class_name: str, func_name: str, func_args, func_kwargs, message: str = '', **kwargs) -> str:
    # Create a base log object with standard fields
    log_data = {
        'module': module_name,
        'class': class_name,
        'function': func_name,
        'message': message
    }

    # Handle args and kwargs carefully to ensure they're JSON serializable
    try:
        log_data['args'] = [str(arg) for arg in func_args]
    except:
        log_data['args'] = '<non-serializable>'

    try:
        log_data['kwargs'] = {k: str(v) for k, v in func_kwargs.items()}
    except:
        log_data['kwargs'] = '<non-serializable>'

    # Add any additional kwargs to the log data
    for kwarg in kwargs:
        log_data[kwarg] = str(kwargs[kwarg])

    return json.dumps(
        {
            'log_payload': log_data
        }
    )
