import json
import mimetypes
import posixpath
import urllib
import urlparse
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as helpers

import rdflib

from ckan.lib.base import request
from ckan.lib.helpers import parse_rfc_2822_date
import ckan.plugins as p
from ckanext.lire.controllers.pan import (
    PANController,
)

from ckan.lib.base import BaseController, response, request

c = p.toolkit.c
render = p.toolkit.render

################
## LIRE SEMRE ##
################
class SEMREController(BaseController):

    # Use this function in custom template to get dataset relationships
    # It will enable us to represent them semantically
    def semre_create(self,datasetName):

      # To get dataset relationships we call CKAN core function 'package_relationship_list'
      # to whom we forward the name of the dataset
      datasetRelationships = p.toolkit.get_action('package_relationships_list')(
          data_dict={'id': datasetName})

      # return results as dictionary
      return datasetRelationships

    #function for semantics...
    def semantic(self):

      datasets = toolkit.get_action('package_list')(
              data_dict={})

      c.datasets = datasets

      tagURL = helpers.url_for(controller="package", action='read',qualified=True)
      sourceURL = tagURL.rstrip('packages')
      c.sourceURL = sourceURL

      c.test = 'aaa'

      return render('lire/semantic.html')

   #function for semantics...
    def checkDataset(self):


      tagURL = helpers.url_for(controller="package", action='read',qualified=True)
      sourceURL = tagURL.rstrip('packages')

      datasetURL = sourceURL + 'dataset/' + request.params['dataset'] + '.rdf'

      g = rdflib.Graph()
      g.load(datasetURL)

      resultS = 0
      resultO = 0
      rowS = g.query('select ?s where { ?Dataset void:subjectsTarget ?s . filter isURI(?s) . }')
      resultS = resultS + len(rowS)
      rowO = g.query('select ?o where { ?Dataset void:objectsTarget ?o . filter isURI(?o) . }')
      resultO = resultO + len(rowO)

      #get relations for dataset
      dR = toolkit.get_action('package_relationships_list')(
          data_dict={'id': request.params['dataset']})


      if (((len(dR) - resultS) == 0) and ((len(dR) - resultO) == 0)):
        linksetsS = 0
        linksetsO = 0
      else:
        linksetsS = len(dR) - resultS
        linksetsO = len(dR) - resultO
     
      
      results = {'linksetsS':linksetsS,'linksetsO':linksetsO,'datasetURL':datasetURL}

      response.headers['Content-Type'] = 'application/json;charset=utf-8'
      return json.dumps(results)

    #function for linksets in RDF...
    def linksets(self, id=None):

      #load controller for processing datasets by tag, group, organization, random number of datasets and all datasets
      pan = PANController()

      tempDatasets = toolkit.get_action('package_list')(
              data_dict={})

      pan_rezultati = pan.process_datasets(tempDatasets)

      #get datasets with relations
      dR = pan_rezultati['dR']

      c.linksets = dR

      tagURL = helpers.url_for(controller="package", action='read',qualified=True)
      tagURL = tagURL.rstrip('packages') + 'dataset'
      c.tagURL = tagURL

      if (id == 'rdf'):
        response.headers['Content-Type'] = 'application/rdf+xml; charset=utf-8'
        return render('linksets/linksets.rdf')
      elif(id == 'nt'):
        response.headers['Content-Type'] = 'text/n3; charset=utf-8'
        return render('linksets/linksets.nt')
      else:
        response.headers['Content-Type'] = 'text/n3; charset=utf-8'
        return render('linksets/linksets.n3')

    #function for group in RDF...
    def org_rdf(self, org=None, ext=None):

      orgInfo = toolkit.get_action('organization_show')(
          data_dict={'id': org })

      URL = helpers.url_for(controller="package", action='read',qualified=True)
      organizationURL = URL.rstrip('packages') + 'organization'
      groupURL = URL.rstrip('packages') + 'group'
      datasetURL = URL.rstrip('packages') + 'dataset'
      userURL = URL.rstrip('packages') + 'user'
      c.groupURL = groupURL
      c.organizationURL = organizationURL
      c.datasetURL = datasetURL 
      c.organization = orgInfo      
      c.userURL = userURL

      if (ext == 'rdf'):
        response.headers['Content-Type'] = 'application/rdf+xml; charset=utf-8'
        return render('organization/read.rdf')
      elif(ext == 'nt'):
        response.headers['Content-Type'] = 'text/n3; charset=utf-8'
        return render('organization/read.nt')
      else:
        response.headers['Content-Type'] = 'text/n3; charset=utf-8'
        return render('organization/read.n3')

