from django.contrib.gis.db import models
from django.db.models import DateTimeField

__author__ = 'Tom'



class CreationDateTimeField(DateTimeField):
    """
    CreationDateTimeField
    By default, sets editable=False, blank=False, auto_now_add=True
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)
        kwargs.setdefault('blank', False)
        kwargs.setdefault('auto_now_add', True)
        DateTimeField.__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "DateTimeField"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.editable is not False:
            kwargs['editable'] = True
        if self.blank is not True:
            kwargs['blank'] = False
        if self.auto_now_add is not False:
            kwargs['auto_now_add'] = True
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        if not getattr(model_instance, 'update_created', True):
            field_data = getattr(model_instance, self.attname)
            if field_data is not None:
                return field_data
        return super().pre_save(model_instance, add)


class ModificationDateTimeField(CreationDateTimeField):
    """
    ModificationDateTimeField
    By default, sets editable=False, blank=False, auto_now=True
    Sets value to now every time the object is saved.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('auto_now', True)
        DateTimeField.__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "DateTimeField"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.auto_now is not False:
            kwargs['auto_now'] = True
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        if not getattr(model_instance, 'update_modified', True):
            field_data = getattr(model_instance, self.attname)
            if field_data is not None:
                return field_data
        return super().pre_save(model_instance, add)


class TimeStampedModel(models.Model):
    """
    An abstract base class model that
    provides self-updating 'created'
    and 'modified fields'.
    """

    def __init__(self):
        self.update_created = False
        self.update_modified = False
        super().__init__()

    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    class Meta:
        abstract = True

    def set_created_date(self, created_date):
        """
        Using this method allows one to set the created date manually. This is useful when importing data.
        """
        self.update_created = False
        self.created = created_date

    def set_modified_date(self, modified_date):
        """
        Using this method allows one to set the modified date manually. This is useful when importing data.
        """
        self.update_modified = False
        self.modified = modified_date
