import logging

class Logger():
    _logger = None
    @classmethod
    def logger(cls):
        if cls._logger is None:
            logger = logging.getLogger("airbot")
            formatter = logging.Formatter("%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            cls._logger = logger
        return cls._logger

def logger() :
    return Logger.logger()



if __name__=="__main__" :
    logger().debug("hello")