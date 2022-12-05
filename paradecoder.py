#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Markus Thilo'
__version__ = '0.1_2022-12-05'
__license__ = 'GPL-3'
__email__ = 'markus.thilo@gmail.com'
__status__ = 'Testing'
__description__ = 'Versatile decoder with openssl in mind'

import logging
from configparser import ConfigParser
from threading import Thread
from datetime import datetime
from argparse import ArgumentParser, FileType
from pathlib import Path

from sys import exit as sysexit
from sys import stdout, stderr

class Logger:
	'Logging for this tool'

	def __init__(self, level, filename):
		'Initiate logging by given level and to given file'
		logging.basicConfig(
			level={
				'debug': logging.DEBUG,
				'info': logging.INFO,
				'warning': logging.WARNING,
				'error': logging.ERROR,
				'critical': logging.CRITICAL
			}[level],
			filename = filename,
			format = '%(asctime)s %(levelname)s: %(message)s',
			datefmt = '%Y-%m-%d %H:%M:%S'
		)
		logging.info(f'Start logging to {filename}')
		self.filename = filename	# log to file

class Config:
	'Handle the config file'

	def __init__(self, configfile=Path(__file__).parent / 'zmimport.conf'):
		'Get configuration from file and initiate logging'
		config = ConfigParser()
		config.read(configfile)
		self.loglevel = config['LOGGING']['level']
		self.logfile = Path(config['LOGGING']['filepath'])
		self.csvpath = Path(config['FILELIST']['filepath'])
		self.fieldnames = [ fn.strip(' ') for fn in  config['FILELIST']['fieldnames'].split(',') ]
		self.pgp_cmd = Path(config['PGP']['command'])
		self.pgp_passphrase = config['PGP']['passphrase']
		self.triggerfile = Path(config['TRIGGER']['filepath'])
		self.updates = [ t.strip(' ') for t in config['TRIGGER']['time'].split(',') ]
		self.sleep = int(config['TRIGGER']['sleep'])
		if self.sleep < 60:	# or there will be several polls in one minute
			self.sleep = 60
		self.sourcetype = config['SOURCE']['type'].lower()
		self.sourcepath = Path(config['SOURCE']['path'])
		if self.sourcetype == 'url':
			self.sourcepath = config['SOURCE']['path']
			if self.sourcepath[-1] != '/':
				self.sourcepath += '/'
			self.xpath = config['SOURCE']['xpath']
			self.retries = int(config['SOURCE']['retries'])
			self.retrydelay = int(config['SOURCE']['delay'])
		else:
			self.sourcepath = Path(config['SOURCE']['path'])
			self.xpath = ''
		self.backuppath = Path(config['BACKUP']['path'])
		self.targets = dict()
		for section in config.sections():
			if section[:6] == 'TARGET':
				if section == 'TARGET':
					self.targetpath = Path(config['TARGET']['path'])
				else:
					self.targets[Path(config[section]['path'])] = config[section]['pattern']


class Worker:
	'Main class'

	def __init__(self, config):
		pass

if __name__ == '__main__':	# start here if called as application
	argparser = ArgumentParser(description=__description__)
	argparser.add_argument('-c', '--config', type=Path,
		help='Config file', metavar='FILE'
	)
	argparser.add_argument('-i', '--cipher', type=str,
		help='Cipher commands, default is reading from config file', metavar='STRING'
	)
	argparser.add_argument('-l', '--log', type=Path,
		help='Set logfile (default: paradecoder_STARTTIME.log)', metavar='FILE'
	)
	argparser.add_argument('-w', '--write', type=Path,
		help='Write decoded data to file', metavar='FILE'
	)
	argparser.add_argument('-r', '--pwfile', type=Path,
		help='File with passwords, one per line', metavar='FILE'
	)
	argprser.add_argument('encrypted', nargs=1, type=Path,
		help='Encrypted file to decrypt', metavar='FILE'
	)
	args = argparser.parse_args()
	config = Config(args.config)
	Logger(args.log, config)
	Worker(args.pwfile, args.encrypted, args.write, config)
	sysexit(0)
