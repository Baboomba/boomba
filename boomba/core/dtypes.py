from abc import ABC, abstractmethod
from typing import Union
import polars as pl
import pyarrow as pa

__all__ = ['Dtype']

class _Dtypes(ABC):
    @property
    @abstractmethod
    def dtype(self) -> Union[pa.DataType, pl.DataType]:
        pass

# Datatypes for Polars
class Dtype:
    
    class Int8(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.Int8
        
    class Int16(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.Int16

    class Int32(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.Int32

    class Int64(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.Int64

    class UInt8(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.UInt8

    class UInt16(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.UInt16

    class UInt32(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.UInt32

    class UInt64(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.UInt64

    class Float32(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.Float32

    class Float64(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.Float64

    class String(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.Utf8

    class Boolean(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.Boolean

    class Date(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.Date

    class Time(_Dtypes):
        @property
        def dtype(self) -> pl.DataType:
            return pl.Time

    class Datetime(_Dtypes):
        '''
        Data type representing a calendar date and time of day.
        
        Parameters
        ---
        time_unit : {'us', 'ns', 'ms'}
            Unit of time. Defaults to 'ms' (milliseconds).
        '''
        def __init__(self, time_unit: str='ms') -> None:
            self.time_unit = time_unit
        
        @property
        def dtype(self) -> pl.DataType:
            return pl.Datetime(self.time_unit)

    class Decimal(_Dtypes):
        def __init__(self, precision: int, scale: int) -> None:
            self.precision = precision
            self.scale = scale

        @property
        def dtype(self) -> pl.DataType:
            return pl.Decimal(self.precision, self.scale)

    class __List(_Dtypes):
        def __init__(self, dtype: _Dtypes) -> None:
            self._dtype = dtype

        @property
        def dtype(self) -> pl.DataType:
            return pl.List(self._dtype.dtype)

    class __Struct(_Dtypes):
        def __init__(self, fields: dict) -> None:
            self.fields = fields

        @property
        def dtype(self) -> pl.DataType:
            return pl.Struct([(k, v.dtype) for k, v in self.fields.items()])


# Datatypes for Arrow
class _ArrowDtypes:

    class Int8(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.int8()

    class Int16(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.int16()

    class Int32(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.int32()

    class Int64(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.int64()

    class UInt8(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.uint8()

    class UInt16(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.uint16()

    class UInt32(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.uint32()

    class UInt64(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.uint64()

    class Float16(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.float16()

    class Float32(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.float32()

    class Float64(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.float64()

    class Boolean(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.bool_()

    class String(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.string()

    class Binary(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.binary()

    class LargeString(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.large_string()

    class LargeBinary(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.large_binary()

    class Date32(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.date32()

    class Date64(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.date64()

    class Timestamp(_Dtypes):
        def __init__(self, unit="ns", tz=None):
            self.unit = unit
            self.tz = tz

        @property
        def dtype(self) -> pa.DataType:
            return pa.timestamp(self.unit, self.tz)

    class Time32(_Dtypes):
        def __init__(self, unit="s"):
            self.unit = unit

        @property
        def dtype(self) -> pa.DataType:
            return pa.time32(self.unit)

    class Time64(_Dtypes):
        def __init__(self, unit="ns"):
            self.unit = unit

        @property
        def dtype(self) -> pa.DataType:
            return pa.time64(self.unit)

    class Decimal128(_Dtypes):
        def __init__(self, precision, scale):
            self.precision = precision
            self.scale = scale

        @property
        def dtype(self) -> pa.DataType:
            return pa.decimal128(self.precision, self.scale)

    class Decimal256(_Dtypes):
        def __init__(self, precision, scale):
            self.precision = precision
            self.scale = scale

        @property
        def dtype(self) -> pa.DataType:
            return pa.decimal256(self.precision, self.scale)

    class ListType(_Dtypes):
        def __init__(self, value_type):
            self.value_type = value_type

        @property
        def dtype(self) -> pa.DataType:
            return pa.list_(self.value_type)

    class LargeListType(_Dtypes):
        def __init__(self, value_type):
            self.value_type = value_type

        @property
        def dtype(self) -> pa.DataType:
            return pa.large_list(self.value_type)

    class MapType(_Dtypes):
        def __init__(self, key_type, item_type):
            self.key_type = key_type
            self.item_type = item_type

        @property
        def dtype(self) -> pa.DataType:
            return pa.map_(self.key_type, self.item_type)

    class StructType(_Dtypes):
        def __init__(self, fields):
            self.fields = fields

        @property
        def dtype(self) -> pa.DataType:
            return pa.struct(self.fields)

    class NullType(_Dtypes):
        @property
        def dtype(self) -> pa.DataType:
            return pa.null()