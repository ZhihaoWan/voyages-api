from django.shortcuts import render
from django.db.models import Q,Prefetch
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
import urllib
import json
import requests
import time
from .models import *
from .serializers import *
import pprint
from tools.nest import *
from tools.reqs import *
import collections

enslaved_options=options_handler('past/enslaved_options.json',hierarchical=False)
enslaver_options=options_handler('past/enslaver_options.json',hierarchical=False)

class SingleEnslaved(generics.GenericAPIView):
	def get(self,request,enslaved_id):
		enslaved_record=Enslaved.objects.get(pk=enslaved_id)
		serialized=EnslavedSerializer(enslaved_record,many=False).data
		return JsonResponse(serialized,safe=False)

class SingleEnslavedVar(TemplateView):
	template_name='singlevar.html'
	def get(self,request,enslaved_id,varname):
		enslaved_record=Enslaved.objects.get(pk=enslaved_id)
		serialized=EnslavedSerializer(enslaved_record,many=False).data
		keychain=varname.split('__')
		bottomval=bottomout(serialized,list(keychain))
		var_options=enslaved_options[varname]
		data={
			'enslaved_id':enslaved_id,
			'variable_api_name':varname,
			'variable_label':var_options['flatlabel'],
			'variable_type':var_options['type'],
			'variable_value':bottomval
		}
		context = super(SingleEnslavedVar, self).get_context_data()
		context['data']=data
		return context

#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class EnslavedList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=EnslavedSerializer
	def options(self,request):
		j=options_handler('past/enslaved_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		st=time.time()
		times=[]
		labels=[]
		print("+++++++\nusername:",request.auth.user)
		print("FETCHING...")
		queryset=Enslaved.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaved_options,auto_prefetch=True)
		if len(error_messages)==0:
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			read_serializer=EnslavedSerializer(queryset,many=True)
			serialized=read_serializer.data
			
			outputs=[]
		
			hierarchical=request.POST.get('hierarchical')
			if str(hierarchical).lower() in ['false','0','f','n']:
				hierarchical=False
			else:
				hierarchical=True
		
			if hierarchical==False:
				if selected_fields==[]:
					selected_fields=[i for i in enslaved_options]
			
				for s in serialized:
					d={}
					for selected_field in selected_fields:
						keychain=selected_field.split('__')
						bottomval=bottomout(s,list(keychain))
						d[selected_field]=bottomval
					outputs.append(d)
			else:
				outputs=serialized
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(outputs,safe=False,headers=headers)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=500)

#This will only accept one field at a time
#Should only be a text field
#And it will only return max 10 results
#It will therefore serve as an autocomplete endpoint
#I should make all text queries into 'or' queries
class EnslavedTextFieldAutoComplete(generics.GenericAPIView):
	serializer_class=EnslavedSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("+++++++\nusername:",request.auth.user)
		try:
			st=time.time()
			params=dict(request.POST)
			k=next(iter(params))
			v=params[k][0]
			retrieve_all=True
			queryset=Enslaved.objects.all()		
			kwargs={'{0}__{1}'.format(k, 'icontains'):v}
			queryset=queryset.filter(**kwargs)
			queryset=queryset.prefetch_related(k)
			queryset=queryset.order_by(k)
			results_count=queryset.count()
			fetchcount=20
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
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dict,safe=False)
		except:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':'bad autocomplete request'}, status=400)

class EnslaverTextFieldAutoComplete(generics.GenericAPIView):
	serializer_class=EnslaverSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("+++++++\nusername:",request.auth.user)
		try:
			st=time.time()
			params=dict(request.POST)
			k=next(iter(params))
			v=params[k][0]
			retrieve_all=True
			queryset=EnslaverIdentity.objects.all()		
			kwargs={'{0}__{1}'.format(k, 'icontains'):v}
			queryset=queryset.filter(**kwargs)
			queryset=queryset.prefetch_related(k)
			queryset=queryset.order_by(k)
			results_count=queryset.count()
			fetchcount=20
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
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dict,safe=False)
		except:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':'bad autocomplete request'}, status=400)



