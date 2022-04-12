from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
import urllib
import json
import requests
import time
from .models import *
import pprint
from tools.nest import *
from tools.reqs import *
from tools.timer import timer
import collections
import gc
from .serializers import *

pp = pprint.PrettyPrinter(indent=4)


voyage_options=options_handler('voyage/voyage_options.json',hierarchical=False)
geo_options=options_handler('voyage/geo_options.json',hierarchical=False)


#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class VoyageList(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('voyage/voyage_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("username:",request.auth.user)
		t=timer('FETCHING...',[])
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count=post_req(queryset,self,request,voyage_options)
		headers={"total_results_count":results_count}
		#read_serializer=VoyageSerializer(queryset,many=True,selected_fields=selected_fields)
		t=timer('building query',t)
		read_serializer=VoyageSerializer(queryset,many=True)
		t=timer('sql execution',t)
		serialized=read_serializer.data
		t=timer('serializing',t)

		#if the user hasn't selected any fields (default), then get the fully-qualified var names as the full list
		if selected_fields==[]:
			selected_fields=list(voyage_options.keys())
		outputs=[]
		
		hierarchical=request.POST.get('hierarchical')
		if str(hierarchical).lower() in ['false','0','f','n']:
			hierarchical=False
		else:
			hierarchical=True
		
		if hierarchical==False:
			for s in serialized:
				d={}
				for selected_field in selected_fields:
					#In this flattened view, the reverse relationship breaks the references to the outcome variables in the serializer
					#not badly -- you just get some repeat, nested data -- but that's unhelpful
					#The fix will be to make it a through table relationship
					keychain=selected_field.split('__')
					bottomval=bottomout(s,list(keychain))
					d[selected_field]=bottomval
				outputs.append(d)
		else:
			outputs=serialized
		t=timer('flattening',t,done=True)
		return JsonResponse(outputs,safe=False,headers=headers)

