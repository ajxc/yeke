#!/usr/bin/env python3

# ZSH shell:
# > ./wikisource_upload.py /tmp/ysplit/*(n)

import pywikibot
from pywikibot import pagegenerators
from pywikibot.page import Page
import sys
import re

file_paths = sys.argv[1:]
file_paths = list(filter(lambda file_path: '.txt' in file_path and 'p' in file_path, file_paths))

site = pywikibot.Site('ko', 'wikisource')

for file_path in file_paths:
	with open(file_path, 'r') as file:
		p_content = file.read()
		p_content = p_content.strip()

		file_name = re.sub(r'.+\/', '', file_path)
		page_name = re.sub(r'.*(\d)p(\d+).*', r'Page:譯語類解 古 3912-5-v.1-2 GR32256 00 000\1.pdf/\2', file_name)

		page = Page(site, page_name)
		page.text = p_content
		page.save(f'Upload from {file_name}.')
		input('[press enter to proceed to the next page]')