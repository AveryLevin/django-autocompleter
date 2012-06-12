#!/usr/bin/python
# -*- coding: utf-8 -*-

from test_app.tests.base import AutocompleterTestCase
from autocompleter import Autocompleter
from autocompleter import settings as auto_settings


class MultiMatchingPerfTestCase(AutocompleterTestCase):
    fixtures = ['stock_test_data.json', 'indicator_test_data.json']

    def setUp(self):
        self.autocomp = Autocompleter("mixed")
        self.autocomp.store_all()
        super(MultiMatchingPerfTestCase, self).setUp()

    def tearDown(self):
        self.autocomp.remove_all()
        pass

    def test_repeated_matches(self):
        """
        Matching is fast
        """
        setattr(auto_settings, 'MATCH_OUT_OF_ORDER', True)

        for i in range(1, 1000):
            self.autocomp.suggest('ma')

        for i in range(1, 1000):
            self.autocomp.suggest('price consumer')

        for i in range(1, 1000):
            self.autocomp.suggest('a')

        # Must set the setting back to where it was as it will persist
        setattr(auto_settings, 'MATCH_OUT_OF_ORDER', False)
