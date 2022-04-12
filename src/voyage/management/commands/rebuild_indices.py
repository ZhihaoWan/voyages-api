import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.models import Voyage
import time
import os

class Command(BaseCommand):
	help = 'rebuilds the options flatfiles'
	def handle(self, *args, **options):
		#this one will run off api calls -- likely df calls
		#the goal is to set up super fast access to items
		##based on pk autoincrement ids
		##to enable performant rendering of tailored views
		#like voyage_ids
		##to enable the voyage map animations
		#we'll use it to build either
		##"index" tables storing json blobs
		##flat files w line ids corresponding to the pk ids
		##redis caches or solr indices
		###(but solr may not be able to handle thousands of pk's as a search query? i've seen it break on queries like that before)
		#FIRST FIELD MUST BE THE PK ON THE TOP TABLE BEING INDEXED
		#AND THE INDEXED JSON DUMP FIELD NAME WILL ALWAYS BE 'json_dump'
		indices={
			'voyage_animations': {
				'vars':	[
					'id',
					'voyage_itinerary__imp_principal_port_slave_dis__longitude',
					'voyage_itinerary__imp_principal_port_slave_dis__latitude',
					'voyage_itinerary__imp_principal_port_slave_dis__place',
					'voyage_itinerary__imp_principal_place_of_slave_purchase__place',
					'voyage_itinerary__imp_principal_place_of_slave_purchase__longitude',
					'voyage_itinerary__imp_principal_place_of_slave_purchase__latitude',
					'voyage_ship__imputed_nationality__name',
					'voyage_ship__tonnage',
					'voyage_ship__ship_name',
					'voyage_slaves_numbers__imp_total_num_slaves_embarked'
					],
				'fname':'voyage/voyage_animations__index.json'
			}
		}
		
		url='http://127.0.0.1:8000/voyage/'
		from .app_secrets import headers
		
		batch_size=2000
		
		for ind in indices:
			st=time.time()
			vars=indices[ind]['vars']
			fname=indices[ind]['fname']
			pk_name=vars[0]
			
			page_num=1
			j={"ordered_keys":[v for v in vars],"entries":{}}
			data={
				'selected_fields':vars,
				'results_per_page':batch_size,
				'results_page':page_num,
				'hierarchical':False
			}
			
			while True:
				r=requests.post(url=url,headers=headers,data=data)
				items=json.loads(r.text)
				for item in items:
					pk=item[pk_name]
					j['entries'][pk]=[item[v] for v in vars]
				total_results_count=int(r.headers['total_results_count'])
				
				if page_num*batch_size>total_results_count:
					break
				else:
					page_num+=1
					data['results_page']=page_num
					print('fetched %d of %d entries in %d seconds' %(len(j['entries']),total_results_count,int(time.time()-st)))
			print("fetched %d fields on %d entries" %(len(vars),len(j['entries'])))
			
			d=open(fname,'w')
			d.write(json.dumps(j))
			d.close()
			elapsed_seconds=int(time.time()-st)
			print("...finished in %d minutes %d seconds" %(int(elapsed_seconds/60),elapsed_seconds%60))