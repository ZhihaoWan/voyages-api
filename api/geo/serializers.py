from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
			
class LocationTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=LocationType
		fields='__all__'

class PolygonSerializer(serializers.ModelSerializer):
	class Meta:
		model=Polygon
		fields='__all__'

class LocationParentSerializer(serializers.ModelSerializer):
	class Meta:
		model=Location
		fields='__all__'

class LocationChildSerializer(serializers.ModelSerializer):
	class Meta:
		model=Location
		fields='__all__'


class LocationSerializerDeep(serializers.ModelSerializer):
	parents=LocationParentSerializer(many=False)
	children=LocationChildSerializer(many=True)
# 	spatial_extent=PolygonSerializer(many=False)
# 	location_type=LocationTypeSerializer(many=False)
	class Meta:
		model=Location
		fields='__all__'

##REMOVING CHILD_OF AND PARENT_OF RECORDS FROM THE MAIN LOCATION SERIALIZER
##IT HUGELY REDUCES THE OVERHEAD HERE
@extend_schema_serializer(
	examples = [
         OpenApiExample(
            'Ex. 1: numeric range',
            summary='Filter on a numeric range for a nested variable',
            description='Here, we search for voyages whose imputed year of arrival at the principal port of disembarkation was between 1820 & 1850. We choose this variable as it is one of the most fully-populated numeric variables in the dataset.',
            value={
				'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year': [1820,1850]
			},
			request_only=True,
			response_only=False,
        ),
		OpenApiExample(
            'Ex. 2: array of str vals',
            summary='OR Filter on exact matches of known str values',
            description='Here, we search on str value fields for known exact matches to ANY of those values. Specifically, we are searching for voyages that are believed to have disembarked captives principally in Barbados or Cuba',
            value={
				'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name': ['Barbados','Cuba']
			},
			request_only=True,
			response_only=False,
        )
    ]
)
class LocationSerializer(serializers.ModelSerializer):
	spatial_extent=PolygonSerializer(many=False)
	location_type=LocationTypeSerializer(many=False)
	class Meta:
		model=Location
		fields='__all__'

class AdjacencySerializer(serializers.ModelSerializer):
	source=LocationSerializer(many=False)
	target=LocationSerializer(many=False)
	class Meta:
		model=Adjacency
		fields='__all__'