import unittest
from unittest.mock import mock_open, patch
from assessment.gprsio import Data, Meta


class TestDataClass(unittest.TestCase):
    def test_load_data_from_valid_file(self):
        with patch(
            "builtins.open",
            mock_open(read_data="Tables: [table1, table2]\nregionslist: {}"),
        ):
            meta_instance = Meta.from_file("valid_meta.yaml")
            self.assertIsNotNone(meta_instance.data)
            self.assertEqual(meta_instance.Tables, ["table1", "table2"])

    def test_load_data_from_invalid_file(self):
        with patch("builtins.open", mock_open(read_data="invalid_yaml")):
            meta_instance = Meta.from_file("invalid_meta.yaml")
            self.assertIsNone(meta_instance.data)

    def test_load_data_from_missing_file(self):
        with patch("builtins.open", side_effect=FileNotFoundError()):
            meta_instance = Meta.from_file("missing_meta.yaml")
            self.assertIsNone(meta_instance.data)

    def test_initialize_attributes(self):
        meta_instance = Meta()
        meta_instance.data = {
            "Tables": ["table1", "table2"],
            "regionslist": {"region1": "details"},
            "Output": "output_folder",
            "Database": "example.db",
            "BACI": "some_value",
            "BACIcodes": {"code1": "desc1"},
            "COMTRADEcodes": {"code2": "desc2"},
        }
        meta_instance._initialize_attributes()

        self.assertEqual(meta_instance.Tables, ["table1", "table2"])
        self.assertEqual(meta_instance.regions_list, {"region1": "details"})
        self.assertEqual(meta_instance.Output, "output_folder")
        self.assertEqual(meta_instance.Database, "example.db")
        self.assertEqual(meta_instance.BACI, "some_value")
        self.assertEqual(meta_instance.BACIcodes, {"code1": "desc1"})
        self.assertEqual(meta_instance.COMTRADEcodes, {"code2": "desc2"})

    def test_error_loading_configuration_data(self):
        with patch("builtins.open", side_effect=Exception("An error")):
            with self.assertLogs(level="ERROR") as log_context:
                meta_instance = Meta()
            self.assertIn(
                "Error loading the configuration data.", log_context.output[0]
            )

    def setUp(self):
        # Create an instance of the Data class for testing
        self.data_instance = Data()

    def test_empty_input(self):
        # Test when no data is provided
        self.data_instance.process_inputs()
        # TODO: Add assertions to verify expected behavior for empty input

    def test_valid_inputs(self):
        # Test with valid inputs
        valid_data = {
            "Project1": {
                "year": [2002, 2005, 2010],
                "resource": ["Cobalt", "Lithium"],
                "eco_unit": ["India", "Afghanistan"],
                "recycling_rate": [0.5, 0.7],
                "sub_index": [0.1, 0.2, 0.3],
            }
        }
        self.data_instance.data = valid_data
        self.data_instance.project_name = "Project1"
        self.data_instance.process_inputs()
        # TODO: Add assertions to verify expected behavior for valid input

    def test_invalid_inputs(self):
        # Test with invalid inputs
        invalid_data = {
            "Project2": {
                "year": [2000, 2022],  # Invalid year values
                "eesource": ["Metal1", "Metal2"],  # Typo in key "eesource"
                "eco_unit": ["Region1", "Region2"],
                "recycling_rate": [1.2],  # Invalid recycling rate
                "sub_index": [0.1, "Invalid"],  # Invalid sub_index value
            }
        }
        self.data_instance.data = invalid_data
        self.data_instance.project_name = "Project2"
        with self.assertRaises(Exception) as context:
            self.data_instance.process_inputs()
        # TODO: Add assertions to verify expected behavior for invalid input

    def test_missing_project_name(self):
        # Test when project_name is not set
        invalid_data = {
            "": {
                "year": [2000, 2005],
                "resource": ["Metal1", "Metal2"],
                "eco_unit": ["Region1", "Region2"],
                "recycling_rate": [0.5, 0.7],
                "sub_index": [0.1, 0.2],
            }
        }
        self.data_instance.data = invalid_data
        with self.assertRaises(Exception) as context:
            self.data_instance.process_inputs()
        # project_name not set intentionally

        # TODO: Add assertions to verify expected behavior for missing project_name

    def test_missing_data(self):
        # Test when data is not provided
        self.data_instance.project_name = "Project3"  # Set project_name
        with self.assertRaises(Exception) as context:
            self.data_instance.process_inputs()
        # TODO: Add assertions to verify expected behavior for missing data

    def test_setfolder(self):
        # Test the setfolder method with a valid data folder path
        data_path = "Documents\geopolrisk\output"
        self.data_instance.setfolder(data_path)
        self.assertEqual(
            self.data_instance.datafolder, data_path
        )  # Check if datafolder is set correctly

    def test_write(self):
        # Test the write method
        # Create a sample data dictionary to write
        sample_data = {
            "Project4": {
                "year": [2002, 2005, 2010],
                "resource": ["Cobalt", "Lithium"],
                "eco_unit": ["India", "Afghanistan"],
                "recycling_rate": [0.5, 0.7],
                "sub_index": [0.1, 0.2, 0.3],
            }
        }
        self.data_instance.data = sample_data
        self.data_instance.project_name = "Project4"
