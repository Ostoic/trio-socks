import logging
import sys

logging.basicConfig(
	level=logging.DEBUG,
	stream=sys.stdout,
	format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
	datefmt='%H:%M:%S',
)

loggers = {}

def set_level(level):
	for name, logger in loggers.items():
		logger.setLevel(level)

def get_logger(name: str) -> logging.Logger:
	if name not in loggers:
		loggers[name] = logging.getLogger(name)

	return loggers[name]