#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class EnslaverList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=EnslaverSerializer
	def options(self,request):
		j=options_handler('past/enslaver_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("+++++++\nusername:",request.auth.user)
		print("FETCHING...")
		st=time.time()
		queryset=EnslaverIdentity.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaver_options,auto_prefetch=True)
		if len(error_messages)==0:
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			read_serializer=EnslaverSerializer(queryset,many=True)
			serialized=read_serializer.data
			
			outputs=[]
		
			hierarchical=request.POST.get('hierarchical')
			if str(hierarchical).lower() in ['false','0','f','n']:
				hierarchical=False
			else:
				hierarchical=True
		
			if hierarchical==False:
				if selected_fields==[]:
					selected_fields=[i for i in enslaver_options]
			
				for s in serialized:
					d={}
					for selected_field in selected_fields:
						keychain=selected_field.split('__')
						bottomval=bottomout(s,list(keychain))
						d[selected_field]=bottomval
					outputs.append(d)
			else:
				outputs=serialized
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(outputs,safe=False,headers=headers)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=500)


# Basic statistics
## takes a numeric variable
## returns its sum, average, max, min, and stdv
class EnslavedAggregations(generics.GenericAPIView):
	serializer_class=EnslavedSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("+++++++\nusername:",request.auth.user)
		params=dict(request.POST)
		aggregations=params.get('aggregate_fields')
		print("aggregations:",aggregations)
		queryset=Enslaved.objects.all()
		
		aggregation,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaved_options,retrieve_all=True)
		output_dict={}
		if len(error_messages)==0 and type(aggregation)==list:
			for a in aggregation:
				for k in a:
					v=a[k]
					fn=k.split('__')[-1]
					varname=k[:-len(fn)-2]
					if varname in output_dict:
						output_dict[varname][fn]=a[k]
					else:
						output_dict[varname]={fn:a[k]}
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dict,safe=False)
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

#DATAFRAME ENDPOINT (experimental & a resource hog!)
class EnslavedDataFrames(generics.GenericAPIView):
	serializer_class=EnslavedSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('past/enslaved_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("+++++++\nusername:",request.auth.user)
		st=time.time()
		params=dict(request.POST)
		retrieve_all=True
		if 'results_per_page' in params:
			retrieve_all=False
		queryset=Enslaved.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaved_options,auto_prefetch=False,retrieve_all=retrieve_all,selected_fields_exception=True)
		if len(error_messages)==0:
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			if selected_fields==[]:
				sf=list(enslaved_options.keys())
			else:
				sf=[i for i in selected_fields if i in list(enslaved_options.keys())]
			
			serialized=EnslavedSerializer(queryset,many=True,selected_fields=selected_fields)
			
			serialized=serialized.data
			output_dicts={}
			for selected_field in sf:
				keychain=selected_field.split('__')
				for s in serialized:
					bottomval=bottomout(s,list(keychain))
					if selected_field in output_dicts:
						output_dicts[selected_field].append(bottomval)
					else:
						output_dicts[selected_field]=[bottomval]
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dicts,safe=False,headers=headers)
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)


