#!/usr/bin/env python3

# ZSH shell:
# > ./split.py *.txt(n) | less

# ch chapter
# p page
# n number

import os
import re
import regex
import sys

p_max_item_count = 10 * 2 # 10 columns with 2 lexical items

file_paths = sys.argv[1:]
file_paths = list(filter(lambda file_path: '.txt' in file_path and 'p' in file_path, file_paths))

books = {
	1: {},
	2: {},
}

for file_path in file_paths:
	with open(file_path, 'r') as file:
		ch_content = file.read()
		ch_content = ch_content.strip()

		# get from file name
		# book number, chapter page number, chapter name
		m = re.search(r'(\d+)p(\d+) ([^ .-]+)', file_path)
		book_n, ch_p_n, ch_name = int(m[1]), int(m[2]), m[3]

		# mark chapter beginning
		ch_content = regex.sub(
			r'#(?!\d)',
			'BOCh' + ch_name + r'BOCh#',
			ch_content,
			count = 1
		)

		# individual pages
		p_content_all = ch_content.split('\n\n')

		for p_content in p_content_all:
			# get page number
			m = re.search(r'p(\d+)', p_content)
			p_n = (int(m[1]) if m else ch_p_n)

			# find lexical items
			# reading is optional, see book 2 page 87
			# gloss is multiple, see book 1 page 4
			lexical_items = regex.findall(
				r'(?:BOCh(.+)BOCh)?' + # 0 chapter name normalized
				r'(#\d*)?' + # 1 header level
				r'(.*\p{Script=Hani}.*\n)' + # 2 headword
				r'(?:(.*\p{Script=Hang}.*\n)(.*\p{Script=Hang}.*\n))?' + # 3 4reading
				r'((?:○.+\n)*)', # 5 gloss
				p_content + '\n'
			)

			# find pages that are 'too long'
			if len(lexical_items) > p_max_item_count:
				print(f'{file_path} | p{p_n} too long: {len(lexical_items)}')
				for i, lexical_item in enumerate(lexical_items):
					print(i + 1, lexical_item)

			# record page number and lexical items
			if not p_n in books[book_n]:
				books[book_n][p_n] = []
			books[book_n][p_n] += lexical_items

			ch_p_n += 1

for book_n in books:
	try:
		os.mkdir(f'/tmp/{book_n}')
	except FileExistsError:
		pass

	ch_name_previous = ''

	for p_n in books[book_n]:
		lexical_items = books[book_n][p_n]

		# find pages that are 'too long'
		if len(lexical_items) > p_max_item_count:
			print(f'b{book_n} p{p_n} too long: {len(lexical_items)}')
			for i, lexical_item in enumerate(lexical_items):
				print(i + 1, lexical_item)
		# approximately find pages that are 'too short'
		# subtract 2, as when there are two chapter titles on one page
		elif len(lexical_items) < p_max_item_count - 2:
			if book_n == 1 and p_n == 120:
				continue
			elif book_n == 1 and p_n == 140:
				continue
			elif book_n == 2 and p_n == 18:
				continue
			elif book_n == 2 and p_n == 109:
				continue
			print(f'b{book_n} p{p_n} too short: {len(lexical_items)}')
			for i, lexical_item in enumerate(lexical_items):
				print(i + 1, lexical_item)

		with open(f'/tmp/{book_n}/{p_n}', 'w') as file:
			for lexical_item in lexical_items:
				if lexical_item[0] != '':
					#print(ch_name_previous, lexical_item[0])
					if ch_name_previous != '':
						file.write('<section end="' + ch_name_previous + '" />')
					file.write('<section begin="' + lexical_item[0] + '" />')
					ch_name_previous = lexical_item[0]

				if lexical_item[1] != '':
					header_level = lexical_item[1].replace('#', '') or 2
					file.write(f'<h{header_level}>\n')

				file.write(';' + lexical_item[2])
				if lexical_item[3] != '':
					file.write(':' + lexical_item[3])
				if lexical_item[4] != '':
					file.write(':' + lexical_item[4])
				if lexical_item[5] != '':
					for line in lexical_item[5].strip().split('\n'):
						file.write(':' + line + '\n')

				if lexical_item[1] != '':
					file.write(f'</h{header_level}>\n')
