#!/usr/bin/python

import time
import os
import sys, traceback
import logging
import logging.handlers
import subprocess

#################
#  LOGGING SETUP
#################
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler('/home/pi/wifimonitor/wifi_monitor.log', when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
	def __init__(self, logger, level):
		"""Needs a logger and a logger level."""
		self.logger = logger
		self.level = level

	def write(self, message):
		# Only log if there is a message (not just a new line)
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

logger.info('Starting Wifi monitoring service')

while(True):

	try:
		logger.info('\n========= Checking Wifi connectivity =========')

		try:
			out_bytes = subprocess.check_output("ping -c 4 192.168.0.13", shell=True, stderr=subprocess.STDOUT)
			logger.info("Ping to server is OK")

			# Log iwconfig info
			logger.info('*** Logging iwconfig info ***')
			try:
				out_bytes = subprocess.check_output("iwconfig", shell=True, stderr=subprocess.STDOUT)
			except subprocess.CalledProcessError as e:
				out_bytes = e.output       # Output generated before error
				code      = e.returncode   # Return code
			logger.info(out_bytes)

		except subprocess.CalledProcessError as e:
			out_bytes = e.output       # Output generated before error
			code      = e.returncode   # Return code
			logger.info(out_bytes)
			logger.info("Ping to server is KO (code="+str(code)+")")

			# Log ifconfig info
			logger.info('*** Logging ifconfig info ***')
			try:
				out_bytes = subprocess.check_output("ifconfig", shell=True, stderr=subprocess.STDOUT)
			except subprocess.CalledProcessError as e:
				out_bytes = e.output       # Output generated before error
				code      = e.returncode   # Return code
			logger.info(out_bytes)

		time.sleep(60)

	except:
		logger.info("*****Exception in main loop, continuing in 60 seconds******")
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)	
		del exc_traceback
		time.sleep(60.0)
		continue


   
