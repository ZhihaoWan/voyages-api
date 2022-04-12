import json
import pprint
import urllib
from django.db.models import Avg,Sum,Min,Max,Count,Q
from django.db.models.aggregates import StdDev
from .nest import *

#GENERIC FUNCTION TO RUN A CALL ON REST SERIALIZERS
##Default is to auto prefetch, but need to be able to turn it off.
##For instance, on our PAST graph-like data, the prefetch can overwhelm the system if you try to get everything
##can also just pass an array of prefetch vars


def post_req(queryset,s,r,options_dict,auto_prefetch=True,retrieve_all=False):
	
	params=dict(r.POST)
	pp = pprint.PrettyPrinter(indent=4)
	print("--post req params--")
	pp.pprint(params)
		
	#SELECT SPECIFIC FIELDS TO RETURN
	selected_fields=params.get('selected_fields')
	
	if selected_fields is None:
		selected_fields=[]
	
	#INCLUDE AGGREGATION FIELDS
	aggregations_param=params.get('aggregate_fields')
	
	if aggregations_param is not None:
		valid_aggregation_fields=[f for f in options_dict if 'Integer' in options_dict[f]['type'] or 'Decimal' in options_dict[f]['type']]
		aggregation_fields=[f for f in aggregations_param if f in valid_aggregation_fields]
		selected_fields=[]
		auto_prefetch=False
	else:
		aggregation_fields=[]
	
	all_fields={i:options_dict[i] for i in options_dict if 'type' in options_dict[i]}
	active_fields=list(set([i for i in params]+selected_fields+aggregation_fields).intersection(set(all_fields)))
	
	#ORDER RESULTS
	order_by=params.get('order_by')
	if order_by is not None:
		print('--order by--')
		print(order_by)
		queryset=queryset.order_by(*order_by)
	
	###FILTER RESULTS
	##select text and numeric fields, ignoring those without a type
	text_fields=[i for i in all_fields if 'CharField' in all_fields[i]['type']]
	numeric_fields=[i for i in all_fields if 'IntegerField' in all_fields[i]['type'] or 'DecimalField' in all_fields[i]['type'] or 'FloatField' in all_fields[i]['type']]
	boolean_fields=[i for i in all_fields if 'BooleanField' in all_fields[i]['type']]
	
	##build filters
	kwargs={}
	###numeric filters -- only accepting one range per field right now
	active_numeric_search_fields=[i for i in set(params).intersection(set(numeric_fields))]
	if len(active_numeric_search_fields)>0:
		for field in active_numeric_search_fields:
			range=params.get(field)[0]
			vals=[float(i) for i in range.split(',')]
			vals.sort()
			min,max=vals
			kwargs['{0}__{1}'.format(field, 'lte')]=max
			kwargs['{0}__{1}'.format(field, 'gte')]=min
	###text filters (exact match, and allow for multiple entries joined by an or)
	###this hard eval is not ideal but I can't quite see how else to do it just now?
	active_text_search_fields=[i for i in set(params).intersection(set(text_fields))]
	if len(active_text_search_fields)>0:
		for field in active_text_search_fields:
			vals=params.get(field)
			qobjstrs=["Q(%s='%s')" %(field,val) for val in vals]
			queryset=queryset.filter(eval('|'.join(qobjstrs)))
	##boolean filters -- only accepting one range per field right now
	active_boolean_search_fields=[i for i in set(params).intersection(set(boolean_fields))]
	if len(active_boolean_search_fields)>0:
		for field in active_boolean_search_fields:
			searchstring=params.get(field)
			if searchstring.lower() in ["true","t","1","yes"]:
				searchstring=True
			elif searchstring.lower() in ["false","f","0","no"]:
				searchstring=False
			
			if searchstring in [True,False]:
				kwargs[field]=searchstring
	
	###apply filters
	queryset=queryset.filter(**kwargs)
	results_count=queryset.count()
	print('--counts--')
	print("resultset size:",results_count)
	
	#PREFETCH REQUISITE FIELDS
	if auto_prefetch:
		prefetch_keys=list(options_dict.keys())
	else:
		prefetch_keys = active_fields
	
	#print(prefetch_keys)
	##ideally, I'd run this list against the model and see
	##which were m2m relationships (prefetch_related) and which were 1to1 (select_related)
	prefetch_vars=list(set(['__'.join(i.split('__')[:-1]) for i in prefetch_keys if '__' in i]))
	for p in prefetch_vars:
		queryset=queryset.prefetch_related(p)
	print('--prefetching %d vars--' %len(prefetch_vars))
	#print(prefetch_vars)
	
	#AGGREGATIONS
	##e.g. voyage_slaves_numbers__imp_total_num_slaves_embarked__sum
	aggregations_param=params.get('aggregate_fields')
	
	if aggregation_fields != []:
		aggqueryset=[]
		selected_fields=[]
		for aggfield in aggregation_fields:
			for aggsuffix in ["sum","avg","min","max","count","stddev"]:
				selected_fields.append(aggfield+"_"+aggsuffix)
			aggqueryset.append(queryset.aggregate(Sum(aggfield)))
			aggqueryset.append(queryset.aggregate(Avg(aggfield)))
			aggqueryset.append(queryset.aggregate(Min(aggfield)))
			aggqueryset.append(queryset.aggregate(Max(aggfield)))
			aggqueryset.append(queryset.aggregate(Max(aggfield)))
			aggqueryset.append(queryset.aggregate(StdDev(aggfield)))
		queryset=aggqueryset
	
	def val_or_default(params,key,default):
		val=params.get(key)
		if val is None:
			val=default
		else:
			val=int(val[0])
		return val
	
	#PAGINATION/LIMITS
	if retrieve_all==False:
		results_per_page=val_or_default(params,'results_per_page',10)
		results_page=val_or_default(params,'results_page',1)
		
		start_idx=(results_page-1)*results_per_page
		end_idx=(results_page)*results_per_page
		
		if end_idx-1>=results_count:
			end_idx=results_count-1
		
		if start_idx-1>=results_count:
			queryset=None
		else:
			queryset=queryset[start_idx:end_idx]
	
	return queryset,selected_fields,results_count

def options_handler(flatfilepath,request=None,hierarchical=True):
	if request is not None:
		if 'hierarchical' in request.query_params:
			if request.query_params['hierarchical'].lower() in ['false','0','n']:
				hierarchical=False
	d=open(flatfilepath,'r')
	t=d.read()
	j=json.loads(t)
	d.close()
	if hierarchical:
		j=nest_django_dict(j)
	return j