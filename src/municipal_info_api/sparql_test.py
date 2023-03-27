import unittest

import info_api


class TestSparql(unittest.TestCase):

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

    def test_get_general_waste_bin_collection_info(self):
        result = info_api.get_general_waste_bin_collection_info()
        self.assertTrue(len(result) == 2)
        self.assertTrue(hasattr(result[0], "place"))

    def test_get_waste_bin_collection_info(self):
        result = info_api.get_waste_bin_collection_info('holtið')
        self.assertTrue(hasattr(result[0], "start_time"))


if __name__ == '__main__':
    unittest.main()