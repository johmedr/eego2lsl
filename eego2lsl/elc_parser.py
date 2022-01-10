import re
import os

def read_channels_positions(fname, return_desc=False):
	desc = read_elc(fname)

	if return_desc:
		return {
			c['ch_name']: c['pos'] 
			for c in desc['channels']
		}, desc
	else:
		return {
			c['ch_name']: c['pos'] 
			for c in desc['channels']
		}


def read_elc(fname):
	this_dir = os.path.realpath(os.path.dirname(__file__))
	extra_path = os.path.join(this_dir, 'extra')
	fname = os.path.join(extra_path, fname)

	keywords = [
		'NumberPositions', 
		'UnitPosition',
		'HSPTransformed',
	]

	descriptor = dict(channels=[])
	is_reading_position = False

	with open(fname, 'r') as f:
		for l in f.readlines():
			line = l.strip()
			if line[0] == '#':
				continue

			if is_reading_position: 
				pattern = re.compile(r"^\s*([A-Za-z0-9_\-]+)\s*:\s*(-?[0-9]+(?:.[0-9]+)?)\s+(-?[0-9]+(?:.[0-9]+)?)\s+(-?[0-9]+(?:.[0-9]+)?)")
				matches = re.findall(pattern, line)

				if len(matches) > 0 and len(matches[0]) == 4:
					ch_name, pos_x, pos_y, pos_z = matches[0]
					descriptor['channels'].append({
						'ch_name': ch_name, 'pos': (pos_x, pos_y, pos_z) 
					})

			else:
				found_kw = False
				for keyword in keywords:
					idx = line.find(keyword)

					if idx != -1:
						matches = re.findall(re.compile(keyword + r'[=\s]+' + '([A-Za-z0-9]+)'), line)
						if len(matches) == 1:
							descriptor[keyword] = matches[0]
						keywords.remove(keyword)
						found_kw = True 
						break
				if found_kw: 
					continue
				else: 
					matches = re.findall(re.compile(r'([Pp]ositions?)'), line)
					if len(matches) > 0:
						is_reading_position = True
	return descriptor