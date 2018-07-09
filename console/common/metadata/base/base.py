#!/usr/bin/env python
# coding=utf-8


class BaseMetadata(object):
    """
    经常有类型、状态等常量会在代码多处出现，有时图方便会写成固定的值，导致管理起来很麻烦，
    建议以后对类型、状态等常量的取值遵循以下标准，举个例子（主机类型）：

    class InstanceType(BaseMetadata):
        KVM = 'kvm'
        POWERVM = 'powerVM'
        AIX = 'AIX'

        @classmethod
        def _data_map(cls):
            return {
                cls.KVM: 'x86云主机(KVM)',
                cls.POWERVM: 'AIX云主机(powerVM)',
                cls.AIX: 'AIX物理机(AIX)',
            }

    使用场景：
    ins_obj = InstanceModel.objects.get(id='i-1234')
    if ins_obj.ins_type == InstanceType.KVM:
        ins_type_name = InstanceType(ins_obj.ins_type).name

    InstanceType.all()
    [{'pk': 'kvm', 'name': 'x86云主机(KVM)'},{'pk': 'powerVM': 'name': 'AIX云主机'}]

    ins_type = models.ChoiceField(choices=InstanceType.get_pk_list())
    ['kvm', 'powerVM', 'VMware']

    """
    __SCHEMA = ['pk', 'name']

    def __init__(self, pk=None):
        self._pk = pk
        for key in self.__SCHEMA:
            setattr(self, '_' + key, None)
        if pk is not None:
            self._fetch_name_by_pk(pk)

    def _fetch_name_by_pk(self, pk):
        _data_map = self.__class__._data_map()
        if pk in _data_map:
            self._name = _data_map.get(pk)
        else:
            raise Exception(
                'class {} does not have const {}'.format(
                    self.__class__.__name__, self._pk))

    @classmethod
    def _data_map(self):
        raise NotImplementedError(
            'class {} must implement the _data_map() method'.format(
                self.__name__))

    @property
    def pk(self):
        if self.pk is None:
            raise Exception('需要初始化具体的primary key值')
        return self._pk

    @property
    def name(self):
        if self.pk is None:
            raise Exception('需要初始化具体的primary key值')
        return self._name

    @classmethod
    def get_pk_list(cls):
        return cls._data_map().keys()

    @classmethod
    def get_value_list(cls):
        return cls._data_map().values()

    @classmethod
    def all(cls):
        return cls._data_map()
