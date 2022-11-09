from django.test import TestCase
from autocompleter import Autocompleter
from autocompleter.utils import get_normalized_term
from autocompleter.views import SuggestView


class TestFacetHash(TestCase):
    def test_facet_identity_hash(self):
        """
        Hashing a facet should equal the hash of an earlier call
        """
        facets = [{"type": "or", "facets": [{"key": "sector", "value": "Technology"}]}]
        first_hash = Autocompleter.hash_facets(facets)
        second_hash = Autocompleter.hash_facets(facets)
        self.assertEqual(first_hash, second_hash)

    def test_hashing_facet_type(self):
        """
        Facet list with same sub facets but different type should not have equal hashes
        """
        and_facet = [
            {"type": "and", "facets": [{"key": "sector", "value": "Technology"}]}
        ]

        or_facet = [
            {"type": "or", "facets": [{"key": "sector", "value": "Technology"}]}
        ]
        and_hash = Autocompleter.hash_facets(and_facet)
        or_hash = Autocompleter.hash_facets(or_facet)
        self.assertNotEqual(and_hash, or_hash)

    def test_hashing_order(self):
        """
        Facets with identical key/values in different order should still have same hash
        """
        facet_1 = [
            {
                "type": "or",
                "facets": [
                    {"key": "sector", "value": "Technology"},
                    {"value": "Software", "key": "industry"},
                ],
            }
        ]

        facet_2 = [
            {
                "type": "or",
                "facets": [
                    {"key": "industry", "value": "Software"},
                    {"key": "sector", "value": "Technology"},
                ],
            }
        ]

        facet_1_hash = Autocompleter.hash_facets(facet_1)
        facet_2_hash = Autocompleter.hash_facets(facet_2)
        self.assertEqual(facet_1_hash, facet_2_hash)

    def test_hash_identical_values_different_facet_type(self):
        """
        Facets with same key/values but different facet type in different order shouldn't have same hash
        """
        facet_1 = [
            {
                "type": "and",
                "facets": [
                    {"key": "sector", "value": "Technology"},
                    {"key": "industry", "value": "Software"},
                ],
            }
        ]

        facet_2 = [
            {
                "type": "or",
                "facets": [
                    {"key": "industry", "value": "Software"},
                    {"key": "sector", "value": "Technology"},
                ],
            }
        ]

        facet_1_hash = Autocompleter.hash_facets(facet_1)
        facet_2_hash = Autocompleter.hash_facets(facet_2)
        self.assertNotEqual(facet_1_hash, facet_2_hash)

    def test_multiple_facets_hashing_order(self):
        """
        A facet list with multiple facets should have same hash when key/values are identical regardless of order
        """
        facet_1 = [
            {
                "type": "or",
                "facets": [
                    {"value": "Technology", "key": "sector"},
                    {"value": "Software", "key": "industry"},
                ],
            },
            {
                "type": "and",
                "facets": [
                    {"key": "sector", "value": "Energy"},
                    {"key": "industry", "value": "Oil & Gas Integrated"},
                ],
            },
        ]

        facet_2 = [
            {
                "type": "and",
                "facets": [
                    {"key": "industry", "value": "Oil & Gas Integrated"},
                    {"key": "sector", "value": "Energy"},
                ],
            },
            {
                "type": "or",
                "facets": [
                    {"value": "Technology", "key": "sector"},
                    {"key": "industry", "value": "Software"},
                ],
            },
        ]

        facet_1_hash = Autocompleter.hash_facets(facet_1)
        facet_2_hash = Autocompleter.hash_facets(facet_2)
        self.assertEqual(facet_1_hash, facet_2_hash)


class TestFacetValidation(TestCase):
    def test_valid_facet(self):
        """
        A valid facet should pass validation
        """
        facets = [
            {
                "type": "or",
                "facets": [
                    {"key": "sector", "value": "Financial Services"},
                    {"key": "industry", "value": "Investment"},
                ],
            },
            {
                "type": "or",
                "facets": [
                    {"key": "sector", "value": "Technology"},
                    {"key": "industry", "value": "Software"},
                ],
            },
        ]

        self.assertTrue(SuggestView.validate_facets(facets))

    def test_invalid_facet_no_type(self):
        """
        Facet without a type should fail validation
        """
        no_type_facets = [{"facets": [{"key": "sector", "value": "Technology"}]}]

        self.assertFalse(SuggestView.validate_facets(no_type_facets))

    def test_invalid_facet_wrong_type(self):
        """
        Facet without an invalid type should fail validation
        """
        wrong_type_facets = [
            {"type": "blah", "facets": [{"key": "sector", "value": "Technology"}]}
        ]

        self.assertFalse(SuggestView.validate_facets(wrong_type_facets))

    def test_invalid_facet_no_sub_facets(self):
        """
        Facet without a sub facet should fail validation
        """
        no_sub_facets = [
            {
                "type": "or",
            }
        ]

        self.assertFalse(SuggestView.validate_facets(no_sub_facets))

        empty_sub_facets = [{"type": "or", "facets": []}]

        self.assertFalse(SuggestView.validate_facets(empty_sub_facets))

    def test_invalid_facet_no_key(self):
        """
        Facet with no key in the sub facet should fail validation
        """
        no_key_in_sub_facet = [{"type": "or", "facets": [{"value": "Technology"}]}]

        self.assertFalse(SuggestView.validate_facets(no_key_in_sub_facet))

    def test_invalid_facet_no_value(self):
        """
        Facet with no value in the sub facet should fail validation
        """
        no_value_in_sub_facet = [{"type": "or", "facets": [{"key": "Sector"}]}]

        self.assertFalse(SuggestView.validate_facets(no_value_in_sub_facet))


class TestNormalizeRounding(TestCase):
    def test_rounding_half(self):
        """
        Rounding a number that ends in .5 should produce a number with a greater absolute value
        """
        self.assertEqual(1, Autocompleter.normalize_rounding(0.5))
        self.assertEqual(2, Autocompleter.normalize_rounding(1.5))
        self.assertEqual(-1, Autocompleter.normalize_rounding(-0.5))
        self.assertEqual(-2, Autocompleter.normalize_rounding(-1.5))

    def test_rounding_works_correctly(self):
        """
        Rounding works correctly
        """
        self.assertEqual(1, Autocompleter.normalize_rounding(0.51))
        self.assertEqual(0, Autocompleter.normalize_rounding(0.49))
        self.assertEqual(-1, Autocompleter.normalize_rounding(-0.51))
        self.assertEqual(0, Autocompleter.normalize_rounding(-0.49))
        self.assertEqual(1, Autocompleter.normalize_rounding(1))

    def test_non_int(self):
        """
        Rounding a non-integer results in ValueError
        """
        with self.assertRaises(ValueError):
            Autocompleter.normalize_rounding(None)


class TestNormalizedTerm(TestCase):
    def test_byte_string(self):
        self.assertEqual("us gdp", get_normalized_term(b"US GDP"))

    def test_replace_characters(self):
        self.assertEqual(
            "us and china", get_normalized_term("US & [CHiNA]", replaced_chars=[])
        )
        self.assertEqual(
            "percent change",
            get_normalized_term("Non Percent Change", replaced_chars=["non"]),
        )
        self.assertEqual(
            "cent change",
            get_normalized_term("Non Percent Change", replaced_chars=["non", "per"]),
        )
