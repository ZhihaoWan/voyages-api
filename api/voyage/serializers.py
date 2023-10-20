from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from document.models import Source,SourcePage,SourcePageConnection,SourceVoyageConnection
from geo.models import Location
from common.models import SparseDate
from past.models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

#### GEO

class VoyageLocationSerializer(serializers.ModelSerializer):
	class Meta:
		model=Location
		fields='__all__'

##### VESSEL VARIABLES ##### 

class RigOfVesselSerializer(serializers.ModelSerializer):
	class Meta:
		model=RigOfVessel
		fields='__all__'

class NationalitySerializer(serializers.ModelSerializer):
	class Meta:
		model=Nationality
		fields='__all__'

class TonTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=TonType
		fields='__all__'

class VoyageShipSerializer(serializers.ModelSerializer):
	rig_of_vessel=RigOfVesselSerializer(many=False)
	imputed_nationality=NationalitySerializer(many=False)
	ton_type=TonTypeSerializer(many=False)
	vessel_construction_place=VoyageLocationSerializer(many=False)
	vessel_construction_region=VoyageLocationSerializer(many=False)
	registered_place=VoyageLocationSerializer(many=False)
	registered_region=VoyageLocationSerializer(many=False)
	
	class Meta:
		model=VoyageShip
		fields='__all__'

##### ENSLAVED NUMBERS ##### 

class VoyageSlavesNumbersSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageSlavesNumbers
		fields='__all__'

##### CREW NUMBERS ##### 

class VoyageCrewSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageCrew
		fields='__all__'

##### ITINERARY #####

class VoyageItinerarySerializer(serializers.ModelSerializer):
	port_of_departure=VoyageLocationSerializer(many=False)
	int_first_port_emb=VoyageLocationSerializer(many=False)
	int_second_port_emb=VoyageLocationSerializer(many=False)
	int_first_region_purchase_slaves=VoyageLocationSerializer(many=False)
	int_second_region_purchase_slaves=VoyageLocationSerializer(many=False)
	int_first_port_dis=VoyageLocationSerializer(many=False)
	int_second_port_dis=VoyageLocationSerializer(many=False)
	int_first_region_slave_landing=VoyageLocationSerializer(many=False)
	imp_principal_region_slave_dis=VoyageLocationSerializer(many=False)
	int_second_place_region_slave_landing=VoyageLocationSerializer(many=False)
	first_place_slave_purchase=VoyageLocationSerializer(many=False)
	second_place_slave_purchase=VoyageLocationSerializer(many=False)
	third_place_slave_purchase=VoyageLocationSerializer(many=False)
	first_region_slave_emb=VoyageLocationSerializer(many=False)
	second_region_slave_emb=VoyageLocationSerializer(many=False)
	third_region_slave_emb=VoyageLocationSerializer(many=False)
	port_of_call_before_atl_crossing=VoyageLocationSerializer(many=False)
	first_landing_place=VoyageLocationSerializer(many=False)
	second_landing_place=VoyageLocationSerializer(many=False)
	third_landing_place=VoyageLocationSerializer(many=False)
	first_landing_region=VoyageLocationSerializer(many=False)
	second_landing_region=VoyageLocationSerializer(many=False)
	third_landing_region=VoyageLocationSerializer(many=False)
	place_voyage_ended=VoyageLocationSerializer(many=False)
	region_of_return=VoyageLocationSerializer(many=False)
	broad_region_of_return=VoyageLocationSerializer(many=False)
	imp_port_voyage_begin=VoyageLocationSerializer(many=False)
	imp_region_voyage_begin=VoyageLocationSerializer(many=False)
	imp_broad_region_voyage_begin=VoyageLocationSerializer(many=False)
	principal_place_of_slave_purchase=VoyageLocationSerializer(many=False)
	imp_principal_place_of_slave_purchase=VoyageLocationSerializer(many=False)
	imp_principal_region_of_slave_purchase=VoyageLocationSerializer(many=False)
	imp_broad_region_of_slave_purchase=VoyageLocationSerializer(many=False)
	principal_port_of_slave_dis=VoyageLocationSerializer(many=False)
	imp_principal_port_slave_dis=VoyageLocationSerializer(many=False)
	imp_broad_region_slave_dis=VoyageLocationSerializer(many=False)
	class Meta:
		model=VoyageItinerary
		fields='__all__'

##### OUTCOMES #####

class ParticularOutcomeSerializer(serializers.ModelSerializer):
	class Meta:
		model=ParticularOutcome
		fields='__all__'

class SlavesOutcomeSerializer(serializers.ModelSerializer):
	class Meta:
		model=SlavesOutcome
		fields='__all__'
		
