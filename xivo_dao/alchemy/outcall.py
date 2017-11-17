# -*- coding: utf-8 -*-
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql import func, cast, not_
from sqlalchemy.types import Integer, String, Text, Boolean

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy.outcalltrunk import OutcallTrunk
from xivo_dao.alchemy.dialpattern import DialPattern
from xivo_dao.alchemy.schedulepath import SchedulePath


class Outcall(Base):

    __tablename__ = 'outcall'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False)
    context = Column(String(39))
    internal = Column(Integer, nullable=False, server_default='0')
    preprocess_subroutine = Column(String(39))
    hangupringtime = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    dialpatterns = relationship('DialPattern',
                                primaryjoin="""and_(DialPattern.type == 'outcall',
                                                    DialPattern.typeid == Outcall.id)""",
                                foreign_keys='DialPattern.typeid',
                                cascade='all, delete-orphan',
                                back_populates='outcall')

    extensions = association_proxy('dialpatterns', 'extension')

    outcall_trunks = relationship('OutcallTrunk',
                                  order_by='OutcallTrunk.priority',
                                  collection_class=ordering_list('priority'),
                                  cascade='all, delete-orphan',
                                  back_populates='outcall')

    trunks = association_proxy('outcall_trunks', 'trunk',
                               creator=lambda _trunk: OutcallTrunk(trunk=_trunk))

    ivr_dialactions = relationship('Dialaction',
                                   primaryjoin="""and_(Dialaction.action == 'outcall',
                                                       Dialaction.actionarg1 == cast(Outcall.id, String),
                                                       Dialaction.category.in_(['ivr', 'ivr_choice']))""",
                                   foreign_keys='Dialaction.actionarg1',
                                   cascade='all, delete-orphan')

    schedule_paths = relationship('SchedulePath',
                                  primaryjoin="""and_(SchedulePath.path == 'outcall',
                                                      SchedulePath.pathid == Outcall.id)""",
                                  foreign_keys='SchedulePath.pathid',
                                  cascade='all, delete-orphan',
                                  back_populates='outcall')
    schedules = association_proxy('schedule_paths', 'schedule',
                                  creator=lambda _schedule: SchedulePath(path='outcall',
                                                                         schedule_id=_schedule.id,
                                                                         schedule=_schedule))

    @hybrid_property
    def internal_caller_id(self):
        return self.internal == 1

    @internal_caller_id.expression
    def internal_caller_id(cls):
        return cast(cls.internal, Boolean)

    @internal_caller_id.setter
    def internal_caller_id(self, value):
        self.internal = int(value == 1)

    @hybrid_property
    def ring_time(self):
        if self.hangupringtime == 0:
            return None
        return self.hangupringtime

    @ring_time.expression
    def ring_time(cls):
        return func.nullif(cls.hangupringtime, 0)

    @ring_time.setter
    def ring_time(self, value):
        if value is None:
            self.hangupringtime = 0
        else:
            self.hangupringtime = value

    @hybrid_property
    def enabled(self):
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value == 0)

    def associate_extension(self, extension, **kwargs):
        extension.type = 'outcall'
        dialpattern = DialPattern(type='outcall',
                                  exten=extension.exten,
                                  **kwargs)
        self.dialpatterns.append(dialpattern)
        index = self.dialpatterns.index(dialpattern)
        self.dialpatterns[index].extension = extension
        self._fix_context()

    def dissociate_extension(self, extension):
        self.extensions.remove(extension)
        extension.type = 'user'
        extension.typeval = '0'
        self._fix_context()

    def update_extension_association(self, extension, **kwargs):
        for dialpattern in self.dialpatterns:
            if extension == dialpattern.extension:
                dialpattern.strip_digits = kwargs.get('strip_digits', dialpattern.strip_digits)
                dialpattern.prefix = kwargs.get('prefix', dialpattern.prefix)
                dialpattern.external_prefix = kwargs.get('external_prefix', dialpattern.external_prefix)
                dialpattern.caller_id = kwargs.get('caller_id', dialpattern.caller_id)

    def _fix_context(self):
        for extension in self.extensions:
            self.context = extension.context
            return
        self.context = None
