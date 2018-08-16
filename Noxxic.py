#!/usr/local/bin/python3

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json

def simple_get(url):
	"""
	Attempts to get the content at `url` by making an HTTP GET request.
	If the content-type of response is some kind of HTML/XML, return the
	text content, otherwise return None
	"""
	try:
		with closing(get(url, stream=True)) as resp:
			if is_good_response(resp):
				return resp.content
			else:
				return None
				
	except RequestException as e:
		log_error('Error during requests to {0} : {1}'.format(url, str(e)))
		return None
		
def is_good_response(resp):
	"""
	Returns true if the response seems to be HTML, false otherwise
	"""
	content_type = resp.headers['Content-Type'].lower()
	return (resp.status_code == 200
			and content_type is not None
			and content_type.find('html') > -1)

def log_error(e):
	"""
	It is always a good idea to log errors. 
	This function just prints them, but you can
	make it do anything.
	"""
	print(e)
	
def get_classes():
	"""
	list all the classes in Noxxic 
	Class name -> 1 blank line -> specs -> 2 blank lines
	"""
		
	url = 'http://www.noxxic.com/wow/'
	response = simple_get(url)
	class_specs = []
	
	if response is not None:
		html = BeautifulSoup(response, 'html.parser')
		class_menu = html.select('ul .dr')[0]
		if class_menu is not None:
			menu_text = class_menu.text.strip()
			in_submenu = False
			blank_counter = 0
			class_name = ''
			
			for entry in menu_text.split('\n'):
				next_entry = entry.strip()
				if next_entry == '':
					blank_counter += 1
					if blank_counter == 2:
						class_name = ''
						in_submenu = False
						blank_counter = 0
					elif class_name == '':
						in_submenu = False
					else:
						in_submenu = True
				elif in_submenu:
					new_spec = {'name': next_entry, 'priorities': []}
					class_specs[-1]['specs'].append(new_spec)
				else:
					class_name = next_entry
					class_specs.append({'classname': class_name})
					class_specs[-1]['specs'] = []
					blank_counter = 0
					
	return class_specs

def get_stats_noxxic(classname, spec):
	"""
	classname: convert to lower case, replace space with dash
	spec: convert to lower case, replace space with dash
	find the first bubble string to retrive suggested spec priority
	"""
	
	url_class = classname.lower().replace(' ', '-')	
	url_spec = spec.lower().replace(' ', '-')
	
	url = 'http://www.noxxic.com/wow/pve/%s/%s/stat-priority/' % (url_class, url_spec)
	response = simple_get(url)
	
	if response is not None:
		html = BeautifulSoup(response, 'html.parser')
		stats = html.select('.bubble-string')[0]
		if stats is not None:
			print(stats.text)
			stats_lines = stats.text.replace(' > ', '\n').split('\n')
			return stats_lines
	return []
	
def strip_talent(spec, talent):
	talent = talent.strip()
	if (talent == 'Guardian Of Elune' or talent == 'Elemental Blast'
		or talent == 'Galactic Guardian' or talent == 'Storm Elemental'):
			return talent
	if talent.startswith(spec + ' '):
		talent = talent.replace(spec + ' ', '')
	if talent.endswith(' ' + spec):
		talent = talent.replace(' ' + spec, '')
	return talent
	
def get_talents_noxxic(classname, spec):
	"""
	classname: convert to lower case, replace space with dash
	spec: convert to lower case, replace space with dash
	find the nxc-wow-main-build and then 
	find the selected entries in to to get the suggested talents
	"""

	url_class = classname.lower().replace(' ', '-')	
	url_spec = spec.lower().replace(' ', '-')
	
	url = 'http://www.noxxic.com/wow/pve/%s/%s/spec-builds-talents/' % (url_class, url_spec)
	response = simple_get(url)
	
	if response is not None:
		html = BeautifulSoup(response, 'html.parser')
		talents = html.select('.nxc-wow-main-build')[0]
		if talents is not None:
			selected_talents = [strip_talent(spec, t.string) for t  in talents.select('.selected')]
			print(selected_talents)
			return selected_talents
	return []

	
classes = get_classes()

for c in range(0, len(classes)):
	class_name = classes[c]['classname']
	for s in range(0, len(classes[c]['specs'])):
		spec = classes[c]['specs'][s]
		print(class_name, spec['name'])

		stats = get_stats_noxxic(class_name, spec['name'])
		talents = get_talents_noxxic(class_name, spec['name'])
		classes[c]['specs'][s]['priorities'] = stats
		classes[c]['specs'][s]['talents'] = talents
		
classes_json = json.dumps(classes, indent=2)
print(classes_json)

save_file = '/Users/sarah/Desktop/class_stats.json'
f = open(save_file, 'w')
f.write(classes_json)
f.close()

# Errors without trim:
#####################
# Havoc Soul Rending
# Balance Guardian Affinity
# Feral Balance Affinity
# Feral Soul Of The Forest
# Feral Moment Of Clarity
# Restoration Guardian Affinity
# Beast Mastery A Murder Of Crows
# Holy Divine Purpose
# Shadow Mindbender
# Enhancement Ascendance

# Guardian Affinity Balance
# Soul Of The Forest Guardian
# Balance Affinity Restoration
# Rushing Jade Wind Brewmaster
# Fist Of Justice Retribution
# Mindbender Shadow
# Totem Mastery Elemental


# Errors with trim:
###################
# Galactic Guardian
# Guardian Of Elune
# Elemental Blast
# Storm Elemental

