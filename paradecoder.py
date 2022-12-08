#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Markus Thilo'
__version__ = '0.1_2022-12-08'
__license__ = 'GPL-3'
__email__ = 'markus.thilo@gmail.com'
__status__ = 'Testing'
__description__ = 'Versatile decoder with openssl in mind'

import logging
from argparse import ArgumentParser
from pathlib import Path
from subprocess import Popen, PIPE
from time import sleep
from sys import exit as sysexit

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

class Exec(Popen):
	'Command to execute'

	def __init__(self, cmd):
		'Start running command'
		super().__init__(cmd.split())#, stdout=PIPE)

class GenCmd:
	'Generaor for executable command'

	def __init__(self, input):
		'Analize command and make generator'
		raw_slices = input.split('{')
		self.slices = raw_slices[:1]
		self.infiles = []
		for slice in raw_slices[1:]:
			subslices = slice.split('}')
			self.infiles.append(Path(subslices[0]))
			self.slices.append(subslices[1])

	def __get__(self, cmd, infiles, slices):
		'Recursion to buld executable commands'
		if infiles == []:
			yield cmd, infiles, slices
		else:
			with open(infiles[0], 'r') as fh:
				for line in fh.readlines():
					if line != '\n':
						for newcmd, newinfiles, newslices in self.__get__(
							cmd  + line.strip() + slices[0],
							infiles[1:],
							slices[1:]
						):
							yield newcmd, newinfiles, newslices

	def get(self):
		'Give commands as string'
		for cmd, infiles, slices in self.__get__(self.slices[0], self.infiles, self.slices[1:]):
			yield cmd

class Threads:
	'Thread handler'

	def __init__(self, cmdgen, maxthreads):
		'Generate list with process handlers'
		self.cmdgen = cmdgen
		self.maxthreads = maxthreads
		self.procs = []
		while len(self.procs) < self.maxthreads:
			if self.add() == None:
				break

	def add(self):
		if len(self.procs) < self.maxthreads:
			try:
				cmd = next(self.cmdgen)
			except StopIteration:
				return None
			logging.debug(f'Threads: Trying to execute as thread {len(self.procs)}: {cmd}')
			self.procs.append(Exec(cmd))
			return len(self.procs)

	def check(self):
		'Check for finished processes and give return code'
		for proc in self.procs:
			returncode = proc.poll()
			if returncode != None:
				self.procs.remove(proc)
				return returncode

class Brake:
	'Criteria to end app'

	def __init__(self, brake):
		'Chose brake'
		self.check = {
			'0': self.__exit0__
		}[brake]

	def __exit0__(self, returncode):
		'Process returned 0?'
		return returncode == 0

class Worker:
	'Main class'

	def __init__(self, cmd, brake, maxthreads):
		logging.debug('Starting Worker')
		cmd = GenCmd(cmd).get()
		brake = Brake(brake)
		print(brake)
		threads = Threads(cmd, maxthreads)
		while len(threads.procs) > 0:
			returncode = threads.check()
			if returncode == None:
				sleep(.1)
				continue
			if brake.check(returncode):
				logging.info('Brake')
				return
			threads.add()
		logging.info('Finished: tried all combinations.')

if __name__ == '__main__':	# start here if called as application
	argparser = ArgumentParser(description=__description__)
	argparser.add_argument('-b', '--brake', type=str,  default='0',
		help='Brake on: 0 = exit code is 0 (default)', metavar='STRING'
	)
	argparser.add_argument('-l', '--logfile', type=Path,
		help='Set logfile', metavar='FILE'
	)
	argparser.add_argument('-t', '--threads', type=int,  default=1,
		help='Number of threads (default: 1)', metavar='INTEGER'
	)
	argparser.add_argument('-v', '--verbose', action='store_true',
		help='Set loglevel debug'
	)
	argparser.add_argument('cmd', type=str,  nargs=1,
		help='Command to execute', metavar='STRING'
	)
	args = argparser.parse_args()
	if args.verbose:
		loglevel = logging.DEBUG
	else:
		loglevel = logging.ERROR
	Logger(loglevel, args.logfile)
	Worker(args.cmd[0], args.brake, args.threads)
	sysexit(0)
