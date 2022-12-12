#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Markus Thilo'
__version__ = '0.1_2022-12-12'
__license__ = 'GPL-3'
__email__ = 'markus.thilo@gmail.com'
__status__ = 'Testing'
__description__ = '''ParaDecoder creates command lines by combining lists
and executing the commands in parallel threads. The initial task was to test
openssl decryption. Other tasks/applications are possible. The files have to
contain one argument per line, e.g. ciphers or passwords. 
'''
__example__ = '''Example:
$ python paradecoder.py -t 4 -v 'openssl {ciphers.txt} -d -pbkdf2
-in sample.enc -k {pw_list.txt}'
'''

from logging import basicConfig as logConfig
from logging import INFO as logINFO
from logging import DEBUG as logDEBUG
from logging import info as log_info
from logging import debug as log_debug
from argparse import ArgumentParser
from pathlib import Path
from subprocess import Popen, PIPE
from time import sleep
from sys import exit as sysexit

class Logger:
	'Logging for this tool'

	def __init__(self, level=logINFO, filename=None):
		'Initiate logging by given level and to given file, None for stdout'
		if filename == None:
			logConfig(level=level, format = '%(message)s')
		else:
			logConfig(
				level=level,
				filename = filename,
				format = '%(asctime)s %(levelname)s: %(message)s',	# log file format
				datefmt = '%Y-%m-%d %H:%M:%S'
			)
			logging.info(f'Start logging to {filename}')

class Exec(Popen):
	'Command to execute, use Popen from subprocess'

	def __init__(self, cmd):
		'Start running command'
		super().__init__(cmd.split(), stdout=PIPE, stderr=PIPE)	# get stdout and stderr

class GenCmd:
	'Generaor for executable command'

	def __init__(self, input):
		'Analize command and make generator'
		raw_slices = input.split('{')
		self.slices = raw_slices[:1]	# outside {}
		self.infiles = []	# inside {}
		for slice in raw_slices[1:]:
			subslices = slice.split('}')
			self.infiles.append(Path(subslices[0]))
			self.slices.append(subslices[1])

	def __get__(self, cmd, infiles, slices):
		'Recursion to buld executable commands'
		if infiles == []:	# all done?
			yield cmd, infiles, slices
		else:
			with open(infiles[0], 'r') as fh:	# open list file
				for line in fh.readlines():	# line by line
					if line != '\n':	# ignore empty lines
						for newcmd, newinfiles, newslices in self.__get__(
							cmd  + line.strip() + slices[0],
							infiles[1:],
							slices[1:]
						):	# update command line
							yield newcmd, newinfiles, newslices

	def get(self):
		'Generator to give commands as string'
		for cmd, infiles, slices in self.__get__(self.slices[0], self.infiles, self.slices[1:]):
			yield cmd

class Threads:
	'Thread handler'

	def __init__(self, cmdgen, maxthreads):
		'Generate list with process handlers'
		self.cmdgen = cmdgen
		self.maxthreads = maxthreads
		self.procs = []	# processes are stored in this list
		while len(self.procs) < self.maxthreads:	# generate initial threads
			if self.add() == None:
				break

	def add(self):
		'Add new thread if maximum is not reached'
		if len(self.procs) < self.maxthreads:	# return none if max threads are reached
			try:	# or no job = command line is left
				cmd = next(self.cmdgen)
			except StopIteration:
				return
			log_debug(f'Threads: trying to execute as thread {len(self.procs)}: {cmd}')
			self.procs.append(Exec(cmd))	# generate new thread
			return len(self.procs)

	def check(self):
		'Check for finished processes and give return code'
		for proc in self.procs:
			if proc.poll() != None:	# poll() gives None while running
				self.procs.remove(proc)	# remove finished thread
				return proc

class Brake:
	'Criteria to end app'

	ENCODING = 'utf-8'	# to decode stdout and stderr

	def __init__(self, brake):
		'Chose brake'
		self.check = {
			'0': self.__exit0__
		}[brake]

	def dec(self, encoded):
		'Try to decode STDOUT or STDERR'
		try:
			return encoded.decode(self.ENCODING) 
		except:
			return None

	def __exit0__(self, proc):
		'Process returned 0?'
		returncode = proc.poll()
		stdout, stderr = proc.communicate()
		return returncode == 0, proc.args, returncode, self.dec(stdout), self.dec(stderr)

class Worker:
	'Main class'

	SLEEP = .1	# inbetween checking

	def __init__(self, cmd, brake, maxthreads):
		'The work is done here'
		log_debug('Starting Worker')
		self.brake = Brake(brake)
		self.threads = Threads(GenCmd(cmd).get(), maxthreads)

	def loop(self):
		'Main loop, returns 0 on brake/success'
		while len(self.threads.procs) > 0:	# while there are running threads
			proc = self.threads.check()	# check for finished threads
			if proc == None:	# do not check at insane intervals
				sleep(self.SLEEP)
				continue
			stdout, stderr = proc.communicate()	# get stdout and stderr
			interrupt, args, returncode, outstr, errstr = self.brake.check(proc)
			if interrupt:	# success?
				log_debug('Worker: Brake returned True')
				log_info(
					'The following command matched the brake criteria:\n' + ' '.join(args)
					+ f'\nReturn Code: {returncode}\nSTDOUT:\n{outstr}\nSTDERR:\n{errstr}'
				)
				return 0
			self.threads.add()
		log_debug('Worker finished: Tried all combinations')
		log_info('Nothing matched.')
		return 1

if __name__ == '__main__':	# start here if called as application
	argparser = ArgumentParser(description=__description__, epilog=__example__)
	argparser.add_argument('-b', '--brake', type=str,  default='0',
		help='Exit on: 0 = exit code is 0 (default)', metavar='STRING'
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
		help='Command to execute, give replacement files in {}', metavar='STRING'
	)
	args = argparser.parse_args()
	if args.verbose:
		loglevel = logDEBUG
	else:
		loglevel = logINFO
	Logger(loglevel, args.logfile)
	worker = Worker(args.cmd[0], args.brake, args.threads)
	sysexit(worker.loop())
