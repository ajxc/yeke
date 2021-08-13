#!/usr/bin/env python3

# python3 a.py yeokhae*/*

# TODO
# https://ko.wikisource.org/wiki/페이지:譯語類解_古_3912-5-v.1-2_GR32256_00_0001.pdf/117
# ○通稱계집
# ○一云老ᄅᅶ婆포

import sys
import re

file_paths = sys.argv[1:]
file_paths = list(filter(lambda file_path: 'yeokhae' in file_path, file_paths))

keywords = ['一云', '或云', '或呼', '俗呼', '舊本', '俗音', '或作', '一作', '一名', '又音', '俗稱', '或曰', '舊釋', '或稱', '通稱', '方音', '南話']
keywords_search = re.compile('|'.join(keywords))

found = {}

for file_path in file_paths:
	with open(file_path, 'r') as file:
		p_content = file.read()
		p_content = p_content.strip()

		p_content = re.sub(r'{{이체자\|([^|}]+)\|([^|}]+)}}', r'\2', p_content)
		p_content = re.sub(r'{{이체자\|([^|}]+)}}', r'\1', p_content)

		for (match, gloss) in re.findall(r'(;.+\n' + r':.+\n' + r':.+\n' + r'(:[^\n]*○[^;]*' + r':.+\n))', p_content):
			page_link = re.sub(r'yeokhae(.+)/(.+)', r'=== [[Page:譯語類解 古 3912-5-v.1-2 GR32256 00 000\1.pdf/\2|\1-\2]] ===', file_path)
			keyword_found = re.search(keywords_search, gloss)

			if keyword_found:
				keyword_found = keyword_found[0]

			if not keyword_found in found:
				found[keyword_found] = []
			found[keyword_found].append((page_link, match, gloss))

for keyword_found in sorted(found, key = lambda k: len(found[k])):
	print(f'== {keyword_found} ==\n')
	for x in found[keyword_found]:
		print(x[0] + '\n' + x[1])