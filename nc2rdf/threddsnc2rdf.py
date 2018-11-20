import nc2rdf
import re
import sys
import datetime
import argparse
import uuid
try:
        from urlparse import urljoin  # Python2
        from urlparse import urlsplit, urlunsplit
        from urlparse import urlparse
except ImportError:
        from urllib.parse import urljoin  # Python3
        from urllib.parse import urlsplit, urlunsplit
        from urllib.parse import urlparse
import lxml
import json
import requests
from dateutil import parser
from pydap.client import open_url
import pydap.lib
from owslib.wms import WebMapService
from owslib.iso import *
import urllib
from timeit import default_timer as timer
import code, traceback, signal
import os

pydap.lib.TIMEOUT = 5


#Utility to allow debugger to attach to this program
def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message  = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)

#Utility to allow debugger to attach to this program
def listen():
    signal.signal(signal.SIGUSR1, debug)  # Register handler

class ThreddsHarvester:
    """Harvests metadata from a Thredds service"""
    def lookup_datasets_in_catalog(self, base_url, catalog_url, list_of_netcdf_files):
       """loads the catalog xml and extracts dataset access information"""
       xml = None
       res = requests.get(catalog_url)
       if res.status_code == 200:
          xml = lxml.etree.fromstring(res.content)
       else:
          print("Exiting ThreddsHarvester - HTTP code for catalog_url(" + catalog_url + ") was ", res.status_code)
          return None
          
#       try:
#          xml = lxml.etree.parse(catalog_url)
#       except Exception as e:
#           print("Exception caught in ThreddsHarvester - catalog_url(" + catalog_url + ")")
#           print(e)
#           return
       namespaces = {"xlink": "http://www.w3.org/1999/xlink", 'c':'http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0'}
       access_infos = []
       used_types = []
       for node in xml.xpath('/c:catalog/c:service/c:service', namespaces=namespaces):
           access_type = node.get('serviceType')
           if access_type not in used_types:
               used_types.append(access_type)
               access_info = { "type" : access_type, "access" : node.get('base') }
               access_infos.append(access_info)

       #print "b: " + base_url
       #print "c: " + catalog_url

       #open_dap_result = xml.xpath('/c:catalog/*/c:service[@serviceType="opendap"]', namespaces=namespaces)
       open_dap_result = xml.xpath('//c:service[@serviceType="opendap" or @serviceType="OPENDAP" or @serviceType="OPeNDAP"]', namespaces=namespaces)
       if len(open_dap_result) > 0:
          open_dap_prefix = open_dap_result[0].get('base')
       else:
          open_dap_prefix = xml.xpath('/c:catalog/c:service[@serviceType="OPeNDAP"]', namespaces=namespaces)[0].get('base')

       iso_prefix_result = xml.xpath('/c:catalog/c:service/c:service[@serviceType="ISO"]', namespaces=namespaces)
       wms_prefix_result = xml.xpath('/c:catalog/c:service/c:service[@serviceType="WMS"]', namespaces=namespaces)

       if len(wms_prefix_result) > 0:
          wms_prefix = wms_prefix_result[0].get('base')
       else:
          wms_prefix = None

       if len(iso_prefix_result) > 0:
          iso_prefix = iso_prefix_result[0].get('base')
       else:
          iso_prefix = None

       res = xml.xpath('/c:catalog/c:dataset/c:dataset|/c:catalog/c:dataset[@urlPath]|/c:catalog/c:dataset/c:dataset/c:access[@urlPath and @serviceName="dap"]|//c:catalogRef', namespaces=namespaces)

       for item in res:
          print(item)
          #if 'urlPath' in item.keys() and 'serviceName' in item.keys():
          if 'urlPath' in item.keys():
             # get the name from parent elem 
             parent = item.getparent()
             name = parent.attrib['name']

             url_path = item.attrib['urlPath']
             iso_path = base_url + iso_prefix + url_path if iso_prefix != None else None
             wms_path = base_url + wms_prefix + url_path if wms_prefix != None else None
             dataset_access_infos = []
             print("urlPath: " + url_path)
             for access_info in access_infos:
                  dataset_access_info = { "type" : access_info["type"], "access" :  base_url + access_info["access"] + url_path }
                  dataset_access_infos.append(dataset_access_info)
             datasetEntry = { 'name' : name, 'open_dap_path': base_url + open_dap_prefix + url_path, 'iso_path': iso_path, 'wms_path': wms_path, 'access_infos' : dataset_access_infos }
             list_of_netcdf_files.append(datasetEntry)
          elif 'urlPath' in item.keys():
              url_path = item.attrib['urlPath']
              iso_path = base_url + iso_prefix + url_path if iso_prefix != None else None
              wms_path = base_url + wms_prefix + url_path if wms_prefix != None else None
              dataset_access_infos = []
              print("urlPath: " + url_path)
              for access_info in access_infos:
                  dataset_access_info = { "type" : access_info["type"], "access" :  base_url + access_info["access"] + url_path }
                  dataset_access_infos.append(dataset_access_info)
              datasetEntry = { 'name' : item.attrib['name'], 'open_dap_path': base_url + open_dap_prefix + url_path, 'iso_path': iso_path, 'wms_path': wms_path, 'access_infos' : dataset_access_infos }
              list_of_netcdf_files.append(datasetEntry)
          if '{http://www.w3.org/1999/xlink}href' in item.keys():
                  newCatalogPath = item.attrib["{http://www.w3.org/1999/xlink}href"]
                  #print  item 
                  #print "baseUrl " + base_url
                  #print "href " + newCatalogPath
                  #print "catalogUrl " + catalog_url
                  newCatalogUrl = urljoin(catalog_url, newCatalogPath)
                  print("newCatalogUrl " + newCatalogUrl)
                  if (newCatalogPath.endswith('catalog.xml')):
                      self.lookup_datasets_in_catalog(base_url, newCatalogUrl, list_of_netcdf_files)
                  elif (newCatalogPath.endswith('.xml')):
                      self.lookup_datasets_in_catalog(base_url, catalog_url.replace('catalog.xml', newCatalogPath), list_of_netcdf_files)
       return list_of_netcdf_files

