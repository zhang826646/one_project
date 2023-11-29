import ujson
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import inspect

base = declarative_base()


class BaseModel(base):
    __abstract__ = True

    @classmethod
    def upsert(cls, db_session, *conditions, attrs: dict, default: dict = None):
        """
        更新或新增某条数据 根据conditions条件查询 如果没有查到数据 则根据attrs插入一条数据
        如果default不为空 则再用default更新这条数据
            ```
            LeisuMember.upsert(
                db_session,
                LeisuMember.id == 3,
                attrs={'name': 'aoo', 'status': 1},
                default={'created_at': 1588241501}
            )
            ```
        :param db_session:
        :param conditions:  查询条件 [LeisuMember.name == 'aoo', LeisuMember.status == 1]
        :param attrs:  更新的键值对
        :param default:  当执行的是插入操作时 除了更新attrs以外 再更新default
        :return: 返回元祖(是否是新数据,更新的字段,model实例)
        :rtype: tuple
        """
        # 获取表所有字段名
        columns = inspect(cls).c.keys()
        _attrs = {}
        _default = {}
        # 过滤掉所有非法的key
        for c in columns:
            if attrs:
                if c in attrs:
                    _attrs[c] = attrs[c]
            if default:
                if c in default:
                    _default[c] = default[c]
        is_new = False  # 是否是新增数据
        updated_columns = []  # 更新的字段

        row = db_session.query(cls).filter(*conditions).first()
        if row:
            # 更新
            # 同步时如果是忽略字段 不更新
            locked_cols = []
            if 'locked_cols' in columns:
                locked_cols = row.locked_cols
                if locked_cols:
                    locked_cols = ujson.loads(locked_cols)
            for k, v in _attrs.items():
                if getattr(row, k) != v and k not in locked_cols:
                    setattr(row, k, v)
                    updated_columns.append(k)
        else:
            # 创建
            row = cls()
            is_new = True
            if _default:
                _attrs.update(**_default)
            for k, v in _attrs.items():
                if getattr(row, k) != v:
                    setattr(row, k, v)
                    updated_columns.append(k)
        return is_new, updated_columns, row

    def to_dict(self, *exclude):
        """
        ORM对象转字典
        :return:
        """
        return {k: getattr(self, k) for k in inspect(self.__class__).c.keys() if k not in exclude}

    def to_json(self, *exclude):
        """
        ORM对象转json字符串
        :param exclude:
        :return:
        """
        return ujson.dumps(self.to_dict(*exclude))
