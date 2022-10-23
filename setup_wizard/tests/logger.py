import logging
import logging.config


class Logger:
    def __init__(self, filename):
        # set up logging to file
        logging.basicConfig(
            filename=filename,
            level=logging.INFO, 
            format= '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            force=True
        )

        # set up logging to console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        # set a format which is simpler for console use
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)

        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

        logger = logging.getLogger(__name__)
        logger.info('Logger finished initialization')
