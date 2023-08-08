from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
from collections import Counter
import urllib
import json
import requests
import time
import collections
import gc
from voyages3.localsettings import *
import re
import pysolr
from voyage.models import Voyage
from past.models import *
import uuid

#this isn't pretty
#but i'm having trouble finding a more elegant way of exporting this data to an external service
#without installing networkx on this django instance, which i don't want to do!
class PastGraphMaker(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		#VOYAGE DICT
		voys=Voyage.objects.all()
		voys.prefetch_related(
			'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location',
			'voyage_itinerary__imp_principal_port_slave_dis__geo_location'
		)
		voys.select_related(
			'voyage_ship',
			'voyage_dates__imp_arrival_at_port_of_dis_sparsedate'
		)
		voy_vals=voys.values_list(
			'id',
			'voyage_ship__ship_name',
			'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year',
			'voyage_itinerary__imp_principal_port_slave_dis__geo_location__name',
			'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name'
		)
		
		valkeys=[
			'id',
			'voyage_ship__ship_name',
			'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year',
			'voyage_itinerary__imp_principal_port_slave_dis__geo_location__name',
			'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name'
		]
		
		voy_df={
			k:[
				voy_vals[i][valkeys.index(k)] for i in range(len(voy_vals))
			]
			for k in valkeys
		}
				
		#ENSLAVER DICT
		enslaver_aliases=EnslaverAlias.objects.all()
		enslaver_alias_map={str(uuid.uuid4()):v[0] for v in voy_vals}
		enslaver_aliases_vals=enslaver_aliases.values_list(
			'id',
			'alias',
			'identity'
		)
		
		valkeys=(
			'id',
			'alias',
			'identity'
		)
		
		enslaver_aliases_df={
			k:[
				enslaver_aliases_vals[i][valkeys.index(k)] for i in range(len(enslaver_aliases_vals))
			]
			for k in valkeys
		}
		
		#ENSLAVED PEOPLE DICT
		enslaved_people=Enslaved.objects.all()
		enslaved_people_vals=enslaved_people.values_list(
			'id',
			'documented_name',
			'age',
			'gender'
		)
		
		valkeys=(
			'id',
			'documented_name',
			'age',
			'gender'
		)
		
		enslaved_people_df={
			k:[
				enslaved_people_vals[i][valkeys.index(k)] for i in range(len(enslaved_people_vals))
			]
			for k in valkeys
		}
		
		#ENSLAVEMENT RELATION DICT
		enslavementrelations=EnslavementRelation.objects.all()
		enslavementrelations=enslavementrelations.select_related('relation_type')
		enslavementrelation_vals=enslavementrelations.values_list(
			'id',
			'relation_type__name',
			'voyage'
		)
		valkeys=(
			'id',
			'relation_type__name',
			'voyage'
		)
		
		enslavementrelation_df={
			k:[
				enslavementrelation_vals[i][valkeys.index(k)] for i in range(len(enslavementrelation_vals))
			]
			for k in valkeys
		}
		
		#ENSLAVED IN RELATION
		enslaved_in_relation=EnslavedInRelation.objects.all()
		enslaved_in_relation_vals=enslaved_in_relation.values_list(
			'relation',
			'enslaved'
		)
		valkeys=(
			'relation',
			'enslaved'
		)
		
		enslaved_in_relation_df={
			k:[
				enslaved_in_relation_vals[i][valkeys.index(k)] for i in range(len(enslaved_in_relation_vals))
			]
			for k in valkeys
		}
		
		#ENSLAVER IN RELATION
		enslaver_in_relation=EnslaverInRelation.objects.all()
		enslaver_in_relation=enslaver_in_relation.select_related('role')
		enslaver_in_relation_vals=enslaver_in_relation.values_list(
			'relation',
			'enslaver_alias',
			'role__name'
		)
		valkeys=(
			'relation',
			'enslaver_alias',
			'role__name'
		)
		
		enslaver_in_relation_df={
			k:[
				enslaver_in_relation_vals[i][valkeys.index(k)] for i in range(len(enslaver_in_relation_vals))
			]
			for k in valkeys
		}
		
		relation_map={
			'enslaved':enslaved_people_df,
			'enslavers':enslaver_aliases_df,
			'voyages':voy_df,
			'enslavement_relations':enslavementrelation_df,
			'enslaved_in_relation':enslaved_in_relation_df,
			'enslavers_in_relation':enslaver_in_relation_df	
		}
		print("elapsed time:",time.time()-st)
		return JsonResponse(relation_map,safe=False)


class GlobalSearch(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("Global Search+++++++\nusername:",request.auth.user)
		
		params=dict(request.POST)
		search_string=params.get('search_string')
		# Oh, yes. Little Bobby Tables, we call him.
		search_string=re.sub("\s+"," ",search_string[0])
		search_string=search_string.strip()
		searchstringcomponents=[''.join(filter(str.isalnum,s)) for s in search_string.split(' ')]
		
		core_names= [
			'voyages',
			'enslaved',
			'enslavers',
			'blog'
		]
		
		output_dict=[]
		
		for core_name in core_names:
		
			solr = pysolr.Solr(
					'http://voyages-solr:8983/solr/%s/' %core_name,
					always_commit=True,
					timeout=10
				)
			finalsearchstring="(%s)" %(" ").join(searchstringcomponents)
			results=solr.search('text:%s' %finalsearchstring)
			results_count=results.hits
			ids=[r['id'] for r in results]
			output_dict.append({
				'type':core_name,
				'results_count':results_count,
				'ids':ids
			})

		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return JsonResponse(output_dict,safe=False)
			