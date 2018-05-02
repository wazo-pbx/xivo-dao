# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import CheckConstraint, Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestUser(Base):

    DESTINATION_TYPE_ID = 1

    __tablename__ = 'func_key_dest_user'
    __table_args__ = (
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        CheckConstraint('destination_type_id = {}'.format(DESTINATION_TYPE_ID)),
    )

    func_key_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('userfeatures.id'), primary_key=True)
    destination_type_id = Column(Integer, primary_key=True, server_default="{}".format(DESTINATION_TYPE_ID))

    type = 'user'  # TODO improve with relationship

    func_key = relationship(FuncKey)
    userfeatures = relationship(UserFeatures)

    @classmethod
    def for_user(cls, func_key, user):
        destination = cls(func_key=func_key, userfeatures=user)
        return destination

    def to_tuple(self):
        return (('user_id', self.user_id),)
