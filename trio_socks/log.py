import logging
import sys

def set_level(level):
	logging.basicConfig(
		level=level,
		stream=sys.stdout,
		format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
		datefmt='%H:%M:%S',
	)

set_level(logging.INFO)
def get_logger(name: str) -> logging.Logger:
	return logging.getLogger(name)
