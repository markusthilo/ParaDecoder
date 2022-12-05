#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Markus Thilo'
__version__ = '0.1_2022-12-05'
__license__ = 'GPL-3'
__email__ = 'markus.thilo@gmail.com'
__status__ = 'Testing'
__description__ = 'Versatile decoder with openssl in mind'

import logging
from threading import Thread
from datetime import datetime
from argparse import ArgumentParser, FileType
from pathlib import Path

from sys import exit as sysexit
from sys import stdout, stderr

class Logger:
	'Logging for this tool'

	def __init__(self, level=logging.ERROR, filename=None):
		'Initiate logging by given level and to given file'
		if filename == None:
			logging.basicConfig(level=level, format = '%(message)s')
		else:
			logging.basicConfig(
				level=level,
				filename = filename,
				format = '%(asctime)s %(levelname)s: %(message)s',
				datefmt = '%Y-%m-%d %H:%M:%S'
			)
			logging.info(f'Start logging to {filename}')




class Worker:
	'Main class'

	def __init__(self, cmd, files):
		logging.debug('Starting Worker')

if __name__ == '__main__':	# start here if called as application
	argparser = ArgumentParser(description=__description__)
	argparser.add_argument('-c', '--cmd', type=Path,  required=True,
		help='Command to execute', metavar='STRING'
	)
	argparser.add_argument('-l', '--logfile', type=Path,
		help=f'Set logfile', metavar='FILE'
	)
	argparser.add_argument('-v', '--verbose', action='store_true',
		help=f'Set loglevel debug'
	)
	argparser.add_argument('infiles', nargs='+', type=Path,
		help='Files with arguments to test', metavar='FILE'
	)
	args = argparser.parse_args()
	if args.verbose:
		loglevel = logging.DEBUG
	else:
		loglevel = logging.ERROR
	Logger(loglevel, args.logfile)
	Worker(args.cmd, args.infiles)
	sysexit(0)
