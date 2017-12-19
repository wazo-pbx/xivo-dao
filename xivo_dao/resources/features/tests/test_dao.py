# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    none,
)

from xivo_dao.alchemy.features import Features
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as features_dao


class TestFindAll(DAOTestCase):

    def test_find_all_no_features_general(self):
        result = features_dao.find_all('general')

        assert_that(result, empty())

    def test_find_all(self):
        row1 = self.add_features(var_metric=3,
                                 var_name='setting1',
                                 var_val='value1')
        row2 = self.add_features(var_metric=2,
                                 var_name='setting2',
                                 var_val='value1')
        row3 = self.add_features(var_metric=1,
                                 var_name='setting3',
                                 var_val='value1')
        row4 = self.add_features(var_metric=4,
                                 var_name='setting2',
                                 var_val='value2')

        features = features_dao.find_all('general')

        assert_that(features, contains(row3, row2, row1, row4))

    def test_find_all_do_not_find_var_val_none(self):
        self.add_features(var_name='setting1',
                          var_val=None)
        row2 = self.add_features(var_name='setting1',
                                 var_val='value1')

        features = features_dao.find_all('general')

        assert_that(features, contains_inanyorder(row2))

    def test_find_all_do_not_find_other_section(self):
        self.add_features(category='not_general')
        row2 = self.add_features(var_name='setting1',
                                 var_val='value1')

        features = features_dao.find_all('general')

        assert_that(features, contains_inanyorder(row2))

    def test_find_all_do_not_find_parking_options(self):
        self.add_features(category='general', var_name='parkext', var_val='value1')
        self.add_features(category='general', var_name='parkeddynamic', var_val='value2')
        self.add_features(category='general', var_name='context', var_val='value3')

        features = features_dao.find_all('general')

        assert_that(features, empty())


class TestEditAll(DAOTestCase):

    def test_edit_all(self):
        row1 = Features(var_name='setting1', var_val='value1', category='general')
        row2 = Features(var_name='setting2', var_val='value1', category='general')
        row3 = Features(var_name='setting3', var_val='value1', category='general')
        row4 = Features(var_name='setting4', var_val='value1', category='general')

        features_dao.edit_all('general', [row1, row2, row3, row4])

        features = features_dao.find_all('general')
        assert_that(features, contains_inanyorder(row1, row2, row3, row4))

    def test_delete_old_entries(self):
        self.add_features()
        self.add_features()
        row = Features(var_name='nat', var_val='value1', category='general')

        features_dao.edit_all('general', [row])

        features = features_dao.find_all('general')
        assert_that(features, contains_inanyorder(row))


class TestFindParkPositionRange(DAOTestCase):

    def test_given_parking_is_disabled_then_returns_nothing(self):
        self.add_features(var_name='parkpos',
                          var_val='701-750',
                          commented=1)

        result = features_dao.find_park_position_range()

        assert_that(result, none())

    def test_given_parking_is_enabled_then_returns_range(self):
        self.add_features(var_name='parkpos',
                          var_val='701-750')

        expected = (701, 750)

        result = features_dao.find_park_position_range()

        assert_that(result, equal_to(expected))


class TestGetValue(DAOTestCase):

    def test_when_getting_feature_by_id_then_returns_value(self):
        self.add_features(id=12,
                          var_name='parkext',
                          var_val='700')

        result = features_dao.get_value(12)

        assert_that(result, equal_to('700'))

    def test_given_no_features_then_raises_error(self):
        self.assertRaises(NotFoundError, features_dao.get_value, 12)
