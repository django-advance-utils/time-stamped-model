[![PyPI version](https://badge.fury.io/py/time-stamped-model.svg)](https://badge.fury.io/py/time-stamped-model)

# Time Stamped Model

This package creates adds a `created` and `modified` field to your django modals.

## To use

Add time-stamped-model to your installed apps

```
from time-stamped-model.modals import TimeStampedModel

class Foo(TimeStampedModel):
    bar = models.BooleanField(default=False)
```

## Manual set

Sometimes you want to manual set the time. This may be required if you import data from another system.

To do this you can use the functions `set_created_date` and `set_modified_date`