class EnslavedAggRoutes(generics.GenericAPIView):
	'''
	Given
	1. a source field and a target field in the "groupby_fields"
	2. This will return the count of people who went from A to B
	3. In either a geojson or geosankey format, as requested
	'''
	serializer_class=EnslavedSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		try:
			st=time.time()
			print("+++++++\nusername:",request.auth.user)
			params=dict(request.POST)
			groupby_fields=params.get('groupby_fields')
			
			queryset=Enslaved.objects.all()
			queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaved_options,auto_prefetch=False,retrieve_all=retrieve_all,selected_fields_exception=True)
			ids=[i[0] for i in queryset.values_list('id')]

			u2=FLASK_BASE_URL+'crosstabs/'
			d2=params
			d2['ids']=ids
			r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
			j=json.loads(r.text)

			abpairs={int(float(k)):{int(float(v)):j[k][v] for v in j[k]} for k in j}
			dataset=int(params['dataset'][0])
			##third argument: output_format -- can be either
			####"geojson", which returns just a big featurecollection or
			####"geosankey", which returns a featurecollection of points only, alongside an edges dump as "links.csv" -- following the specifications here: https://github.com/geodesign/spatialsankey
			output_format=params['output_format'][0]
			routes=Route.objects.all()
			routes.prefetch_related('source')
			routes.prefetch_related('target')
			adjacencies=Adjacency.objects.all()
			adjacencies.prefetch_related('source')
			adjacencies.prefetch_related('target')
	
			adjacency_weights={}
	
			for s_id in abpairs:
				for t_id in abpairs[s_id]:
					source_id=min(s_id,t_id)
					target_id=max(s_id,t_id)
					w=abpairs[s_id][t_id]
					route=json.loads(routes.filter(**{'source__id':source_id,'target__id':target_id})[0].shortest_route)
					for a_id in route:
						if a_id in adjacency_weights:
							adjacency_weights[a_id]+=w
						else:
							adjacency_weights[a_id]=w
	
			adjacency_ids=[k for k in adjacency_weights.keys()]
	
			network_adjacencies=adjacencies.filter(pk__in=adjacency_ids)
	
			nodes={}
			edges={}
			for a in network_adjacencies:
				nodes[a.source.id]=[float(a.source.longitude),float(a.source.latitude),a.source.name]
				nodes[a.target.id]=[float(a.target.longitude),float(a.target.latitude),a.source.name]
				edges[a.id]={'nodes':[a.source.id,a.target.id],'weight':adjacency_weights[a.id]}
	
			geojson={"type": "FeatureCollection", "features": []}
	
			for node_id in nodes:
				longitude,latitude,name=nodes[node_id]
	
				geojsonfeature={
					"type": "Feature",
					"id":node_id,
					"geometry": {"type":"Point","coordinates": [longitude,latitude]},
					"properties":{"name":name}
				}
		
				geojson['features'].append(geojsonfeature)
	
			if output_format=="geojson":
		
				for e_id in edges:
					source_id,target_id=edges[e_id]['nodes']
					sv_longlat=nodes[source_id][0:2]
					tv_longlat=nodes[target_id][0:2]
					w=edges[e_id]['weight']
					geojsonfeature={
						"type":"Feature",
						"id":e_id,
						"geometry":{
							"type":"LineString",
							"coordinates":[sv_longlat,tv_longlat]
						},
						"properties":{"weight":w}
					}
					geojson['features'].append(geojsonfeature)
				output=geojson
			elif output_format=="geosankey":
				#print("GEOSANKEY")
				output_edges=[]
				for e_id in edges:
					source_id,target_id=edges[e_id]['nodes']
					w=edges[e_id]['weight']
					output_edges.append([source_id,target_id,w])
				output={'links':output_edges,'nodes':geojson}
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output,safe=False)
		except:
			return JsonResponse({'status':'false','message':'bad geo_route request'}, status=400)



# Basic statistics
## takes a numeric variable
## returns its sum, average, max, min, and stdv
class EnslaverAggregations(generics.GenericAPIView):
	serializer_class=EnslaverSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("+++++++\nusername:",request.auth.user)
		params=dict(request.POST)
		aggregations=params.get('aggregate_fields')
		print("aggregations:",aggregations)
		queryset=EnslaverIdentity.objects.all()
		
		aggregation,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,enslaver_options,retrieve_all=True)
		output_dict={}
		if len(error_messages)==0 and type(aggregation)==list:
			for a in aggregation:
				for k in a:
					v=a[k]
					fn=k.split('__')[-1]
					varname=k[:-len(fn)-2]
					if varname in output_dict:
						output_dict[varname][fn]=a[k]
					else:
						output_dict[varname]={fn:a[k]}
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dict,safe=False)
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)