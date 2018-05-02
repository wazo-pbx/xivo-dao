# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKeyConstraint, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer

from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestBSFilter(Base):

    DESTINATION_TYPE_ID = 12

    __tablename__ = 'func_key_dest_bsfilter'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id', 'filtermember_id'),
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        ForeignKeyConstraint(['filtermember_id'],
                             ['callfiltermember.id']),
        CheckConstraint('destination_type_id = {}'.format(DESTINATION_TYPE_ID)),
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default="{}".format(DESTINATION_TYPE_ID))
    filtermember_id = Column(Integer, nullable=False)

    type = 'bsfilter'

    func_key = relationship(FuncKey)
    filtermember = relationship(Callfiltermember)

    def to_tuple(self):
        return (('filter_member_id', self.filtermember_id),)

    @hybrid_property
    def filter_member_id(self):
        return self.filtermember_id

    @filter_member_id.setter
    def filter_member_id(self, value):
        self.filtermember_id = value
