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

from ckan.lib.base import request
from ckan.lib.helpers import parse_rfc_2822_date

from datetime import datetime

from ckan.lib.base import BaseController

class FUNCTIONSController(BaseController):

  #function for calculating five star results for two datasets
  def fiveStar(self, subjectInfo, objectInfo):

    #create datasets dictionary with formats and their five star values
    formatFS = {'pdf':1,'zip':1,'gzip':1,'rar':1,'tar':1,'exe':1,'kmz':1,'wfs':1,'wms':1,'wmts':1,'url':1,'qgis':1,'wcs':1,'sparql':3,'csv':3,'json':3,'jpg':1,'png':1,'tif':1,'gif':1,'html':1,'lyr':1,'shp':1,'sav':1,'esri grid':1,'esri rest':1,'arc/info grid':1,'arc/info ascii grid':1,'rss':2,'georss':2,'xls':2,'xlsx':2,'doc':1,'docx':1,'mdb':1,'mdbx':1,'txt':1,'tfw':1,'arc grid':1,'rtf':1,'tsv':3,'prj':1,'ods':2,'odt':2,'sld':1,'mxd':1,'sbn':1,'sbx':1,'dwg':1,'xml':3,'rdf':4,'wsdl':2,'xsd':2,'open xml':3,'gml':2,'kml':2,'netCDF':1,'gpx':1,'wma':1,'psd':1,'ecw':1,'cdr':1,'odp':1,'icalendar':1,'ppt':1,'pptx':1,'aspx':1,'webpage':1,'api':1,'php':1,'ttl':4,'rdfa':4,'n3':4,'nq':4,'rdf+xml':4,'turtle':3,'n-triples':4}

    #create temporary variables for storing results of calculating
    sD = 0
    oD = 0

    #summarizing five star values of each format in subject dataset to get value for entire dataset
    for keyS, valueS in enumerate(subjectInfo['resources']):
      for keyF, valueF in formatFS.items():
        if (valueS['format'].lower() == keyF):
          sD += valueF

    #summarizing five star values of each format in object dataset to get value for entire dataset
    for keyO, valueO in enumerate(objectInfo['resources']):
      for keyF, valueF in formatFS.items():
        if (valueO['format'].lower() == keyF):
          oD += valueF

    #obtaining mean values for subject dataset
    sD = sD / len(subjectInfo['resources'])
    sD = int(round(sD, 0))

    #obtaining mean values for object dataset
    oD = oD / len(objectInfo['resources'])
    oD = int(round(oD, 0))

    #storing results in list
    results = [sD, oD]

    return results

  #function for examination datasets time creation
  def compareDateTime(self, subjectInfo, objectInfo):

    resultDateTime = 0
    sDT = 0
    oDT = 0

    #converting datasets time creation into miliseconds for examination
    sDT = datetime.strptime(subjectInfo['metadata_created'],'%Y-%m-%dT%H:%M:%S.%f')

    oDT = datetime.strptime(objectInfo['metadata_created'],'%Y-%m-%dT%H:%M:%S.%f')

    #examination of time
    if (sDT < oDT):
      #subject dataset is older
      resultDateTime = 1
    else:
      #object dataset is older
      resultDateTime = 0

    return resultDateTime

  #function for comparing whether two datasets belongs to the same group
  def compareGroups(self, subjectInfo, objectInfo):

    sG = []
    oG = []
    group = 'false'
    control = 0

    #get names of all groups that subject dataset belongs to
    for list in subjectInfo['groups']:
      for key,value in list.items():
        if 'name' in key:
          sG.append(value)
    
    #get names of all groups that object dataset belongs to
    for list in objectInfo['groups']:
      for key,value in list.items():
        if 'name' in key:
          oG.append(value)

    #firts IF condition examines whether dataset belongs to any group
    if((len(sG) > 0) and (len(oG) > 0)):
      #as datasets can belong to different groups, we examine whether they have at least one same group
      #if we find at least one matching we break loops
      for keyS,valueS in enumerate(sG):
        for keyO,valueO in enumerate(oG):
          if valueS == valueO:
            group = 'true'
            control = 1
            break
        if (control == 1):
          break
    else:
      group = 'N.A.'

    return group

  #get dataset key from dictionary where are all datasets in portal
  def getKey(self,datasetName,datasets):
    
    key = 0
    
    for k,v in datasets.items():
      if (datasetName == datasets[k]['title']):
        key = k   

    return key

  #get type of relation between two datasets
  def getType(self,s,o,dR):

    type = ''
    
    for k1,v1 in dR.items():
      for k2,v2 in dR.items():
        if ((dR[k1][0]['subject'] == s) and (dR[k2][0]['object'] == o)):
          type = dR[k1][0]['type']
          break

    return type





