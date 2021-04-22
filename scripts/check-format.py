#!/usr/bin/python3

import sys
import yaml

# Default Doorstop fields must be present
# Zephyr fields must comply with following rules:
# - Text must be a sentence starting with a capital letter and ending with a period
# - TODO: Text must follow structure defined by Safety Working Group
# - Name must be a sentence starting with a capital letter and ending without a period
# - Release must be in the form 'v#.#.#' (TODO: Always #.#.0?)
# Fields must be in alphabetical order

def check_format(filename):
	# Errors formatted in GitHub warning format to be echoed by workflow action:
	# ::error file={name},line={line}::{message}
	errors = ""

	req = {}
	try:
		# Read in requirement YAML file
		with open(filename, 'r') as file:
			req_yaml = yaml.safe_load(file)
		req_fields = list(req_yaml.keys())
		req_fields_alpha = sorted(req_fields)
		
		# All fields present
		with open('template.yml', 'r') as file:
			template_yaml = yaml.safe_load(file)
		template_fields_alpha = sorted(list(template_yaml.keys()))

		if req_fields_alpha != template_fields_alpha:
			missing_fields = list(set(template_fields_alpha) - set(req_fields_alpha))
			errors += '::error file=' + filename + '::format error; missing fields ' + \
						missing_fields + '\n'

		# Fields in alphabetical order
		if req_fields != template_fields_alpha:
			errors += '::error file=' + filename + '::format error; fields not in alphabetical order\n'

		# Component
		components = []
		with open('components.txt', 'r') as file:
			for line in file.readlines():
				components.append(line.strip()) # Strip ending \n
		if req_yaml['component allocation'] not in components:
			errors += '::error file=' + filename + '::format warning; previously unused component allocation \"' + req_yaml['component allocation'] + '\"\n'

		# Name
		if '.' in req_yaml['name']:
			errors += '::error file=' + filename + '::format error; name is not one sentence not ended by period \n'
		# TODO: Capitalization

		# Text is one sentence ending in period
		if '.' not in req_yaml['text']:
			errors += '::error file=' + filename + '::format error; text does not end in a period\n'
		elif req_yaml['text'].count('.') > 1 or \
				not req_yaml['text'].endswith('.'):
			errors += '::error file=' + filename + '::format error; text has more than one sentence\n'
		# TODO: Capitalization

		# Release
		# TODO: Regex match 'v#.#.0'

	except EnvironmentError: # File does not exist or an IO error occurred
		errors += '::error file=' + filename + '::GitHub environment error; couldn\'t read file\n'

	return errors


if __name__ == "__main__":
	filename = str(sys.argv[0])

	print(check_format(filename))
