import os
import inspect
from datetime import datetime

class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR" 
    CRITICAL = "CRITICAL"


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def log(level, message):
    # get the frame of the caller
    frame = inspect.currentframe().f_back
    
    file_name = frame.f_code.co_filename  # get file name of where called
    line_number = frame.f_lineno         # line number
    function_name = frame.f_code.co_name # name of calling function

    # check if called from class method
    class_name = None
    for cls in inspect.getouterframes(frame):
        if cls.function != '<module>':
            # if frame is not of type module( function ) and has self, then it is a class method
            if 'self' in frame.f_locals:
                class_name = frame.f_locals['self'].__class__.__name__
            break

    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # build context string, basically the log
    context = f"{file_name}:{line_number}"
    if class_name:
        context += f" {class_name}.{function_name}"
    else:
        context += f" {function_name}"

    # build the log message
    log_message = f"[{formatted_time}] [{level.upper()}] [{context}] {message}"
    with open(LOG_FILE, 'a') as f:
        f.write(log_message + '\n')

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