def get_opendap_record(dataset_url):
    """Get the open dap record from the thredds service and look for the eReefs observed properties, build a record of these and return"""
    data = {}
    print(dataset_url)
    datasetInformation = open_url(dataset_url)
    for variable in datasetInformation.keys():
        variable_properties = datasetInformation[variable]
        data[variable] = {}
        list_attributes = variable_properties.attributes.keys()
        for variable_attribute in list_attributes :
           value = variable_properties.attributes[variable_attribute]
           data[variable][variable_attribute] = value
    return data

def assign_url_later(assign_url_map, property_to_assign, url_to_assign):
    """build a record of a url and which properties in the dataset record it exists on, also update a list of unique urls, assign_url_map holds this information for later use when url is resolved"""
    if not url_to_assign in assign_url_map["unique_urls"]:
        assign_url_map["url_property_map"][url_to_assign] = []
        assign_url_map["unique_urls"].append(url_to_assign)
    assign_url_map["url_property_map"][url_to_assign].append(property_to_assign)

class RecordManager:
    """Abstract class for managing dataset record persistence"""
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def should_update(self, dataset_address):
        return True

    def assign_urls(self, assign_url_map):
        """Resolve urls in the assign_url_map and, if redirected, update the dataset records to use the redirected url"""
        failed_urls = []
        redirected_urls = []
        original_to_resolved_url = {}
        url_contents = {}

        print(assign_url_map)