class ResistanceSerializer(serializers.ModelSerializer):
	class Meta:
		model=Resistance
		fields='__all__'

class OwnerOutcomeSerializer(serializers.ModelSerializer):
	class Meta:
		model=OwnerOutcome
		fields='__all__'

class VesselCapturedOutcomeSerializer(serializers.ModelSerializer):
	class Meta:
		model=VesselCapturedOutcome
		fields='__all__'
		
class VoyageOutcomeSerializer(serializers.ModelSerializer):
	outcome_owner=OwnerOutcomeSerializer(many=False)
	outcome_slaves=SlavesOutcomeSerializer(many=False)
	particular_outcome=ParticularOutcomeSerializer(many=False)
	resistance=ResistanceSerializer(many=False)
	vessel_captured_outcome=VesselCapturedOutcomeSerializer(many=False)
	class Meta:
		model=VoyageOutcome
		fields='__all__'

##### DATES #####

class VoyageSparseDateSerializer(serializers.ModelSerializer):
	class Meta:
		model=SparseDate
		exclude=['id',]

class VoyageDatesSerializer(serializers.ModelSerializer):
	voyage_began_sparsedate=VoyageSparseDateSerializer(many=False)
	slave_purchase_began_sparsedate=VoyageSparseDateSerializer(many=False)
	vessel_left_port_sparsedate=VoyageSparseDateSerializer(many=False)
	first_dis_of_slaves_sparsedate=VoyageSparseDateSerializer(many=False)
	date_departed_africa_sparsedate=VoyageSparseDateSerializer(many=False)
	arrival_at_second_place_landing_sparsedate=VoyageSparseDateSerializer(many=False)
	third_dis_of_slaves_sparsedate=VoyageSparseDateSerializer(many=False)
	departure_last_place_of_landing_sparsedate=VoyageSparseDateSerializer(many=False)
	voyage_completed_sparsedate=VoyageSparseDateSerializer(many=False)
	imp_voyage_began_sparsedate=VoyageSparseDateSerializer(many=False)
	imp_departed_africa_sparsedate=VoyageSparseDateSerializer(many=False)
	imp_arrival_at_port_of_dis_sparsedate=VoyageSparseDateSerializer(many=False)
	class Meta:
		model=VoyageDates
		fields='__all__'

class VoyageSourcePageSerializer(serializers.ModelSerializer):
	class Meta:
		model=SourcePage
		fields='__all__'

class VoyageSourcePageConnectionSerializer(serializers.ModelSerializer):
	source_page=VoyageSourcePageSerializer(many=False)
	class Meta:
		model=SourcePageConnection
		fields='__all__'

class VoyageSourceSerializer(serializers.ModelSerializer):
	page_connection=VoyageSourcePageConnectionSerializer(many=True)
	class Meta:
		model=Source
		fields='__all__'

class VoyageSourceVoyageConnectionSerializer(serializers.ModelSerializer):
	source=VoyageSourceSerializer(many=False)
	class Meta:
		model=SourceVoyageConnection
		fields='__all__'

class VoyageEnslaverRoleSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverRole
		fields='__all__'

class VoyageEnslaverIdentitySerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class VoyageEnslaverAliasSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverAlias
		fields='__all__'

class VoyageEnslaverInRelationSerializer(serializers.ModelSerializer):
	enslaver_roles=VoyageEnslaverRoleSerializer(many=True)
	enslaver_alias=VoyageEnslaverAliasSerializer(many=False)
	class Meta:
		model=EnslaverRole
		fields='__all__'

class VoyageEnslavedSerializer(serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields=['id','documented_name']

class VoyageEnslavementRelationTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslavementRelationType
		feilds='__all__'

class VoyageEnslavementRelationsSerializer(serializers.ModelSerializer):
	relation_enslaved=VoyageEnslavedSerializer(many=True)
	relation_enslavers=VoyageEnslaverInRelationSerializer(many=True)
	relation_type=VoyageEnslavementRelationTypeSerializer(many=False)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

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
class VoyageSerializer(serializers.ModelSerializer):
	voyage_source_connections=VoyageSourceVoyageConnectionSerializer(many=True)
	voyage_itinerary=VoyageItinerarySerializer(many=False)
	voyage_dates=VoyageDatesSerializer(many=False)
	voyage_enslavement_relations=VoyageEnslavementRelationsSerializer(many=True)
	voyage_crew=VoyageCrewSerializer(many=False)
	voyage_ship=VoyageShipSerializer(many=False)
	voyage_slaves_numbers=VoyageSlavesNumbersSerializer(many=False)
	voyage_outcome=VoyageOutcomeSerializer(many=False)
	class Meta:
		model=Voyage
		exclude=['voyage_sources']
