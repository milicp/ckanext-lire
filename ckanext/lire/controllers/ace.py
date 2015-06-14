from __future__ import division

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import json
import csv
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as helpers

import ckan.plugins as p
from ckan.lib.base import BaseController, response, request

##############
## LIRE ACE ##
##############	
class ACEController(BaseController):

  #functions to add/delete dataset relations
  def storeRelationships(self):

    if (request.params['action'] == 'package_relationship_create'):

      result = toolkit.get_action('package_relationship_create')(
          data_dict={'subject': request.params['subject'],'object':request.params['object'],'type':request.params['type'],'comment':request.params['comment']})

    elif (request.params['action'] == 'package_relationship_delete'):

      result = toolkit.get_action('package_relationship_delete')(
          data_dict={'subject': request.params['subject'],'object':request.params['object'],'type':request.params['type']})      
          #data_dict={'subject':'national-diet-library-authorities','object':'melanoma-skin-cancer-incidence','type':'depends_on'})

    else:

      result = 'test...'

    return json.dumps(result)


