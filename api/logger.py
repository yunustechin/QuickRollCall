import logging
import json
import sys

class JsonFormatter(logging.Formatter):
    def format(self, record):
        """
        Formats the log record into a JSON string.

        Args:
            record (logging.LogRecord): The original log record.

        Returns:
            str: A JSON string representation of the log record.
        """
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "source": record.name
        }

        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
        
        return json.dumps(log_record)
    
def setup_logging():
    """Configures the root logger for the application to use the JsonFormatter."""
    if logging.getLogger().hasHandlers():
         return
        
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter()
    handler.setFormatter(formatter)

    logger.addHandler(handler)

def log_info(event: str, details: dict = None):
    """
    Logs an informational event with structured details.

    Args:
        event (str): A string describing the event being logged.
        details (dict, optional): A dictionary of additional key-value
                                  pairs to include in the JSON log.
    """
    logging.info(event, extra={'extra_data': details or {}})

def log_error(event: str, err: Exception, details: dict = None):
    """
    Logs an error event with structured details, including exception info.

    Args:
        event (str): A string describing the context of the error.
        err (Exception): The exception object that was caught.
        details (dict, optional): A dictionary of additional key-value
                                  pairs to provide more context.
    """
    error_details = {
        "event": event,
        "error_type": type(err).__name__,
        "error_message": str(err)
    }

    if details:
        error_details.update(details)
        
    logging.error(event, extra={'extra_data': error_details})
