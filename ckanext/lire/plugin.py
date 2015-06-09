import json
import datetime
import random

import ckan.lib.dictization.model_dictize as model_dictize
import ckan.model as model
import ckan.plugins as p
import ckan.lib.celery_app as celery_app

resource_dictize = model_dictize.resource_dictize
send_task = celery_app.celery.send_task

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

        map.connect('/lire', controller=lire, action='index')

        map.connect('/lire/relationships', controller=lire, action='relationships')

        map.connect('/lire/examineDatasets', controller=rem, action='examineDatasets')

        map.connect('/lire/storeRelationships', controller=ace, action='storeRelationships')

        return map

    #return random int necessary to create position of graphical element (dataset)
    def randomNum(self,num):

      randNum = random.randint(0,num) 

      return randNum

    # Use this function in custom template to get dataset relationships
    # It will enable us to represent them semantically
    def semre_create(self,datasetName):

      # To get dataset relationships we call CKAN core function 'package_relationship_list'
      # to whom we forward the name of the dataset
      datasetRelationships = p.toolkit.get_action('package_relationships_list')(
          data_dict={'id': datasetName})

      # return results as dictionary
      return datasetRelationships

    def get_helpers(self):
        return {'randomNum': self.randomNum,'semre_create': self.semre_create}

