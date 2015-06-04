try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import json
import random
import csv
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as helpers

from ckanext.lire.controllers.pan import (
    PANController,
)
from ckanext.lire.controllers.relin import (
    RELINController,
)
from ckanext.lire.controllers.functions import (
    FUNCTIONSController,
)

from pylons import config

import ckan.plugins as p
from ckan.lib.base import BaseController, response, request


c = p.toolkit.c
render = p.toolkit.render

class LIREController(BaseController):

    #index function for display form to load datasets for managing their relations
    def index(self):
        return render('lire/index.html')

    #main extension function
    def relationships(self):
      
      #load controller for processing datasets by tag, group, organization, random number of datasets and all datasets
      pan = PANController()
      #load controller for preparing datasets for visual display
      relin = RELINController()
      #load controller for using functions to process datasets
      func = FUNCTIONSController()

      #create temporary list for storing results of processing of datasets
      tempDatasets = []
      
      #IF conditions for storing HTML fields values sent by HTTP from index page
      if ('form[random]' not in request.params):
        randomNum = 0
      elif request.params['form[random]'] == '':
        randomNum = 0 
      else:
        randomNum = int(request.params['form[random]'])

      if ('form[tag]' not in request.params):
        tag = ''
      else:
        tag = request.params['form[tag]']
      
      if ('form[group]' not in request.params):
        group = ''
      else:
        group = request.params['form[group]']

      if ('form[organization]' not in request.params):
        organization = ''      
      else:
        organization = request.params['form[organization]']

      #examining which field on start HTML user choosed and processing datasets by that condition
      if (randomNum > 0):
        tempDatasets = toolkit.get_action('package_list')(
                data_dict={})
        datasets = random.sample( tempDatasets, randomNum ) 
        pan_rezultati = pan.process_datasets(datasets)
      elif (tag != ''):
        tempTags = toolkit.get_action('tag_show')(
                data_dict={'id': tag}) 
        for tempList in tempTags['packages']:
          for tempKey,tempValue in tempList.items():
            if 'name' in tempKey:
              tempDatasets.append(tempValue)
        pan_rezultati = pan.process_datasets(tempDatasets)
      elif (group != ''):
        tempGroup = toolkit.get_action('group_show')(
                data_dict={'id': group})
        for tempList in tempGroup['packages']:
          for tempKey,tempValue in tempList.items():
            if 'name' in tempKey:
              tempDatasets.append(tempValue)
        pan_rezultati = pan.process_datasets(tempDatasets)
      elif (organization != ''):
        tempOrganization = toolkit.get_action('organization_show')(
                data_dict={'id': organization})
        for tempList in tempOrganization['packages']:
          for tempKey,tempValue in tempList.items():
            if 'name' in tempKey:
              tempDatasets.append(tempValue)
        pan_rezultati = pan.process_datasets(tempDatasets)
      else:
        tempDatasets = toolkit.get_action('package_list')(
                data_dict={})
        pan_rezultati = pan.process_datasets(tempDatasets) 

      #get names of datasets who have relations
      relationships = pan_rezultati['relationships']
      #get datasets with relations
      dR = pan_rezultati['dR']
      #get data about datasets that will be displayed
      datasets = pan_rezultati['datasets'] 
      
      #get all relations for each dataset
      eKey = relin.oneToAllRelationships(relationships,datasets)

      #filter commutative relations 
      eKey = relin.removeCommutative(eKey) 

      #get all datasets from portal 
      datasetsPortal = toolkit.get_action('package_list')(
            data_dict={})

      #replace datasets name with their keys from datasetsPortal dict because jQuery library uses object with names e10, e2, e3 to draw relations
      for k,v in enumerate(eKey):
        if (eKey[k]['subject'] in datasetsPortal):
          eKey[k]['type'] = func.getType(eKey[k]['subject'],eKey[k]['object'],dR)
          eKey[k]['subject'] = func.getKey(eKey[k]['subject'],datasets)
          eKey[k]['object'] = func.getKey(eKey[k]['object'],datasets)
        else:
          del eKey[k]

      #specify formats that describe linked data
      LDF = ['rdf','rdfa','sparql','n-triples','turtle','n3','nq']

      #preparing data for using in HTML template
      c.eKey = eKey
      c.datasets = datasets
      c.ldf = LDF
      tagURL = helpers.url_for(controller="package", action='read',qualified=True) 
      c.tagURL = tagURL.rstrip('packages') + 'dataset' 

      c.relin_info_test = eKey    
     
      #specifying HTML template to render
      return p.toolkit.render('lire/relationships.html')






