import os
import sys
import time
import logging


class ProjectLogger(logging.Logger):
    """
    Logger class.
    Logs writes to file with name in format of date and time of creating logger's instance. All log files are
    stored in directory logs near the script which has module name "__main__" at run time.

    Important: To activate logging the level of log messages should be set.
    """
    def __init__(self, name):
        super().__init__(name)

        self.__log_directory = "logs"
        if not os.path.exists(self.__log_directory):
            os.mkdir(self.__log_directory)
        self.__log_file = os.path.join(self.__log_directory,
                                       time.strftime("%d_%m_%Y_%H_%M_%S.log", time.localtime(time.time())))

        self.__formatter = logging.Formatter(
            "%(levelname)s %(asctime)s %(filename)s %(funcName)s(): %(message)s", "%Y-%m-%d %H:%M:%S")

        self.propagate = True

        self._set_console_handler()
        self._set_file_handler()

    def _set_file_handler(self):
        file_handler = logging.FileHandler(self.__log_file)
        file_handler.setFormatter(self.__formatter)
        self.addHandler(file_handler)

    def _set_console_handler(self):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(self.__formatter)
        self.addHandler(stream_handler)

    def set_level(self, level):
        """
        Set level of log messages.

        :param level: string, one of five levels ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        self.setLevel(level)


logger = ProjectLogger("RLFR")
