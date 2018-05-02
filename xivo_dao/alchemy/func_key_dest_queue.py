# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, ForeignKey, ForeignKeyConstraint, CheckConstraint
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestQueue(Base):

    DESTINATION_TYPE_ID = 3

    __tablename__ = 'func_key_dest_queue'
    __table_args__ = (
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        CheckConstraint('destination_type_id = {}'.format(DESTINATION_TYPE_ID)),
    )

    func_key_id = Column(Integer, primary_key=True)
    destination_type_id = Column(Integer, primary_key=True, server_default="{}".format(DESTINATION_TYPE_ID))
    queue_id = Column(Integer, ForeignKey('queuefeatures.id'), primary_key=True)

    type = 'queue'  # TODO improve with relationship

    func_key = relationship(FuncKey)
    queue = relationship(QueueFeatures)

    # TODO find another way to calculate hash destination
    def to_tuple(self):
        parameters = (
            ('queue_id', self.queue_id),
        )
        return tuple(sorted(parameters))
