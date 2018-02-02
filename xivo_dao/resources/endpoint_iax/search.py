# -*- coding: UTF-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=UserIAX,
                      columns={'name': UserIAX.name,
                               'type': UserIAX.type,
                               'host': UserIAX.host},
                      default_sort='name')

iax_search = SearchSystem(config)