# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, ForeignKey, ForeignKeyConstraint, CheckConstraint
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestConference(Base):

    DESTINATION_TYPE_ID = 4

    __tablename__ = 'func_key_dest_conference'
    __table_args__ = (
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        CheckConstraint('destination_type_id = {}'.format(DESTINATION_TYPE_ID)),
    )

    func_key_id = Column(Integer, primary_key=True)
    destination_type_id = Column(Integer, primary_key=True, server_default="{}".format(DESTINATION_TYPE_ID))
    conference_id = Column(Integer, ForeignKey('meetmefeatures.id'), primary_key=True)

    type = 'conference'  # TODO improve with relationship

    func_key = relationship(FuncKey)
    conference = relationship(MeetmeFeatures)

    # TODO find another way to calculate hash destination
    def to_tuple(self):
        parameters = (
            ('conference_id', self.conference_id),
        )
        return tuple(sorted(parameters))
