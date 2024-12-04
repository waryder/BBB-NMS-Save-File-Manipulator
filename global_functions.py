from imports import *

def global_log_to_file(message, mode='a'):
    print(message)
    with open("sfm.log", mode) as log_file:  # Open in append mode
        log_file.write(message + "\n")  # Append the message to the file


def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Let KeyboardInterrupt exceptions pass through without logging
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

        # Print the error and traceback
    logger.error(f"Unhandled exception: {exc_value}")
    traceback.print_exception(exc_type, exc_value, exc_traceback)