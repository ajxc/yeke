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

		# get things from file name:
		# book number, chapter page number, chapter name
		m = re.search(r'(\d+)p(\d+) ([^ .-]+)', file_path)
		book_n, ch_p_n, ch_name = int(m[1]), int(m[2]), m[3]

		# mark chapter beginning
		ch_content = re.sub(
			r'#(?!\d)',
			'BOCh' + ch_name + r'BOCh#',
			ch_content,
			count = 1
		)

		# reformat note markup
		# icheja: [真 眞*]
		# write "ICHEJA" instead of "이체자" to avoid disrupting the regex below that detects reading by looking for hangeul
		ch_content = regex.sub(
			r'\[([^ \]]+) (\p{Script=Hani})\*\]',
			r'{{ICHEJA|\1|\2}}',
			ch_content
		)
		# icheja: 眞*
		ch_content = regex.sub(
			r'(\p{Script=Hani})\*',
			r'{{ICHEJA|\1}}',
			ch_content
		)
		# correction: [豬 豚]
		ch_content = regex.sub(
			r'\[(\p{Script=Hani}) (\p{Script=Hani})\]',
			r'{{SIC|\1|\2}}',
			ch_content
		)
		# correction: [쭈 쮸]
		ch_content = regex.sub(
			r'\[(\p{Script=Hang}+) (\p{Script=Hang}+)\]',
			r'{{SIC|\1|\2}}',
			ch_content
		)
		# correction: [화 sic]
		ch_content = regex.sub(
			r'\[(\p{Script=Hang}+) sic\]',
			r'{{SIC|\1}}',
			ch_content
		)
		# correction: [궈 illegible]
		ch_content = regex.sub(
			r'\[([^ \]]+) illegible\]',
			r'{{reconstruct|\1}}',
			ch_content
		)
		# correction: [녀 ?]
		ch_content = regex.sub(
			r'\[([^ \]]+) \?\]',
			r'{{suspect|\1}}',
			ch_content
		)
		# correction: [于 了?]
		# technically Template:suspect does not have a second parameter
		ch_content = regex.sub(
			r'\[([^ \]]+) ([^]]+)\?\]',
			r'{{suspect|\1|\2}}',
			ch_content
		)
		# correction: [壯 狀 according to owner's annotation]
		pass

		# split into individual pages
		p_content_all = ch_content.split('\n\n')

		for p_content in p_content_all:
			# get page number
			match = re.search(r'p(\d+)', p_content)
			p_n = (int(match[1]) if match else ch_p_n)

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
		os.mkdir(f'/tmp/ysplit')
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

		with open(f'/tmp/ysplit/{book_n}p{p_n}.txt', 'w') as file:
			for lexical_item in lexical_items:
				# final tidying
				lexical_item = list(lexical_item) # TypeError: 'tuple' object does not support item assignment
				for i, property in enumerate(lexical_item):
					lexical_item[i] = lexical_item[i].replace('ICHEJA', '이체자')

				if lexical_item[0] != '':
					#print(ch_name_previous, lexical_item[0])

					#
					# WARNING: does not add section end to the final chapter of a book
					#

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
