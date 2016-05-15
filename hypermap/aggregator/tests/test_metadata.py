# -*- coding: utf-8 -*-

"""
Tests for metadata constructs across models
"""

import unittest

from httmock import with_httmock
from lxml import etree

from owslib.csw import CswRecord

from aggregator.models import gen_anytext, Layer, Service
import aggregator.tests.mocks.wms
import aggregator.tests.mocks.warper
import aggregator.tests.mocks.worldmap


@with_httmock(aggregator.tests.mocks.wms.resource_get)
def create_wms_service():
    service = Service(
        type='OGC:WMS',
        url='http://wms.example.com/ows?',
    )
    service.save()


@with_httmock(aggregator.tests.mocks.warper.resource_get)
def create_warper_service():
    service = Service(
        type='WARPER',
        url='http://warper.example.com/warper/maps',
    )
    service.save()


@with_httmock(aggregator.tests.mocks.worldmap.resource_get)
def create_wm_service():
    service = Service(
        type='WM',
    )
    service.save()


class TestMetadata(unittest.TestCase):
    def setUp(self):
        """setup test data"""
        Service.objects.all().delete()
        create_warper_service()
        create_wm_service()
        create_wms_service()

    def tearDown(self):
        """delete test data"""
        Service.objects.all().delete()

    def test_service_fields(self):
        """test Service metadata fields"""
        layer = Service.objects.filter(type='OGC:WMS').all()[0]
        self.assertIsNotNone(layer.xml, 'Expected XML document')

        xml = etree.fromstring(layer.xml)
        csw_record = CswRecord(xml)

        self.assertIsInstance(xml, etree._Element, 'Expected lxml instance')
        self.assertEqual(layer.title, csw_record.title, 'Expected title equality')
        self.assertEqual(layer.abstract, csw_record.abstract, 'Expected abstract equality')
        self.assertEqual(layer.csw_type, 'service', 'Expected CSW type equality')
        self.assertEqual(layer.csw_typename, 'csw:Record', 'Expected CSW typename equality')
        self.assertEqual(layer.csw_schema, 'http://www.opengis.net/cat/csw/2.0.2', 'Expected CSW schema equality')

        anytext = gen_anytext(layer.title, layer.abstract)
        self.assertEqual(anytext, layer.anytext, 'Expected anytext equality')

    def test_layer_fields(self):
        """test Layer metadata fields"""
        layer = Layer.objects.filter(type='OGC:WMS').all()[0]
        self.assertIsNotNone(layer.xml, 'Expected XML document')

        xml = etree.fromstring(layer.xml)
        csw_record = CswRecord(xml)

        self.assertIsInstance(xml, etree._Element, 'Expected lxml instance')
        self.assertEqual(layer.title, csw_record.title, 'Expected title equality')
        self.assertEqual(layer.abstract, csw_record.abstract, 'Expected abstract equality')
        self.assertEqual(layer.csw_type, 'dataset', 'Expected CSW type equality')
        self.assertEqual(layer.csw_typename, 'csw:Record', 'Expected CSW typename equality')
        self.assertEqual(layer.csw_schema, 'http://www.opengis.net/cat/csw/2.0.2', 'Expected CSW schema equality')

        self.assertEqual(layer.service.id, int(csw_record.relation), 'Expected relation equality')
        self.assertEqual(layer.url, csw_record.source, 'Expected URL/source equality')

        anytext = gen_anytext(layer.title, layer.abstract, list(layer.keywords.names()))
        self.assertEqual(anytext, layer.anytext, 'Expected anytext equality')

if __name__ == '__main__':
    unittest.main()