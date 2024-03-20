import uuid

from django.db.models import DateTimeField, Model, Max
from django.utils.text import slugify

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


class TimeStampedModel(Model):
    """
    An abstract base class model that
    provides self-updating 'created'
    and 'modified fields'.
    """

    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    class Meta:
        abstract = True

    def set_created_date(self, created_date):
        """
        Using this method allows one to set the created date manually. This is useful when importing data.
        """
        # noinspection PyAttributeOutsideInit
        self.update_created = False
        self.created = created_date

    def set_modified_date(self, modified_date):
        """
        Using this method allows one to set the modified date manually. This is useful when importing data.
        """
        # noinspection PyAttributeOutsideInit
        self.update_modified = False
        self.modified = modified_date

    def make_new_slug(self, obj=None, name=None, on_edit=False, allow_dashes=True, extra_filters=None,
                      exclude_list=None, on_blank=False, slug_field_name='slug'):
        """
        This allows you to populate a slug field. You need to call this function from model save. Only works if you add
        slug = models.SlugField(unique=True)
        on the model

        Then add
        def save(self, *args, **kwargs):
            self.make_new_slug()
            super().save(*args, **kwargs)

        :param obj: The class name can be none, and it will sort itself out
        :param name: The field to make the slug from
        :param on_edit: Whether to update the slug on edit
        :param allow_dashes: Whether dashes are allowed in the slug
        :param extra_filters: This allows for unique together
        :param exclude_list: Exclude certain slugs
        :param on_blank: Updates the slug if blank or null
        :param slug_field_name: The name of the slug field on the object
        """
        if obj is None:
            obj = self.__class__

        if extra_filters is None:
            extra_filters = {}

        if name is None:
            name = getattr(self, 'name', '')  # Fallback to an empty string if 'name' attribute doesn't exist

        current_slug = getattr(self, slug_field_name, '')

        if not self.pk and (current_slug is None or current_slug == ''):
            main_slug = slugify(name)[:45]  # limits the slug to 45 chars as slug use 50

            if main_slug == '':
                main_slug = str(uuid.uuid4())
            if not allow_dashes:
                main_slug = main_slug.replace('-', '_')
            slug = main_slug
            count = 1

            # This loop checks for existence in the database considering extra_filters
            while obj.objects.filter(**{slug_field_name: slug}, **extra_filters).exists() or slug in exclude_list:
                slug = f'{main_slug}{count}'
                if not allow_dashes:
                    slug = slug.replace('-', '_')
                count += 1

                # Check and increment if slug is in exclude_list
                while slug in exclude_list:
                    slug = f'{main_slug}{count}'
                    count += 1

                # After adjusting for exclude_list, re-check for unique slug avoiding infinite loop
                if not obj.objects.filter(**{slug_field_name: slug}, **extra_filters).exists():
                    break

            setattr(self, slug_field_name, slug)

        elif self.pk and (on_edit or (on_blank and (current_slug is None or current_slug == ''))):
            main_slug = slugify(name)[:45]
            if not allow_dashes:
                main_slug = main_slug.replace('-', '_')
            slug = main_slug
            count = 1

            # Similar check for when on_edit or on_blank conditions are met
            while obj.objects.filter(**{slug_field_name: slug}, **extra_filters).exclude(
                    pk=self.pk).exists() or slug in exclude_list:
                slug = f'{main_slug}{count}'
                if not allow_dashes:
                    slug = slug.replace('-', '_')
                count += 1

                # Again, check and increment if slug is in exclude_list
                while slug in exclude_list:
                    slug = f'{main_slug}{count}'
                    count += 1

                # Check for unique slug after adjustments
                if not obj.objects.filter(**{slug_field_name: slug}, **extra_filters).exclude(pk=self.pk).exists():
                    break

            setattr(self, slug_field_name, slug)

    def set_order_field(self, obj=None, extra_filters=None, order_field='order'):
        """
        Sets the order for a model instance based on the specified ordering field.

        Parameters:
        - obj (Model, optional): The model class to which the order field applies.
          Defaults to the class of the current instance.
        - extra_filters (dict, optional): Additional filters to apply when determining the order.
          Useful for nested or related models.
        - order_field (str): The field used to determine the order. Default is 'order'.

        Usage:
        - Add an 'order' field to your model: order = models.PositiveSmallIntegerField().
        - Override the save method and include set_order_field:

          def save(self, *args, **kwargs):
              self.set_order_field()
              super().save(*args, **kwargs)

        - For subqueries or related models, use extra_filters:

          self.set_order_field(extra_filters={'base': self.base})

        This method calculates the next available order number by finding the maximum value of the order
        field and incrementing it. If no records are found, it starts from 1.
        """

        if obj is None:
            obj = self.__class__
        order = getattr(self, order_field)
        if order is None:
            if extra_filters is None:
                extra_filters = {}
            order = obj.objects.filter(**extra_filters).aggregate(Max(order_field))[f'{order_field}__max']
            if order is None:
                order = 1
            else:
                order += 1
            setattr(self, order_field, order)

    def set_instance_type(self, instance_type_field='instance_type'):
        """
        Sets the type of an instance for a Django model.

        This method automatically assigns a value to a field in the model that indicates the type of the instance.
        It is especially useful in inheritance scenarios, where a base model is extended by several child models and
        there's a need to identify the type of each instance.

        Parameters:
        - instance_type_field (str): The field name in the model that will store the instance type.
          Defaults to 'instance_type'.

        Usage:
        - Implement this method in the model's save method to automatically set the instance
          type before the instance is saved:

          def save(self, *args, **kwargs):
              self.set_instance_type()
              super().save(*args, **kwargs)

        The method first tries to set the 'instance_type_field' with its current value. If this field is None,
        it derives the model's class name from the '_meta.label_lower' attribute, formatted as 'app_label.model_name',
        and uses the model name part as the instance type. This approach is particularly helpful in models using
        abstract base classes or Django's multi-table inheritance.

        Example:
        - In a case where there is an abstract model 'Animal' and a subclass 'Dog',
          calling 'self.set_instance_type()' in Dog's save method would set 'instance_type' to 'dog'.
        """
        instance_type = getattr(self, instance_type_field)
        if instance_type is None:
            instance_type = self._meta.label_lower.split('.')[1]
            setattr(self, instance_type_field, instance_type)
