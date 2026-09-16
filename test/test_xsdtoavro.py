import os
import sys
import tempfile
from os import path, getcwd
from fastavro.schema import load_schema

current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_script_path))
sys.path.append(project_root)

import json
import unittest
from unittest.mock import patch
from avrotize.xsdtoavro import convert_xsd_to_avro

class TestXsdToAvro(unittest.TestCase):

    def validate_avro_schema(self, avro_file_path):
        load_schema(avro_file_path)

    def test_convert_crmdata_xsd_to_avro(self):
        cwd = os.getcwd()        
        xsd_path = os.path.join(cwd, "test", "xsd", "crmdata.xsd")
        avro_path = os.path.join(tempfile.gettempdir(), "avrotize", "crmdata.avsc")
        dir = os.path.dirname(avro_path)
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        
        convert_xsd_to_avro(xsd_path, avro_path)           
        self.validate_avro_schema(avro_path)

    def test_convert_iso20022_xsd_to_avro1(self):
        cwd = os.getcwd()        
        xsd_path = os.path.join(cwd, "test", "xsd", "acmt.003.001.08.xsd")
        avro_path = os.path.join(tempfile.gettempdir(), "avrotize", "acmt.003.001.08.avsc")
        dir = os.path.dirname(avro_path)
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        
        convert_xsd_to_avro(xsd_path, avro_path)
        self.validate_avro_schema(avro_path)

    def test_convert_iso20022_xsd_to_avro2(self):
        cwd = os.getcwd()        
        xsd_path = os.path.join(cwd, "test", "xsd", "admi.017.001.01.xsd")
        avro_path = os.path.join(tempfile.gettempdir(), "avrotize", "admi.017.001.01.avsc")
        dir = os.path.dirname(avro_path)
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        
        convert_xsd_to_avro(xsd_path, avro_path)
        self.validate_avro_schema(avro_path)

    

    def test_optional_elements_get_a_null_default(self):
        """ minOccurs="0" elements become ["null", T] with default null; required elements have no default """
        cwd = os.getcwd()
        xsd_path = os.path.join(cwd, "test", "xsd", "optional-elements.xsd")
        avro_path = os.path.join(tempfile.gettempdir(), "avrotize", "optional-elements.avsc")
        os.makedirs(os.path.dirname(avro_path), exist_ok=True)

        convert_xsd_to_avro(xsd_path, avro_path)
        self.validate_avro_schema(avro_path)

        with open(avro_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        def find_record(node, name):
            if isinstance(node, dict):
                if node.get("type") == "record" and node.get("name") == name:
                    return node
                for value in node.values():
                    found = find_record(value, name)
                    if found is not None:
                        return found
            elif isinstance(node, list):
                for value in node:
                    found = find_record(value, name)
                    if found is not None:
                        return found
            return None
        record = find_record(schema, "OptionalElementsV1")
        self.assertIsNotNone(record, "the complex type becomes a nested record")
        fields = {f["name"]: f for f in record["fields"]}
        self.assertEqual("string", fields["id"]["type"])
        self.assertNotIn("default", fields["id"])
        self.assertEqual(["null", "string"], fields["subject"]["type"])
        self.assertIn("default", fields["subject"])
        self.assertIsNone(fields["subject"]["default"])
        self.assertEqual("null", fields["tags"]["type"][0])
        self.assertEqual("array", fields["tags"]["type"][1]["type"])
        self.assertIsNone(fields["tags"]["default"])
        self.assertNotIn("default", fields["time"])

