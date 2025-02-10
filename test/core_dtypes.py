import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime
import unittest
import polars as pl
from boomba.core.dtypes import Dtype

class TestDtypes(unittest.TestCase):

    def test_int8(self):
        dtype_instance = Dtype.Int8()
        data = pl.DataFrame({"value": [1, 2, 3]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Int8)

    def test_int16(self):
        dtype_instance = Dtype.Int16()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Int16)
        
    def test_int32(self):
        dtype_instance = Dtype.Int32()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Int32)
    
    def test_int64(self):
        dtype_instance = Dtype.Int64()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Int64)

    def test_uint8(self):
        dtype_instance = Dtype.UInt8()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.UInt8)
        
    def test_uint8(self):
        dtype_instance = Dtype.UInt8()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.UInt8)
    
    def test_int8(self):
        dtype_instance = Dtype.Int8()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Int8)

    def test_int16(self):
        dtype_instance = Dtype.Int16()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Int16)

    def test_int32(self):
        dtype_instance = Dtype.Int32()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Int32)

    def test_int64(self):
        dtype_instance = Dtype.Int64()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Int64)

    def test_uint8(self):
        dtype_instance = Dtype.UInt8()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.UInt8)

    def test_uint16(self):
        dtype_instance = Dtype.UInt16()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.UInt16)

    def test_uint32(self):
        dtype_instance = Dtype.UInt32()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.UInt32)

    def test_uint64(self):
        dtype_instance = Dtype.UInt64()
        data = pl.DataFrame({"value": [10, 20, 30]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.UInt64)

    def test_float32(self):
        dtype_instance = Dtype.Float32()
        data = pl.DataFrame({"value": [10.5, 20.5, 30.5]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Float32)

    def test_float64(self):
        dtype_instance = Dtype.Float64()
        data = pl.DataFrame({"value": [10.5, 20.5, 30.5]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Float64)

    def test_string(self):
        dtype_instance = Dtype.String()
        data = pl.DataFrame({"value": ["a", "b", "c"]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Utf8)

    def test_boolean(self):
        dtype_instance = Dtype.Boolean()
        data = pl.DataFrame({"value": [True, False, True]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Boolean)

    def test_date(self):
        dtype_instance = Dtype.Date()
        data = pl.DataFrame({"value": ["2022-01-01", "2022-02-01", "2022-03-01"]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Date)

    def test_time(self):
        dtype_instance = Dtype.Time()
        time_data = [
            datetime.strptime(t, "%H:%M:%S").time() for t in ["12:00:00", "14:30:00", "16:45:00"]
        ]
        data = pl.DataFrame({"value": time_data}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Time)

    def test_datetime_millisecond(self):
        dtype_instance = Dtype.Datetime('ms')
        data = pl.DataFrame({
            "value": [
                datetime(2022, 1, 1, 12, 0, 0),
                datetime(2022, 2, 1, 14, 30, 0),
                datetime(2022, 3, 1, 16, 45, 0)
            ]
        }, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Datetime(time_unit='ms'))

    def test_datetime_microsecond(self):
        dtype_instance = Dtype.Datetime('us')
        data = pl.DataFrame({
            "value": [
                datetime(2022, 1, 1, 12, 0, 0),
                datetime(2022, 2, 1, 14, 30, 0),
                datetime(2022, 3, 1, 16, 45, 0)
            ]
        }, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Datetime(time_unit="us"))

    def test_datetime_nanosecond(self):
        dtype_instance = Dtype.Datetime('ns')
        data = pl.DataFrame({
            "value": [
                datetime(2022, 1, 1, 12, 0, 0),
                datetime(2022, 2, 1, 14, 30, 0),
                datetime(2022, 3, 1, 16, 45, 0)
            ]
        }, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Datetime(time_unit="ns"))

    def test_decimal(self):
        dtype_instance = Dtype.Decimal(precision=10, scale=2)
        data = pl.DataFrame({"value": [10.5, 20.5, 30.5]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.Decimal(10, 2))

    def test_list(self):
        '''
        dtype_instance = Dtype.List(Dtype.Int8())
        data = pl.DataFrame({"value": [[10, 20], [30, 40], [50, 60]]}, schema=[("value", dtype_instance.dtype)])
        self.assertEqual(data["value"].dtype, pl.List(pl.Int8))
        '''
        ...

    def test_struct(self):
        '''
        dtype_instance = Dtype.Struct({"field1": Dtype.Int8(), "field2": Dtype.Boolean()})
        data = pl.DataFrame({"field1": [10, 20, 30], "field2": [True, False, True]}, schema=[("field1", dtype_instance.dtype), ("field2", dtype_instance.dtype)])
        self.assertEqual(data["field1"].dtype, pl.Int8)
        self.assertEqual(data["field2"].dtype, pl.Boolean)
        '''
        ...