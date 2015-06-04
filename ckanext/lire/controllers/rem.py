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

c = p.toolkit.c
render = p.toolkit.render

from ckanext.lire.controllers.pan import (
    PANController,
)
from ckanext.lire.controllers.functions import (
    FUNCTIONSController,
)
##############
## LIRE REM ##
##############
class REMController(BaseController):

  #functions for examination of two datasets that user want to relate
  #and suggesting appropriate relation based on examination
  def examineDatasets(self):

    #get all information about subject and object dataset
    subjectInfo = toolkit.get_action('package_show')(
        data_dict={'id': request.params['subject']})

    objectInfo = toolkit.get_action('package_show')(
        data_dict={'id': request.params['object']})

    tagCount = 0
    tagSOO = 0
    tagOSO = 0
    org_gru = ''
    resultOT = {}
    resultGT = {}
    tracking = {}
    organization = ''
    group = ''
    sOpen = 0
    oOpen = 0

    #examine in following two IF loops whether subject and object dataset are open
    if str(subjectInfo['isopen']) is 'True':
      sOpen = 1
    else:
      sOpen = 0

    if str(objectInfo['isopen']) is 'True':
      oOpen = 1
    else:
      oOpen = 0

    #examine same/similar tags in subject and object dataset
    for listS in subjectInfo['tags']:
      for keyS,valueS in listS.items():
        if 'display_name' in keyS:
          for listO in objectInfo['tags']:
            for keyO,valueO in listO.items():
              if 'display_name' in keyO:
                if listS[keyS] == listO[keyO]:
                  tagCount += 1

    #examine whether datasets are created by same organization
    if subjectInfo['organization']['name'] == objectInfo['organization']['name']:
      organization = 'true'
    else:
      organization = 'false'

    #examine % of similar tags of subject dataset in object dataset organization and vice versa
    resultOT = self.tagsOrganization(subjectInfo,objectInfo)
    tagSOO = resultOT[0]
    tagOSO = resultOT[1]

    #examine % of similar tags of subject dataset in object dataset group and vice versa
    resultGT = self.tagsGroup(subjectInfo,objectInfo)
    tagSOG = resultGT[0]
    tagOSG = resultGT[1]

    #examine whether two datasets are already related with links in extras part
    resultLinks = self.extrasLinks(subjectInfo,objectInfo)

    #get % of similar formats between subject and object dataset
    resultFormats = self.compareFormats(subjectInfo,objectInfo)
    formatsSO = resultFormats[0]
    formatsOS = resultFormats[1]

    functions = FUNCTIONSController()

    #get five star mark for both datasets
    fs = functions.fiveStar(subjectInfo,objectInfo)
    fsS = fs[0]
    fsO = fs[1]

    #examine number of views of datasets
    tracking['subjectD'] = {'total':subjectInfo['tracking_summary']['total'],'recent':subjectInfo['tracking_summary']['recent']}
    tracking['objectD'] = {'total':objectInfo['tracking_summary']['total'],'recent':objectInfo['tracking_summary']['recent']}
    trackingSD = tracking["subjectD"]
    trackingOD = tracking["objectD"]

    #examine number of views of dataset resources
    trackingSResources = self.trackingResources(subjectInfo)
    trackingOResources = self.trackingResources(objectInfo)

    #examine which dataset is older
    dateTimeCreation = functions.compareDateTime(subjectInfo, objectInfo)

    #examine whether datasets have at leas one same group
    group = functions.compareGroups(subjectInfo,objectInfo)

    #check if dataset belong to the same group or organization 
    #we need this information so we can apply in the model the requirement that the dataset can have a relationship 
    #parent_of && child_of only if they belong to the same organization or group
    if ((organization is 'true') and (group is 'true')):
      org_gru = 1
    else:
      org_gru = 0

    #examine whether datasets have at least one linked format
    linkedFormat = self.linkedFormat(subjectInfo,objectInfo)

    #examine whether datasets have at least one machine processable format
    machineProcessable = self.machineProcessable(subjectInfo,objectInfo)

    #examine dataset parameters accordint to the model to check can we suggest 
    #some type of relation to the user apart from the one  he choose
    if ((tagCount > 0) and (org_gru == 1) and (tagSOO >= tagOSO) and (tagSOG >= tagOSG) and (resultLinks is 'true') and (formatsSO > formatsOS) and (dateTimeCreation == 2) and (trackingSD['total'] < trackingOD['total']) and (trackingSD['recent'] < trackingOD['recent']) and (fsS < fsO) and (sOpen == 1) and (oOpen == 1)):
      suggestedType = 'child_of'
    elif ((tagCount > 0) and (org_gru == 1) and (tagSOO <= tagOSO) and (tagSOG <= tagOSG) and (resultLinks is 'true') and (formatsSO < formatsOS) and (dateTimeCreation == 1) and (trackingSD['total'] > trackingOD['total']) and (trackingSD['recent'] > trackingOD['recent']) and (fsS > fsO) and (sOpen == 1) and (oOpen == 1)): 
      suggestedType = 'parent_of'
    elif ((tagCount > 0) and (formatsSO >= formatsOS) and (dateTimeCreation == 2) and (fsS > 3) and (fsO > 3) and (linkedFormat == 1) and (sOpen == 1) and (oOpen == 1) and (machineProcessable == 1)):
      suggestedType = 'links_from'
    elif ((tagCount > 0) and (formatsSO <= formatsOS) and (dateTimeCreation == 1) and (fsS > 3) and (fsO > 3) and (linkedFormat == 1) and (sOpen == 1) and (oOpen == 1) and (machineProcessable == 1)):
      suggestedType = 'links_to'
    else:
      suggestedType = 'N.A.'

    #preparing data for displaying to the user
    data = {"tagCount":tagCount,"org_gru":org_gru,"organization":organization,"group":group,"sOpen":sOpen,"oOpen":oOpen,"tagSOO":tagSOO,"tagOSO":tagOSO,"tagSOG":tagSOG,"tagOSG":tagOSG,"extrasLink":resultLinks,"formatsSO":formatsSO,"formatsOS":formatsOS,"fsS":fsS,"fsO":fsO,"trackingSD":trackingSD,"trackingOD":trackingOD,"trackingSResources":trackingSResources,"trackingOResources":trackingOResources,"dateTimeCreation":dateTimeCreation,"linkedFormat":linkedFormat,"machineProcessable":machineProcessable,"suggestedType":suggestedType}
    
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return json.dumps(data)

  #function for examination whether two datasets have at least one machine processable format
  def machineProcessable(self, subjectInfo, objectInfo):

    #creating a list of machine processable formats
    formats = ['rdf','ttl','rdfa','rdf+xml','n3','n-triples','nq','sparql','csv','json','tsv','xml','open xml']

    mp = ''
    tmp1 = ''
    tmp2 = ''
    control = 0

    #examine whether subject dataset have at least one machine processable format
    for keyS, valueS in enumerate(subjectInfo['resources']):
      for keyF, valueF in enumerate(formats):
        if (valueS['format'].lower() == valueF):
          tmp1 = 'true'
          control = 1
          break
        else:
          tmp1 = 'false'
        if (control == 1):
          break

    control = 0

    #examine whether object dataset have at least one machine processable format
    for keyO, valueO in enumerate(objectInfo['resources']):
      for keyF, valueF in enumerate(formats):
        if (objectInfo['resources'][keyO]['format'].lower() == formats[keyF]):
          tmp2 = 'true'
          control = 1
          break
        else:
          tmp2 = 'false'
        if (control == 1):
          break

    #compare results
    if((tmp1 is 'true') and (tmp2 is 'true')):
      mp = 'true'
    else:
      mp = 'false'

    return mp
  
  #function for examination whether two datasets have at least one linked data format
  def linkedFormat(self, subjectInfo, objectInfo):

    #creating a list of linked data formats
    formats = ['rdf', 'rdfa', 'ttl', 'n3', 'nq' ,'rdf+xml', 'turtle', 'n-triples']

    lF = ''
    tmp1 = ''
    tmp2 = ''
    control = 0

    #examine whether subject dataset have at least one linked data format
    for keyS, valueS in enumerate(subjectInfo['resources']):
      for keyF, valueF in enumerate(formats):
        if (valueS['format'].lower() == valueF):
          tmp1 = 'true'
          control = 1
          break
        else:
          tmp1 = 'false'
        if (control == 1):
          break

    control = 0

    #examine whether object dataset have at least one linked data format
    for keyO, valueO in enumerate(objectInfo['resources']):
      for keyF, valueF in enumerate(formats):
        if (objectInfo['resources'][keyO]['format'].lower() == formats[keyF]):
          tmp2 = 'true'
          control = 1
          break
        else:
          tmp2 = 'false'
        if (control == 1):
          break

    #compare results
    if((tmp1 is 'true') and (tmp2 is 'true')):
      lF = 'true'
    else:
      lF = 'false'

    return lF

  #function for summarizing numbers of views of dataset resources
  def trackingResources(self, datasetInfo):
 
    datasetTrackingResources = {'total':0,'recent':0}
 
    for key, value in enumerate(datasetInfo['resources']):
      datasetTrackingResources['total'] = datasetTrackingResources['total'] + datasetInfo['resources'][key]['tracking_summary']['total']
      datasetTrackingResources['recent'] = datasetTrackingResources['recent'] + datasetInfo['resources'][key]['tracking_summary']['recent'] 

    return datasetTrackingResources

  #function for examination number of similar formats of datasets
  def compareFormats(self, subjectInfo, objectInfo):

    formatsSO = 0
    formatsOS = 0

    sDF = []
    oDF = []

    pan = PANController()

    #get data formats in subject and object dataset
    sDF = pan._get_formats(subjectInfo['name'])
    oDF = pan._get_formats(objectInfo['name'])

    #examine number of similar formats from subject dataset in object dataset
    for keyS, valueS in enumerate(sDF):
      for keyO, valueO in enumerate(oDF):
        if (valueS == valueO):
          formatsSO += 1

    #examine number of similar formats from object dataset in subject dataset
    for keyO, valueO in enumerate(oDF):
      for keyS, valueS in enumerate(sDF):
        if (valueO == valueS):
          formatsOS += 1

    #calculating mean value for both cases
    formatsSO = formatsSO / len(oDF)
    formatsSO = int(round(formatsSO, 2) * 100)

    formatsOS = formatsOS / len(sDF)
    formatsOS = int(round(formatsOS, 2) * 100)

    results = [formatsSO, formatsOS]

    return results

  #function for examination whether two datasets are related between extras part
  def extrasLinks(self,subjectInfo, objectInfo):

    sLinks = []
    oLinks = []
    linkSO = ''
    linkOS = ''
    link = ''

    for list in subjectInfo['extras']:
      for key,value in list.items():
        if 'links:' in value:
          sLinks.append(value.lstrip('links:'))

    for list in objectInfo['extras']:
      for key,value in list.items():
        if 'links:' in value:
          oLinks.append(value.lstrip('links:'))

    if (len(oLinks) > 0):
      for key,value in enumerate(oLinks):
        if subjectInfo['name'] is oLinks[key]:
          linkSO = 'true'
          break
        else:
          linkSO = 'false'
    else:
      linkSO = 'false'

    if (len(sLinks) > 0):
      for key,value in enumerate(sLinks):
        if objectInfo['name'] is sLinks[key]:
          linkOS = 'true'
          break
        else:
          linkOS = 'false'
    else:
      linkOS = 'false'

    if ((linkSO is 'true') or (linkOS is 'true')):
      link = 'true'
    else:
      link = 'false'

    return link

  #function for examination % of similar tags of subject dataset in object dataset group and vice versa
  def tagsGroup(self, subjectInfo, objectInfo):

    #list for storing tags from subject and object group
    sDG = []
    oDG = []
    tagSOG = 0
    tagOSG = 0

    #get all group tags from subject dataset
    for list in subjectInfo['groups']:
      for key,value in list.items():
        if 'name' in key:
          #get detailed information about each group
          tempG = toolkit.get_action('group_show')(
              data_dict={'id': value})
          #get all tags that have current group
          for tempList in tempG['packages']:
            for tempKey,tempValue in tempList.items():
              if 'name' in tempKey:
                tempSG = toolkit.get_action('package_show')(
                    data_dict={'id': tempValue})
                for tempL in tempSG['tags']:
                  for tempK,tempV in tempL.items():
                    if 'display_name' in tempK:
                      sDG.append(tempV)

    #get all group tags from object dataset
    for list in objectInfo['groups']:
      for key,value in list.items():
        if 'name' in key:
          #get detailed information about each group
          tempG = toolkit.get_action('group_show')(
              data_dict={'id': value})
          #get all tags that have current group
          for tempList in tempG['packages']:
            for tempKey,tempValue in tempList.items():
              if 'name' in tempKey:
                tempSG = toolkit.get_action('package_show')(
                    data_dict={'id': tempValue})
                for tempL in tempSG['tags']:
                  for tempK,tempV in tempL.items():
                    if 'display_name' in tempK:
                      oDG.append(tempV)

    #examine same/similar tags from subject dataset and group from object dataset
    for listS in subjectInfo['tags']:
      for keyS,valueS in listS.items():
        if 'display_name' in keyS:
          for keyO,valueO in enumerate(oDG):
            if listS[keyS] == oDG[keyO]:
              tagSOG += 1

    #calculate % of same/similar tags
    if (len(oDG) > 0):
      tagSOG = tagSOG / len(oDG)
      tagSOG = int(round(tagSOG, 2) * 100)
    else:
      tagSOG = 0
    
    #examine same/similar tags from object dataset and group from subject dataset
    for listO in objectInfo['tags']:
      for keyO,valueO in listO.items():
        if 'display_name' in keyO:
          for keyS,valueS in enumerate(sDG):
            if listO[keyO] == sDG[keyS]:
              tagOSG += 1
    
    #calculate % of same/similar tags
    if (len(sDG) > 0):
      tagOSG = tagOSG / len(sDG)
      tagOSG = int(round(tagOSG, 2) * 100)
    else:
      tagOSG = 0

    results = [tagSOG,tagOSG]
    
    return results

  #function for examination % of similar tags of subject dataset in object dataset organization and vice versa
  def tagsOrganization(self,subjectInfo,objectInfo):
    
    tagSOO = 0
    tagOSO = 0
    oDOt = 0
    sDOt = 0
    sDOInfoTags = []
    oDOInfoTags = []
    
    #get detailed information about subject and object organization
    sDOInfo = toolkit.get_action('organization_show')(
        data_dict={'id': subjectInfo['organization']['name']})
    
    oDOInfo = toolkit.get_action('organization_show')(
        data_dict={'id': objectInfo['organization']['name']})

    #examine same/similar tags from subject dataset and tags from object organization
    for list in sDOInfo['packages']:
      for key,value in list.items():
          if 'name' in key:
            tempS = toolkit.get_action('package_show')(
                data_dict={'id': value})
            for tempList in tempS['tags']:
              for tempKey,tempValue in tempList.items():
                if 'display_name' in tempKey:
                  sDOInfoTags.append(tempValue)

    #examine same/similar tags from object dataset and tags from subject organization
    for list in oDOInfo['packages']:
      for key,value in list.items():
        if 'name' in key:
            tempO = toolkit.get_action('package_show')(
                data_dict={'id': value})
            for tempList in tempO['tags']:
              for tempKey,tempValue in tempList.items():
                if 'display_name' in tempKey:
                  oDOInfoTags.append(tempValue)

    for listS in subjectInfo['tags']:
      for keyS,valueS in listS.items():
        if 'display_name' in keyS:
          for keyO,valueO in enumerate(oDOInfoTags):
            if listS[keyS] == oDOInfoTags[keyO]:
              tagSOO += 1
    
    #calculate mean value for subject dataset tags in object dataset organization
    oDOt = len(oDOInfoTags)
    
    tagSOO = tagSOO / oDOt
    tagSOO = int(round(tagSOO, 2) * 100)

    for listO in objectInfo['tags']:
      for keyO,valueO in listO.items():
        if 'display_name' in keyO:
          for keyS,valueS in enumerate(sDOInfoTags):
            if listO[keyO] == sDOInfoTags[keyS]:
              tagOSO += 1

    #calculate mean value for object dataset tags in subject dataset organization
    sDOt = len(sDOInfoTags)

    tagOSO = tagOSO / sDOt
    tagOSO = int(round(tagOSO, 2) * 100)

    results = [tagSOO,tagOSO]

    return results


