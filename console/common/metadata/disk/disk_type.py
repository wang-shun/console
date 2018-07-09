#!/usr/bin/env python
# coding=utf-8
from ..base import BaseMetadata


class DiskType(BaseMetadata):
    POWERVM_HMC = 'POWERVM_HMC'

    @classmethod
    def _data_map(cls):
        return {
            cls.POWERVM_HMC: 'POWERVM HMC',
        }
