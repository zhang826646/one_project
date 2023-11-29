from cerberus import Validator
from functools import wraps
from common.exceptions import InvalidRequestError
from apps import logger
import ujson
import sys


class RequestValidator(Validator):

    def __init__(self, fields, *args, **kwargs):
        self.fields = fields
        parsed_schemas = dict()
        for field in fields:
            parsed_schemas[field.name] = field.to_schema()
        super(RequestValidator, self).__init__(parsed_schemas, *args, **kwargs)

    def validate(self, data, *args, **kwargs):
        data = data or {}
        for field in self.fields:
            if field.name in data.keys():
                data[field.name] = field.to_python(data[field.name])
        return super(RequestValidator, self).validate(data, *args, **kwargs)


class Field(object):
    def __init__(self, name: str, nullable=False, required=True):
        """
        :param name: 字段名称
        :param nullable: 是否允许为null
        :param required:  是否为必需项
        """
        self.nullable = nullable
        self.required = required
        self.name = name

    def to_python(self, value):
        raise NotImplementedError

    def to_schema(self):
        raise NotImplementedError


class CharField(Field):
    def __init__(self, allow_empty: bool = True, min_length: int = None, max_length: int = None, **kwargs):
        """
        :param allow_empty: 是否允许为空字符串
        :param min_length: 字符串最小长度
        :param max_length: 字符串最大长度
        :param kwargs:
        """
        super(CharField, self).__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.allow_empty = allow_empty

    def to_python(self, value):
        return str(value) if value is not None else None

    def to_schema(self):
        schema = {'type': 'string', 'nullable': self.nullable, 'required': self.required}
        if self.min_length is not None:
            schema['minlength'] = self.min_length
        if self.max_length is not None:
            schema['maxlength'] = self.max_length
        if self.allow_empty is not None:
            schema['empty'] = self.allow_empty
        if self.required is not None:
            schema['required'] = self.required
        if self.nullable is not None:
            schema['nullable'] = self.nullable
        return schema


class IntegerField(Field):
    def __init__(self, min_value: int = None, max_value: int = None, **kwargs):
        """
        :param min_value: 最小值
        :param max_value: 最大值
        :param kwargs:
        """
        super(IntegerField, self).__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def to_python(self, value):
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            raise InvalidRequestError()

    def to_schema(self):
        schema = {'type': 'integer'}
        if self.min_value is not None:
            schema['min'] = self.min_value
        if self.max_value is not None:
            schema['max'] = self.max_value
        else:
            schema['max'] = sys.maxsize
        if self.required is not None:
            schema['required'] = self.required
        if self.nullable is not None:
            schema['nullable'] = self.nullable
        return schema


class FloatField(Field):
    def __init__(self, min_value: float = None, max_value: float = None, **kwargs):
        """
        :param min_value: 最小值
        :param max_value: 最大值
        :param kwargs:
        """
        super(FloatField, self).__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def to_python(self, value):
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            raise InvalidRequestError()

    def to_schema(self):
        schema = {'type': 'float'}
        if self.min_value is not None:
            schema['min'] = self.min_value
        if self.max_value is not None:
            schema['max'] = self.max_value
        else:
            schema['max'] = sys.maxsize
        if self.required is not None:
            schema['required'] = self.required
        if self.nullable is not None:
            schema['nullable'] = self.nullable
        return schema


class BooleanField(Field):
    def __init__(self, **kwargs):
        super(BooleanField, self).__init__(**kwargs)

    def to_python(self, value):
        try:
            return bool(value) if value is not None else None
        except (ValueError, TypeError):
            raise InvalidRequestError()

    def to_schema(self):
        schema = {'type': 'boolean'}
        if self.required is not None:
            schema['required'] = self.required
        if self.nullable is not None:
            schema['nullable'] = self.nullable
        return schema


class ListField(Field):
    def __init__(self, allow_empty: bool = True,  **kwargs):
        """
        :param allow_empty: 是否允许为空列表
        :param kwargs:
        """
        super(ListField, self).__init__(**kwargs)
        self.allow_empty = allow_empty

    def to_python(self, value):
        try:
            if isinstance(value, str):
                return ujson.loads(value)
            return list(value)
        except (ValueError, TypeError):
            raise InvalidRequestError()

    def to_schema(self):
        schema = {'type': 'list'}
        if self.allow_empty is not None:
            schema['empty'] = self.allow_empty
        if self.required is not None:
            schema['required'] = self.required
        if self.nullable is not None:
            schema['nullable'] = self.nullable
        return schema


class DictField(Field):
    def __init__(self, allow_empty: bool = True, **kwargs):
        """
        :param allow_empty: 是否允许为空字典
        :param kwargs:
        """
        super(DictField, self).__init__(**kwargs)
        self.allow_empty = allow_empty

    def to_python(self, value):
        try:
            if isinstance(value, str):
                return ujson.loads(value)
            return dict(value) if value is not None else None
        except (ValueError, TypeError):
            raise InvalidRequestError()

    def to_schema(self):
        schema = {'type': 'dict'}
        if self.allow_empty is not None:
            schema['empty'] = self.allow_empty
        if self.required is not None:
            schema['required'] = self.required
        if self.nullable is not None:
            schema['nullable'] = self.nullable
        return schema


def validate_params(*fields):
    """
    校验http请求参数，校验失败将抛出InvalidRequestError异常
    example:
        @validate_params(
            CharField(name='name', max_length=16),
            IntegerField(name='age', min_value=0, max_value=150))
        def aoo(request)
            ...

    :param fields:
    :return:
    """
    def vd(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            validator = RequestValidator(fields, allow_unknown=True)
            if 'application/x-www-form-urlencoded' in request.content_type:
                params = {}
                for k, v in request.form.items():
                    params[k] = v[0]
            else:
                if request.method == 'GET':
                    params = {}
                    for k, v in request.args.items():
                        params[k] = v[0]
                elif request.method == 'POST':
                    params = request.json
                else:
                    params = None
            try:
                valid = validator.validate(params)
            except Exception:
                raise InvalidRequestError()
            if valid:
                # 校验成功，将参数值类型转成预期类型
                request.valid_data = validator.document
                return f(request, *args, **kwargs)
            else:
                # 校验失败
                logger.error(validator.errors)
                raise InvalidRequestError()
        return wrapper
    return vd

