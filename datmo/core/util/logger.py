import hashlib
import logging
import os
import tempfile
from datmo.core.util.misc_functions import grep

# https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/

class DatmoLogger(object):
    instance = None
    class __InternalObj:
        def __init__(self):
            # CRITICAL	50
            # ERROR	40
            # WARNING	30
            # INFO	20
            # DEBUG	10
            # NOTSET 0
            self.logging_level = 20
            self.logging_path = os.path.join(os.path.expanduser("~"),'.datmo','logs')
            self.loggers = {}
            if not os.path.exists(self.logging_path):
                os.makedirs(self.logging_path)

    def __new__(cls): # __new__ always a classmethod
        if not DatmoLogger.instance:
            DatmoLogger.instance = DatmoLogger.__InternalObj()
        return DatmoLogger.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)

    @staticmethod
    def get_logfiles():
        return map(lambda f: os.path.join(DatmoLogger().logging_path,f), os.listdir(DatmoLogger().logging_path))

    @staticmethod
    def find_text_in_logs(text_str):
        results = []
        for logfile in DatmoLogger.get_logfiles():
            with open(logfile,"r") as f:
                for r in grep(text_str, f):
                    results.append({
                      "file": logfile,
                      "line_number": r[0],
                      "line": r[1]
                    })
        return results

    @staticmethod
    def get_logger(name = __name__, file_name="log.txt"):
        """Returns a python logger with logging level set

        Parameters
        ----------
        name : string
          Name of the logger.  eg datmo.core.snapshot or __name__

        file_name : string
          Log file name. default = log.txt

        Returns
        -------
        logging.Logger
          Python logger

        """

        # get or create logging path
        if DatmoLogger().logging_path == None:
            DatmoLogger().logging_path = tempfile.mkdtemp()

        logging_path = DatmoLogger().logging_path
        logfile_path = os.path.join(logging_path, file_name)

        if not os.path.exists(logging_path):
            os.makedirs(logging_path)

        # cache the logger and return it otherwise handlers will get added multiple times
        # and result in multiple messages to the same file
        logger_hash = hashlib.sha1(name + file_name).hexdigest()

        if logger_hash in DatmoLogger().loggers:
            # if the file still exists then use cached logger
            # if the file has been deleted manually, then empty cached obj
            # and re-initialize
            if os.path.exists(logfile_path):
                return DatmoLogger().loggers[logger_hash]
            else:
                DatmoLogger().loggers[logger_hash] = None

        # create logger based on name
        log = logging.getLogger(logger_hash)
        log.setLevel(DatmoLogger().logging_level)

        # cache logger
        DatmoLogger().loggers[logger_hash] = log

        # console logging
        # log_stdout = logging.StreamHandler("ext://sys.stdout")
        # log_stdout.setLevel(logging.DEBUG)
        # log.addHandler(log_stdout)

        log_file_handler = logging.handlers.RotatingFileHandler(logfile_path)
        log_file_handler.maxBytes = 10485760
        log_file_handler.backupCount = 10
        log_file_handler.setLevel(DatmoLogger().logging_level)
        log_file_handler.setFormatter(
            logging.Formatter('%(asctime)s - ['+name+'@%(module)s.%(funcName)s] [%(levelname)s] - %(message)s')
        )
        log.addHandler(log_file_handler)

        return log









