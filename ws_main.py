#!/usr/bin/env python3

# grep -E '<section[^>]+>' --only-matching */*(n) | sed -E 's/yy|<section | *\/>//g' | ./a.py | xclip -selection clipboard
# https://ko.wikisource.org/w/index.php?title=위키문헌%3A연습장&action=historysubmit&type=revision&diff=219726&oldid=219725

import sys
import re

lines = []

template = """
{{머리말
| 제목 = [[../|譯語類解]]
| 다른 표기 = 역어유해
| 부제 = {{SUBPAGENAME}}
| 부제 다른 표기 =
| 저자 = [[Author:김경준|金敬俊(김경준)]] 등
| 편집자 =
| 역자 =
| 이전 = [[../<previous_chapter>/]]
| 다음 = [[../<next_chapter>/]]
| 설명 =
}}

<pages index="譯語類解_古_3912-5-v.1-2_GR32256_00_000<begin_volume>.pdf" from=<begin_page_number> to=<end_page_number> fromsection="{{SUBPAGENAME}}" tosection="{{SUBPAGENAME}}" />
"""

print('{{{{{|safesubst:}}}#switch:{{{{{|safesubst:}}}SUBPAGENAME}}')

for line in sys.stdin: # pipe input
	lines.append(line)

chapters = []

for i in range(0, len(lines), 2):
	lines[i] = re.search(r'(.+)/(.+):begin="(.+)"', lines[i])
	lines[i + 1] = re.search(r'(.+)/(.+):end="(.+)"', lines[i + 1])

for i in range(0, len(lines), 2):
	previous = lines[i - 1]
	begin = lines[i]
	end = lines[i + 1]
	try:
		next = lines[i + 1 + 1]
	except:
		pass

	begin_volume, begin_page_number, begin_chapter = begin.group(1), begin.group(2), begin.group(3)
	end_volume, end_page_number, end_chapter = end.group(1), end.group(2), end.group(3)

	previous_chapter = previous.group(3)
	next_chapter = next.group(3)

	if begin_chapter != end_chapter:
		raise ValueError(f'The chapter name for this data pair is not the same. {begin_chapter}, {end_chapter}')

	VARS = vars()

	print(f'|{begin_chapter}=')
	print(re.sub(r'<([a-z_]+)>', lambda matchobj: VARS[matchobj.group(1)], template))

print('}}')