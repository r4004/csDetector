import logging


def get_cadocs_logger(name):

    # Create a custom logger
    logging.basicConfig(level=logging.INFO)

    cadocs_logger = logging.getLogger(name)
    cadocs_logger.propagate = False
    # Create handlers
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    c_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    c_handler.setFormatter(c_format)

    # Add handlers to the logger
    cadocs_logger.addHandler(c_handler)
    return cadocs_logger
