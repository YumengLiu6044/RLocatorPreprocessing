import pathlib
import unittest
from compile_data import retrieve_xml_file_paths, XML_FOLDER_PATH


class MyTestCase(unittest.TestCase):
    def test_retrieved_expected_xml_files(self):
        xml_file_paths: [pathlib.Path] = retrieve_xml_file_paths(XML_FOLDER_PATH)
        expected_files = [
            'Birt.xml',
            'Eclipse_Platform_UI.xml',
            'AspectJ.xml',
            'JDT.xml',
            'SWT.xml',
            'Tomcat.xml'
        ]
            
        xml_file_names = [x.name for x in xml_file_paths]
        xml_file_names.sort()
        expected_files.sort()
        self.assertEqual(xml_file_names, expected_files)


if __name__ == '__main__':
    unittest.main()
