"""
The Portal ANalyzer Controller

This controller exposes functions for PAN module of LIRE
"""
import json
import mimetypes
import posixpath
import urllib
import urlparse
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as helpers

from ckan.lib.base import request
from ckan.lib.helpers import parse_rfc_2822_date

from ckan.lib.base import BaseController

##############
## LIRE PAN ##
##############	
class PANController(BaseController):

  #function for processing datasets by tag, group, organization, random number of datasets and all datasets
  #getting basic information about each dataset
  def process_datasets(self,datasets):

    datasetTags = []
    datasetName = ''
    datasetNotes = ''
    resultDatasets = {}
    relationships = []
    dR = {}
    results = {}

    counter = 0
    counterDR = 0

    for dataset in datasets:
  
      datasetTags = []
      datasetName = ''
      datasetNotes = ''

      #get relations for dataset
      datasetRelationships = toolkit.get_action('package_relationships_list')(
          data_dict={'id': dataset})

      #get detailed information for dataset
      datasetInfo = toolkit.get_action('package_show')(
        data_dict={'id': dataset})

      #get dataset tags
      for list in datasetInfo['tags']:
        for key,value in list.items():
          if 'display_name' in key:
            datasetTags.append(value)
          else:
            continue

      #get dataset name
      datasetName = datasetInfo['title']
      #get dataset description
      datasetNotes = datasetInfo['notes']

      #get all formats in dataset
      datasetFormats = self._get_formats(dataset)
      #get links in extras part of dataset
      datasetExtrasLinks = self._get_extras_links(dataset)

      #create dataset URL
      datasetURL = helpers.url_for(controller='package',action='read',id=datasetName, qualified=True)
 
      #put information in temporary dictionary       
      resultDatasets[counter] = {'notes':datasetNotes,'title':datasetName,'tags':datasetTags,'formats':datasetFormats,'extrasLinks':datasetExtrasLinks,'relationships':datasetRelationships,'url':datasetURL}

      #only dataset which have relations put in following dictionaries and lists
      if not datasetRelationships:
        control = 1          
      else:
        #create first list only with dataset names which have relations
        #we need this list to get names of subject and object dataset in function oneToAllRelations() from RELIN 
        relationships.append(datasetName)
        #create second list for each dataset and his relations
        #we need this list in for loop to add types of relations in list with unique relations
        dR[counterDR] = datasetRelationships
        counterDR += 1
      
      #empty list with tags of current dataset  
      datasetTags = []
      
      counter += 1
    
    results = {'datasets':resultDatasets,'dR':dR,'relationships':relationships}

    return results 

  #get all formats from dataset
  def _get_formats(self,datasetName):
    """
    Gets all formats in one dataset.

    Returns a list of formats.

    ["rdf", "json",...]
    """
        
    dataset = toolkit.get_action('package_show')(
      data_dict={'id': datasetName})

    formats = []

    for list in dataset['resources']:
      for key,value in list.items():
        if key == 'format':
          formats.append(value)

    return formats

  #function for examination whether dataset has links in extras part
  def _get_extras_links(self, datasetName):
    """
    Gets all links in extras part of dataset.

    Returns a list of dataset names.

    ["dataset-name-1", "dataset-name-2",...]
    """
        
    dataset = toolkit.get_action('package_show')(
        data_dict={'id': datasetName})

    links = []

    for list in dataset['extras']:
      for key,value in list.items():
        if 'links:' in value:
          links.append(value.lstrip('links:'))

    return links


