import info_api
import unittest

class TestSparql(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        TestSparql.db_content = info_api.get_db('rdf')

    @classmethod
    def teardown_class(cls):
        info_api.update_db(TestSparql.db_content, 'rdf')

    def test_info_for_contact(self):
        """Get the contact information for a certain contact, given the full name of the contact
        and only expecting an exact match of that name."""

        result = info_api.get_info_for_contact('Hildur Hallsdóttir')
        self.assertEqual(1, len(result))
        self.assertEqual('hildur@andabaer.is',
                         result[0].email)

    def test_info_for_contact_first_name(self):
        """Get the contact information for a certain contact, given the full name of the contact
        and only expecting an exact match of that name."""

        result = info_api.get_info_for_contact('Hildur')
        self.assertEqual(1, len(result))
        self.assertEqual('hildur@andabaer.is',
                         result[0].email)

    def test_info_for_contact_two_first_names(self):
        """Get the contact information for a certain contact, given two first names of the contact."""

        result = info_api.get_info_for_contact('Anna Jóna')
        self.assertEqual(1, len(result))
        self.assertEqual('anna.jona@andabaer.is',
                         result[0].email)

    def test_info_for_contact_first_name_of_two(self):
        """Get the contact information for a certain contact, given the first name of the contact
        even if the contact has more than one first names."""

        result = info_api.get_info_for_contact('Anna')
        self.assertEqual(1, len(result))
        self.assertEqual('anna.jona@andabaer.is',
                         result[0].email)

    def test_info_for_contact_missing_middle_name(self):
        """Get the contact information for a certain contact, given the first of two first names and the
        family name. Example: 'Anna Árnadóttir' should find 'Anna Jóna Árnadóttir'"""

        result = info_api.get_info_for_contact('Anna Árnadóttir')
        self.assertEqual(1, len(result))
        self.assertEqual('anna.jona@andabaer.is',
                         result[0].email)

    def test_info_for_contact_abbreviated_names(self):
        """Get the contact information for a certain contact, given the first of two first names and the
        family name. Example: 'Anna J Árnadóttir' should find 'Anna Jóna Árnadóttir'"""

        result = info_api.get_info_for_contact('Anna J. Árnadóttir')
        self.assertEqual(1, len(result))
        self.assertEqual('anna.jona@andabaer.is',
                         result[0].email)

        result = info_api.get_info_for_contact('Anna J Árnad')
        self.assertEqual(1, len(result))
        self.assertEqual('anna.jona@andabaer.is',
                         result[0].email)

    def test_info_for_contact_not_full_name(self):
        """When 'contact' is not a complete name (first name(s) or a full name)
        the query should not return any results."""

        result = info_api.get_info_for_contact('Guðm')
        self.assertEqual(0, len(result))

    def test_contact_from_subject(self):
        result = info_api.get_contact_from_subject('Velferðarmál')
        self.assertEqual(1, len(result))
        self.assertEqual('María Jóhannsdóttir',
                         result[0].name)
        self.assertEqual('maria.johannsdottir@andabaer.is',
                         result[0].email)

    def test_name_from_title(self):
        result = info_api.get_name_for_title('bæjarstjóri')
        self.assertEqual('Jón Sigurðsson', result[0].name)

    def test_name_from_title_fuzzy(self):
        result = info_api.get_name_for_title('gjaldkeri')
        self.assertEqual('Ingibjörg Stefánsdóttir', result[0].name)

    def test_valid_roles(self):
        result = info_api.get_valid_subjects()
        self.assertTrue(len(result) > 3)
        found_subject = False
        for res in result:
            if str(res) == 'Skólamál':
                found_subject = True
        self.assertTrue(found_subject)

    def test_get_office_contact_info(self):
        result = info_api.get_office_contact_info()
        self.assertTrue(len(result) == 1)
        self.assertEqual('499 1000', result[0].phone)
        self.assertEqual('andabaer@andabaer.is', result[0].email)

    def test_download_db(self):
        """Download the Fuseki db and see if we can retrieve it with all supported formats
        but not with unknown formats."""

        # Valid formats
        for fmt in info_api.CONTENT_TYPES:
            db = info_api.get_db(fmt)
            self.assertTrue(len(db) > 1)

        # Invalid formats
        invalid_formats = ['text/plain', 'application/zip', 'application/x-turtle']
        for fmt in invalid_formats:
            # Should raise an exception
            with self.assertRaises(Exception):
                db = info_api.get_db(fmt)

    def test_update_db(self):
        """ Test updating db """
        data_type = "turtle"
        db = info_api.get_db(data_type)
        self.assertTrue(len(db) > 1)

        # update db with some dummy data, this will erase everything in the db,
        # but make sure that we have saved the data beforehand and restore it here
        # and in the teardown() method of the test class
        data_string = """
        @prefix ex: <http://example.org/> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

        ex:subject1 rdf:type ex:Class1 .
        ex:subject1 ex:property1 "Value1" .
        """

        info_api.update_db(data_string, data_type)
        db_new = info_api.get_db(data_type)
        self.assertTrue(len(db_new) < len(db))

        # restore db with original data
        info_api.update_db(db, data_type)

if __name__ == '__main__':
    unittest.main()