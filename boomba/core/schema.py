import inspect

import polars as pl

from boomba.core.dtypes import _Dtypes


class _MetaSchema(type):
    '''
    A metaclass that automatically generates a PyArrow schema from the attributes 
    of a class that are instances of _Dtypes.

    This metaclass will scan the class attributes and check if any of them 
    are instances of the _Dtypes class or its subclasses. If so, the corresponding
    PyArrow data type will be used to build a schema that is assigned to the 
    class as the schema attribute.

    Attributes:
        name (str): The name of the class being created.
        bases (tuple): A tuple of base classes of the class being created.
        dct (dict): A dictionary of class attributes.
    
    Returns:
        type: The class being created, with the added `schema` attribute.
    '''
    def __new__(cls, name, bases, dct):
        schema = []
        
        if bases:
            for k, v in dct.items():
                if k.startswith('__') and k.endswith('__'):
                    continue
                
                for base in bases:
                    if hasattr(base, k):
                        continue
                
                if inspect.isfunction(v):
                    continue
                
                if isinstance(v, _Dtypes):
                    schema.append((k, v.dtype))
                else:
                    raise TypeError(
                        f"Invalid attribute '{k}': Expected instance of "
                        f"_Dtypes, got {type(v).__name__}."
                    )
        
        dct['schema'] = pl.Schema(schema)
        return super().__new__(cls, name, bases, dct)


class Schema(metaclass=_MetaSchema):
    '''
    A base class that uses BuilderMeta as its metaclass. 

    Classes inheriting from BaseBuilder should define their attributes as instances 
    of subclasses of _Dtypes, which will automatically be used to generate the 
    PyArrow schema.

    Example:
        class CustomSchema(Schema):
            name = String()
            age = Int32()
    
    In this example, a PyArrow schema will be automatically generated for the 
    'name' and 'age' attributes.
    '''
    pass