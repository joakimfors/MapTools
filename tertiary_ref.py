# -*- coding: utf-8 -*-
import sys
import requests
import re
from os import path
from OsmApi import OsmApi

if __name__ == "__main__":
	osmtoolsrc = open(path.expanduser("~/.osmtoolsrc"))
	username = False
	password = False
	for line in osmtoolsrc:
		key, val = line.split("=", 1)
		if key == 'username':
			username = val.strip()
		if key == 'password':
			password = val.strip()
	api = OsmApi.OsmApi(username=username, password=password, debug=True, dryrun=False)
	data = ''
	with open('tert_ways.osm', 'r') as f:
		data = f.read()

	objs = api.ParseOsm(data)
	ways = []
	rels = {}

	api.ChangesetCreate({u"comment": u"Add 'sekundära länsvägar' to route road relations", u"bot": u"yes", u"type": u"automated"})
	for obj in objs:
		print obj['type'], obj['data']['id'], obj['data']['tag']['ref']
		if obj['type'] == 'way':
			ways.append({'updated': False, 'obj': obj})
		if obj['type'] == 'relation':
			updated = False
			ref = obj['data']['tag']['ref']
			m = re.match('^([A-Z])\s*([0-9\.]+)', ref)
			if m:
				ref = m.group(1) + " " + m.group(2)
			else:
				print "Not a tertiary ref, skipping"
				continue
			if ref != obj['data']['tag']['ref']:
				print "Old:",obj['data']['tag']['ref'],"new: ", ref
				obj['data']['tag']['ref'] = ref
				updated = True
			if obj['data']['tag']['ref'] in rels:
				print "Multiple relations with ref", obj['data']['tag']['ref']
			rels[ref] = {'updated': updated, 'obj': obj}
	print rels

	for way in ways:
		refs = way['obj']['data']['tag']['ref'].split(';')
		i = 0
		for ref in refs:
			ref = ref.strip()
			m = re.match('^([A-Z])\s*([0-9\.]+)', ref)
			if m:
				ref = m.group(1) + " " + m.group(2)
				refs[i] = ref
				# Add to relation
				add = True
				if ref in rels:
					for member in rels[ref]['obj']['data']['member']:
						if member['ref'] == way['obj']['data']['id']:
							add = False
							break
				else:
					print 'Create relation with ref',ref
					rel = api.RelationCreate({
						u'tag': {
							u'type': u'route',
							u'route': u'road',
							u'ref': ref
						},
						u'member': []
					})
					rels[ref] = {'updated': True, 'obj': {'data': rel, 'type': 'relation'}}
					#print rels[ref]
				if add:
					print 'Add way',way['obj']['data']['id'],'with ref',ref,'to relation',rels[ref]['obj']['data']['tag']['ref']
					rels[ref]['obj']['data']['member'].append({
						u'role': u'',
						u'ref': way['obj']['data']['id'],
						u'type': way['obj']['type']
					})
					rels[ref]['updated'] = True

			i += 1
		ref = ';'.join(refs)
		if ref != way['obj']['data']['tag']['ref']:
			print "Old:",way['obj']['data']['tag']['ref'],"new: ", ref
			way['obj']['data']['tag']['ref'] = ref
			way['updated'] = True


	for way in ways:
		if way['updated']:
			api.WayUpdate(way['obj']['data'])

	for ref,rel in rels.items():
		if rel['updated']:
			api.RelationUpdate(rel['obj']['data'])

	api.ChangesetClose()

