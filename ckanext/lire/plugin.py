import json
import datetime
import random

import ckan.lib.dictization.model_dictize as model_dictize
import ckan.model as model
import ckan.plugins as p
from ckanext.lire.controllers.semre import (
    SEMREController,
)

resource_dictize = model_dictize.resource_dictize

class LIREPlugin(p.SingletonPlugin):

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IDomainObjectModification, inherit=True)
    p.implements(p.IResourceUrlChange)
    p.implements(p.ITemplateHelpers)

    def configure(self, config):
        self.site_url = config.get('ckan.site_url')

    def update_config(self, config):
        # p.toolkit.add_resource('fanstatic', 'rem')
        # check if new templates
        if p.toolkit.check_ckan_version(min_version='2.0'):
            if not p.toolkit.asbool(config.get('ckan.legacy_templates', False)):
                # add the extend templates
                p.toolkit.add_template_directory(config, 'templates_extend')
            else:
                # legacy templates
                p.toolkit.add_template_directory(config, 'templates')
            # templates for helper functions
            p.toolkit.add_template_directory(config, 'templates_new')
        else:
            # FIXME we don't support ckan < 2.0
            p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_public_directory(config, 'public')

    def before_map(self, map):
        lire = 'ckanext.lire.controller:LIREController'
        rem = 'ckanext.lire.controllers.rem:REMController'
        ace = 'ckanext.lire.controllers.ace:ACEController'
        semre = 'ckanext.lire.controllers.semre:SEMREController'

        map.connect('/lire', controller=lire, action='index')

        map.connect('/lire/manager', controller=lire, action='manager')

        map.connect('/lire/semantic', controller=semre, action='semantic')

        map.connect('/lire/linksets.:id', controller=semre, action='linksets')

        map.connect('/lire/organization/:org.:ext', controller=semre, action='org_rdf')

        map.connect('/lire/examineDatasets', controller=rem, action='examineDatasets')

        map.connect('/lire/storeRelationships', controller=ace, action='storeRelationships')
    
        map.connect('/lire/checkDataset', controller=semre, action='checkDataset')

        return map

    #return random int necessary to create position of graphical element (dataset)
    def randomNum(self,num):

      randNum = random.randint(0,num) 

      return randNum

    ################
    ## LIRE SEMRE ##
    ################
    # Use this function in custom template to get dataset relationships
    # It will enable us to represent them semantically
    def semre_dataset(self,datasetName):

      semre = SEMREController()

      # To get dataset relationships we call SEMRE to whom we forward the name of the dataset
      datasetRelationships = semre.semre_create(datasetName)

      return datasetRelationships

    def get_helpers(self):
        return {'randomNum': self.randomNum,'semre_dataset': self.semre_dataset}

