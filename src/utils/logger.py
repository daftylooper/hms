import inspect
from datetime import datetime

class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR" 
    CRITICAL = "CRITICAL"

# log levels - DEBUG, INFO, WARNING, ERROR, CRITICAL
def log(level, message):
    # get calling frame context
    frame = inspect.currentframe().f_back
    file_name = frame.f_code.co_filename
    line_number = frame.f_lineno

    function_name = frame.f_code.co_name
    class_name = None
    for cls in inspect.getouterframes(frame):
        if cls.function != '<module>':
            if 'self' in frame.f_locals:
                class_name = frame.f_locals['self'].__class__.__name__
            break

    # build log details
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    context = f"{file_name}:{line_number}"
    if class_name:
        context += f" {class_name}.{function_name}"
    else:
        context += f" {function_name}"

    log_message = f"[{formatted_time}] [{level.upper()}] [{context}] {message}"
    print(log_message)

Level = LogLevel()

# class ExampleClass:
#     def example_method(self):
#         log("info", "This is a log message from inside a method.")

# def example_function():
#     log("debug", "This is a log message from inside a function.")

# if __name__ == "__main__":
#     example_function()
#     example_instance = ExampleClass()
#     example_instance.example_method()
