#!/usr/bin/python3.8

import sys
import yaml
import re

# Returns line number of a line  in file
def get_field_line_number(field, file_lines):
	line = 1

	for file_line in file_lines:
		if file_line.startswith(field):
			return line
		line += 1

	return 1 # Field not found; put warning at top of file

# TODO: Refactor into class
def check_format(filename):
	req = {}

	line = 1
	message = ''
	errors = '\n'

	try:
		# Read in requirement file lines
		with open( filename, 'r') as file:
			req_lines = file.readlines()
		# Read in requirement as YAML
		with open( filename, 'r') as file:
			req_yaml = yaml.safe_load(file)
		req_fields = list(req_yaml.keys())
		req_fields_alpha = sorted(req_fields)
		
		# All fields present
		with open('scripts/template.yml', 'r') as file:
			template_yaml = yaml.safe_load(file)
		template_fields_alpha = sorted(list(template_yaml.keys()))

		if req_fields_alpha != template_fields_alpha:
			missing_fields = list(set(template_fields_alpha) - set(req_fields_alpha))
			message = 'missing fields ' + str(missing_fields) + '\n'
			errors += f'::error file={filename},line=1::{message}' # Put warning at top of file

		# Fields in alphabetical order
		if req_fields != template_fields_alpha:
			message = 'fields not in alphabetical order\n'
			errors += f'::error file={filename},line=1::{message}' # Put warning at top of file

		# Component
		if 'component allocation' in req_fields:
			components = []
			with open('scripts/components.txt', 'r') as file:
				for line in file.readlines():
					components.append(line.strip()) # Strip ending \n

			if req_yaml['component allocation'] not in components:
				line = get_field_line_number('component allocation', req_lines)
				message = 'component allocation not listed in scripts/components.txt \"' + req_yaml['component allocation'] + '\"\n'
				errors += f'::error file={filename},line={line}::{message}'

		# Name
		if 'name' in req_fields:
			if '.' in req_yaml['name']:
				line = get_field_line_number('name', req_lines)
				message = 'name is not one sentence not ended by period \n'
				errors += f'::error file={filename},line={line}::{message}'
			# TODO: Capitalization

		# Text is one sentence ending in period
		if 'text' in req_fields:
			line = get_field_line_number('text', req_lines)
			if '.' not in req_yaml['text']:
				message = 'text does not end in a period\n'
				errors += f'::error file={filename},line={line}::{message}'
			elif req_yaml['text'].count('.') > 1 or \
					not req_yaml['text'].strip().endswith('.'):
				message = 'text has more than one sentence\n'
				errors += f'::error file={filename},line={line}::{message}'
			# TODO: Trailing spaces?
			# TODO: Capitalization

		# Release
		if 'release' in req_fields:
			format = 'v\d\.\d\.0'
			if not re.fullmatch(format, req_yaml['release']):
				line = get_field_line_number('release', req_lines)
				message = 'release doesn\'t match format v#.#.0\n'
				errors += f'::error file={filename},line={line}::{message}'

	except EnvironmentError: # File does not exist or an IO error occurred
		errors += '::error file=' + filename + '::GitHub environment error; couldn\'t read file ' + filename + '\n'

	return errors

if __name__ == "__main__":
	filename = str(sys.argv[1])

	print(check_format(filename))
