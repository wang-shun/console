# coding=utf-8
from console.common import serializers
from .models import CfgRecordModel, ALL_CFG_MODELS
from .utils import get_default_field_names


class CfgRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CfgRecordModel
        fields = (
            'create_datetime',
            'ticket_id',
            'content',
            'applicant',
            'approve'
        )


# 为所有 BaseCfgModel 的子类动态创建对应的 Serializer 类
_excludes = set(['deleted', 'create_datetime', 'zone_id', 'zone', 'delete_datetime', 'instancesmodel'])
_exports = dict()
for _model in ALL_CFG_MODELS.values():
    _name = _model.__name__.replace('Model', 'Serializer')
    _fields = tuple(
        field for field in get_default_field_names(_model) if field not in _excludes
    )
    _cls = type(_name,
                (serializers.ModelSerializer,),
                {
                    '__module__': __name__,
                    'Meta': type('Meta', (), {'model': _model, 'fields': _fields})
                })
    _exports[_name] = _cls
locals().update(_exports)
