import os
import subprocess
import unittest

import netCDF4
import numpy as np
import requests

import bald
from bald.tests import BaldTestCase

OGCFiles = ('https://raw.githubusercontent.com/opengeospatial/netcdf-ld/'
            'master/standard/abstract_tests/')

class Test(BaldTestCase):
    def setUp(self):
        self.cdl_path = os.path.join(os.path.dirname(__file__), 'CDL')
        self.ttl_path = os.path.join(os.path.dirname(__file__), 'TTL')
        self.maxDiff = None
        
    def test_conformance_a(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'ogcClassA.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            with open(cdl_file, 'w') as cdlf:
                cdluri = '{}CDL/ogcClassA.cdl'.format(OGCFiles)
                r = requests.get(cdluri)
                if r.status_code != 200:
                    raise ValueError('CDL download failed for {}'.format(cdluri))
                cdlf.write(r.text)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'http://secret.binary-array-ld.net/identity.nc'
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            ttl_file = os.path.join(self.ttl_path, 'ogcClassA.ttl')
            with open(ttl_file, 'w') as ttlf:
                ttluri = '{}TTL/ogcClassA.ttl'.format(OGCFiles)
                r = requests.get(ttluri)
                if r.status_code != 200:
                    raise ValueError('TTL download failed for {}'.format(ttluri))
                ttlf.write(r.text)
            with open(ttl_file, 'r') as sf:
                expected_ttl = sf.read()
            os.remove(ttl_file)
            os.remove(cdl_file)
            self.assertEqual(expected_ttl, ttl)

    def test_conformance_b(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'ogcClassB.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            with open(cdl_file, 'w') as cdlf:
                cdluri = '{}CDL/ogcClassB.cdl'.format(OGCFiles)
                r = requests.get(cdluri)
                if r.status_code != 200:
                    raise ValueError('CDL download failed for {}'.format(cdluri))
                cdlf.write(r.text)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'http://secret.binary-array-ld.net/prefix.nc'
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri, cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            ttl_file = os.path.join(self.ttl_path, 'ogcClassA.ttl')
            with open(ttl_file, 'w') as ttlf:
                ttluri = '{}TTL/ogcClassB.ttl'.format(OGCFiles)
                r = requests.get(ttluri)
                if r.status_code != 200:
                    raise ValueError('TTL download failed for {}'.format(ttluri))
                ttlf.write(r.text)
            with open(ttl_file, 'r') as sf:
                expected_ttl = sf.read()
            os.remove(ttl_file)
            os.remove(cdl_file)
            self.assertEqual(expected_ttl, ttl)

    def test_conformance_c(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'ogcClassC.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            with open(cdl_file, 'w') as cdlf:
                cdluri = '{}CDL/ogcClassC.cdl'.format(OGCFiles)
                r = requests.get(cdluri)
                if r.status_code != 200:
                    raise ValueError('CDL download failed for {}'.format(cdluri))
                cdlf.write(r.text)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'http://secret.binary-array-ld.net/alias.nc'
            alias_dict = {'NetCDF': 'http://def.scitools.org.uk/NetCDF'}
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            ttl_file = os.path.join(self.ttl_path, 'ogcClassA.ttl')
            with open(ttl_file, 'w') as ttlf:
                ttluri = '{}TTL/ogcClassC.ttl'.format(OGCFiles)
                r = requests.get(ttluri)
                if r.status_code != 200:
                    raise ValueError('TTL download failed for {}'.format(ttluri))
                ttlf.write(r.text)
            with open(ttl_file, 'r') as sf:
                expected_ttl = sf.read()
            os.remove(ttl_file)
            os.remove(cdl_file)
            self.assertEqual(expected_ttl, ttl)

    def test_conformance_d(self):
        with self.temp_filename('.nc') as tfile:
            cdlname = 'ogcClassD.cdl'
            cdl_file = os.path.join(self.cdl_path, cdlname)
            with open(cdl_file, 'w') as cdlf:
                cdluri = '{}CDL/ogcClassD.cdl'.format(OGCFiles)
                r = requests.get(cdluri)
                if r.status_code != 200:
                    raise ValueError('CDL download failed for {}'.format(cdluri))
                cdlf.write(r.text)
            subprocess.check_call(['ncgen', '-o', tfile, cdl_file])
            cdl_file_uri = 'http://secret.binary-array-ld.net/attributes.nc'
            alias_dict = {'NetCDF': 'http://def.scitools.org.uk/NetCDF'}
            root_container = bald.load_netcdf(tfile, baseuri=cdl_file_uri,
                                              alias_dict=alias_dict, cache=self.acache)
            ttl = root_container.rdfgraph().serialize(format='n3').decode("utf-8")
            ttl_file = os.path.join(self.ttl_path, 'ogcClassA.ttl')
            with open(ttl_file, 'w') as ttlf:
                ttluri = '{}TTL/ogcClassD.ttl'.format(OGCFiles)
                r = requests.get(ttluri)
                if r.status_code != 200:
                    raise ValueError('TTL download failed for {}'.format(ttluri))
                ttlf.write(r.text)
            with open(ttl_file, 'r') as sf:
                expected_ttl = sf.read()
            os.remove(ttl_file)
            os.remove(cdl_file)
            self.assertEqual(expected_ttl, ttl)