#VOYAGES SCATTER DATAFRAME ENDPOINT (experimental and going to be a resource hog!)
class VoyageAggregations(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		#print("username:",request.auth.user)
		params=request.GET
		aggregations=params.get('aggregate_fields')
		queryset=Voyage.objects.all()
		aggregation,selected_fields,results_count=post_req(queryset,self,request,voyage_options,retrieve_all=True)
		output_dict={}
		for a in aggregation:
			for k in a:
				v=a[k]
				fn=k.split('__')[-1]
				varname=k[:-len(fn)-2]
				if varname in output_dict:
					output_dict[varname][fn]=a[k]
				else:
					output_dict[varname]={fn:a[k]}
		return JsonResponse(output_dict,safe=False)

#VOYAGES SCATTER DATAFRAME ENDPOINT (experimental and going to be a resource hog!)
class VoyageDataFrames(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		t=timer("FETCHING...",[])
		params=request.POST
		retrieve_all=True
		if 'results_per_page' in params:
			retrieve_all=False
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count=post_req(queryset,self,request,voyage_options,auto_prefetch=False,retrieve_all=retrieve_all)
		headers={"total_results_count":results_count}
		sf=list(selected_fields)
		t=timer('building query',t)
		serialized=VoyageSerializer(queryset,many=True,selected_fields=selected_fields)
		t=timer('sql execution',t)
		serialized=serialized.data
		t=timer('serialization',t)
		output_dicts={}
		for selected_field in sf:
			keychain=selected_field.split('__')
			for s in serialized:
				bottomval=bottomout(s,list(keychain))
				if selected_field in output_dicts:
					output_dicts[selected_field].append(bottomval)
				else:
					output_dicts[selected_field]=[bottomval]
		t=timer('flattening',t,done=True)
		return JsonResponse(output_dicts,safe=False,headers=headers)

#We'll run this one as a two-step
##1. run the search and get only the voyage_ids but all the voyage_ids
##2. if that's sufficiently fast, then run those ids against a redis cache (or solr, actually -- just need a super fast flat record generator)
##2a. into which we'll bake a few different slices of the data -- the specific vars needed by some special view like the timelapse
##-->Flat files seem pretty fast (though a little more work needs to be done in terms of which vars are indexed)
### #basic dataframes call
### #11 fields, 5816 results-->2 seconds
### #11 fields, 63k results-->23.14067506790161 seconds
### #cached voyages call
### #11 fields, 5816 results-->0.3 seconds
### #11 fields, 63k results-->1.2 seconds

class VoyageAnimationCache(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		params=request.POST
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count=post_req(queryset,self,request,voyage_options,auto_prefetch=False,retrieve_all=True)		
		d=open('voyage/voyage_animations__index.json','r')
		j=json.loads(d.read())
		d.close()
		ids=[i[0] for i in queryset.values_list('id')]
		resp={i:j[str(i)] for i in ids}
		return JsonResponse(resp,safe=False)

#Get data on Places
#Default structure is places::region::broad_region
#By passing it the req param 'inverse=True', you'll get back broad_regions::regions::places
class VoyagePlaceList(generics.GenericAPIView):
	serializer_class=PlaceSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('voyage/geo_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		#print("username:",request.auth.user)
		t=timer("FETCHING...",[])
		queryset=Place.objects.all()
		queryset,selected_fields,results_count=post_req(queryset,self,request,geo_options,retrieve_all=True)
		t=timer('building query',t)
		read_serializer=PlaceSerializer(queryset,many=True)
		t=timer('sql execution',t)
		serialized=read_serializer.data
		t=timer('serialization',t)
		params=request.GET
		tree={}
		
		hierarchical=request.POST.get('hierarchical')
		if str(hierarchical).lower() in ['false','0','f','n']:
			hierarchical=False
		else:
			hierarchical=True
		
		if hierarchical:
			for place in serialized:
				broadregion_id=place['region']['broad_region']['id']
				region_id=place['region']['id']
				place_id=place['id']
				minimal_place_dict=dict(place)
				del(minimal_place_dict['region'])
				minimal_region_dict=dict(place['region'])
				del(minimal_region_dict['broad_region'])
				if broadregion_id not in tree:
					tree[broadregion_id]=place['region']['broad_region']
					tree[broadregion_id]['regions']={region_id:minimal_region_dict}
					tree[broadregion_id]['regions'][region_id]['places']={place_id:minimal_place_dict}
				else:
					if region_id not in tree[broadregion_id]['regions']:
						tree[broadregion_id]['regions'][region_id]=minimal_region_dict
						tree[broadregion_id]['regions'][region_id]['places']={place_id:minimal_place_dict}
					else:
						tree[broadregion_id]['regions'][region_id]['places'][place_id]=minimal_place_dict
			tree_list=[]
			for broadregion_id in tree:
				item=dict(tree[broadregion_id])
				item['regions']=[]
				for region_id in tree[broadregion_id]['regions']:
					region=dict(tree[broadregion_id]['regions'][region_id])
					places=[]
					for place_id in region['places']:
						places.append(region['places'][place_id])
					region['places']=places
					item['regions'].append(region)
				tree_list.append(item)						
			outputs=tree_list
		else:
			#if the user hasn't selected any fields (default), then get the fully-qualified var names as the full list
			if selected_fields==[]:
				selected_fields=list(geo_options.keys())
			outputs=[]
			for s in serialized:
				d={}
				for selected_field in selected_fields:
					#In this flattened view, the reverse relationship breaks the references to the outcome variables in the serializer
					#not badly -- you just get some repeat, nested data -- but that's unhelpful
					#The fix will be to make it a through table relationship
					keychain=selected_field.split('__')
					bottomval=bottomout(s,list(keychain))
					d[selected_field]=bottomval
				outputs.append(d)
			
		t=timer('flattening',t,True)
		return JsonResponse(outputs,safe=False)

#This will only accept one field at a time
#Should only be a text field
#And it will only return max 10 results
#It will therefore serve as an autocomplete endpoint
#I should make all text queries into 'or' queries
class VoyageTextFieldAutoComplete(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		#print("username:",request.auth.user)
		st=time.time()
		params=request.POST
		k=next(iter(params))
		v=params[k]
		retrieve_all=True
		queryset=Voyage.objects.all()		
		kwargs={'{0}__{1}'.format(k, 'icontains'):v}
		queryset=queryset.filter(**kwargs)
		queryset=queryset.prefetch_related(k)
		queryset=queryset.order_by(k)
		results_count=queryset.count()
		fetchcount=10
		vals=[]
		for v in queryset.values_list(k).iterator():
			if v not in vals:
				vals.append(v)
			if len(vals)>=fetchcount:
				break
		def flattenthis(l):
			fl=[]
			for i in l:
				if type(i)==tuple:
					for e in i:
						fl.append(e)
				else:
					fl.append(i)
			return fl
		val_list=flattenthis(l=vals)
		output_dict={
			k:val_list,
			"results_count":results_count
		}
		print("executed in",time.time()-st,"seconds")
		return JsonResponse(output_dict,safe=False)

class DuplicateVoyage(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	def get(self,request):
		params=request.GET
		try:
			voyage_id=int(params['voyage_id'])
		except:
			return JsonResponse({"message":"No voyage ID supplied"},safe=False)
		existing_voyages=Voyage.objects.all()
		kwargs={'voyage_id':voyage_id}
		v_queryset=existing_voyages.filter(**kwargs)
		if len(v_queryset)==0:
			return JsonResponse({"message":"Error: Voyage %d does not exist" %voyage_id})
		elif len(v_queryset)>1:
			return JsonResponse({"message":"Error: Multiple voyages with id %d -- check your database" %voyage_id})
		else:
			voyage_to_duplicate=v_queryset[0]
		max_voyage_id=existing_voyages.order_by('-voyage_id')[0].voyage_id
		new_voyage_id=max_voyage_id+1
		duplicated_voyage=voyage_to_duplicate
		duplicated_voyage.id=new_voyage_id
		duplicated_voyage.voyage_id=new_voyage_id
		duplicated_voyage.save()
		existing_voyages=Voyage.objects.all()
		kwargs={'voyage_id':new_voyage_id}
		new_voyage=existing_voyages.filter(**kwargs)
		output_dict=VoyageSerializer(duplicated_voyage,many=False).data
		return JsonResponse(output_dict,safe=False)