def process_dataset(assign_url_map, dataset_address, thredds_url, thredds_catalog_url, outputformat='turtle', isSchemaOrgOutput=False):
    """Extract information about the specific at dataset_address"""
    print("processing dataset address: " + dataset_address['name'])

    #Use multiple endpoints to get information about this dataset with redundancy
    opendap_url = dataset_address['open_dap_path']
    iso_url = dataset_address['iso_path']
    if 'wms_path' in dataset_address and dataset_address['wms_path'] != None:
       wms_url = dataset_address['wms_path']  + "?service=WMS"

    #Common information across all variables in this dataset
    common_info = {}

    opendap_information = {}
    try:
        opendap_information = get_opendap_record(opendap_url)
    except Exception as e:
        print("Exception caught in perform_harvest - get_opendap_record(" + opendap_url + "): ", e.message)

    common_info["access"] = dataset_address["access_infos"]
    common_info["dataset_id"] = opendap_url

    #print opendap_information
    #print json.dumps(opendap_information, check_circular=False, sort_keys=True, indent=4, separators=(',', ': '), default=datetime_handler)
    
    if isSchemaOrgOutput:
       outputformat = 'json-ld'
       unique_dataset_id = uuid.uuid4().hex
       outputpath = OUTDIR + "/" + unique_dataset_id + ".json"
       print("emitting to " + outputpath)
       nc2rdf.nc2schemaorg(opendap_url, outputformat, outputfile=outputpath, baseuri=opendap_url)
    elif outputformat == 'turtle':
       unique_dataset_id = uuid.uuid4().hex
       outputpath = OUTDIR + "/" + unique_dataset_id + ".ttl"
       print("emitting to " + outputpath)
       nc2rdf.nc2rdf(opendap_url, 'turtle', outputfile=outputpath, baseuri=opendap_url)


def perform_harvest(thredds_url, thredds_catalog_url, outputformat='turtle', isSchemaOrgOutput=False ):
    """Perform harvest on the thredds_catalog_url"""
    #Get dataset information
    #print thredds_url
    #print thredds_catalog_url
    list_datasets_address = harvester.lookup_datasets_in_catalog(thredds_url, thredds_catalog_url, [])
    #print list_datasets_address
    dataset_uri = ''

    #Prepare a map for delayed resolution of redirected urls
    assign_url_map = { "unique_urls" : [], "url_property_map": {} }

    #process other dataset information
    for dataset_address in list_datasets_address:
       try:
          process_dataset(assign_url_map, dataset_address, thredds_url, thredds_catalog_url, outputformat, isSchemaOrgOutput=isSchemaOrgOutput)
       except requests.exceptions.HTTPError as e:
          print("HTTPError caught in perform_harvest: ", e.message , " ", thredds_catalog_url)
       except AttributeError as e:
          print("AttributeError caught in perform_harvest: ", e.message , " ", thredds_catalog_url)


def process_thredds(thredds_url, isSchemaOrgOutput=False):
    """harvest thredds endpoint"""
    #assemble catalog url

    if (thredds_url.endswith('catalog.xml')):
        thredds_catalog_url = thredds_url
        thredds_url = get_base_url(thredds_url) 
    else:
       thredds_catalog_url = thredds_url + '/catalog/catalog.xml'
    print('thredds_base_url:' + thredds_url)
    print('thredds_catalog_url:' + thredds_catalog_url)
    perform_harvest(thredds_url, thredds_catalog_url, isSchemaOrgOutput=isSchemaOrgOutput)


def get_base_url(url):
    split_url = urlsplit(url)
    # You now have:
    # split_url.scheme   "http"
    # split_url.netloc   "127.0.0.1" 
    # split_url.path     "/asdf/login.php"
    # split_url.query    ""
    # split_url.fragment ""

    # urlunsplit takes and joins a five item iterable, we "" the last two items to remove the query string and fragment. 
    clean_url = urlunsplit((split_url.scheme, split_url.netloc, "", "", ""))
    return clean_url

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
       return x.isoformat()
    raise TypeError("Unknown type")

def checkOrCreateDir(directory):
    if not os.path.exists(directory):
       os.makedirs(directory)

if __name__ == '__main__':
    start = timer()

    harvester = ThreddsHarvester()

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--schema-org', action="store_true", dest="isSchemaOrgOutput", default=False, help="Flag to indicate if schema.org output activated")
    argparser.add_argument('threddsUrlOrCatalog', help='THREDDS endpoint url or catalog.xml')
    args = argparser.parse_args()

    OUTDIR = 'rdf'
    if(args.isSchemaOrgOutput):
       OUTDIR = 'schemaorg'
    #make sure outdir is created
    checkOrCreateDir(OUTDIR)

    process_thredds(args.threddsUrlOrCatalog, args.isSchemaOrgOutput)
    #process_dpn(dpn_url.strip(), DPN_ELDA_RES_ENDPOINT)

    end = timer()
    elapsed = end - start
    print("Execution took ", elapsed, " seconds")
