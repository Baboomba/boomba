import polars as pl
from boomba.core.dtypes import Dtype
from boomba.core.schema import Schema


def test_schema():
    expected_schema = [
        ('int8', pl.Int8),
        ('int16', pl.Int16),
        ('int32', pl.Int32),
        ('int64', pl.Int64),
        ('uint8', pl.UInt8),
        ('uint16', pl.UInt16),
        ('uint32', pl.UInt32),
        ('uint64', pl.UInt64),
        ('float32', pl.Float32),
        ('float64', pl.Float64),
        ('string', pl.String),
        ('boolean', pl.Boolean),
        ('date_', pl.Date),
        ('time_', pl.Time),
        ('datetime_', pl.Datetime),
        ('decimal', pl.Decimal),
    ]
    
    class TestSchema(Schema):
        int8 = Dtype.Int8()
        int16 = Dtype.Int16()
        int32 = Dtype.Int32()
        int64 = Dtype.Int64()
        uint8 = Dtype.UInt8()
        uint16 = Dtype.UInt16()
        uint32 = Dtype.UInt32()
        uint64 = Dtype.UInt64()
        float32 = Dtype.Float32()
        float64 = Dtype.Float64()
        string = Dtype.String()
        boolean = Dtype.Boolean()
        date_ = Dtype.Date()
        time_ = Dtype.Time()
        datetime_ = Dtype.Datetime()
        decimal = Dtype.Decimal(10, 2)
    
    assert list(TestSchema().schema.items()) == expected_schema