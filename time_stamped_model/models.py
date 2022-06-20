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

    def make_new_slug(self, obj=None, name=None, on_edit=False, allow_dashes=True, extra_filters=None):
        """
        This allow you to populate a slug field. You need to call this function from model save. Only works if you add
        slug = models.SlugField(unique=True)
        on the model

        the add
        def save(self, *args, **kwargs):
            self.make_new_slug()
            super().save(*args, **kwargs)

        :param obj: The class name can be none and it will sort it self out
        :param name: The field to make the slug from
        :param on_edit
        :param allow_dashes:
        :param extra_filters:   this allow for unique together
        """
        if obj is None:
            obj = self.__class__

        if extra_filters is None:
            extra_filters = {}

        if name is None:
            # noinspection PyUnresolvedReferences
            name = self.name

        if not self.pk and (self.slug is None or self.slug == ''):
            main_slug = slugify(name)[:45]  # limits the slug to 45 chars as slug use 50

            if main_slug == '':
                main_slug = str(uuid.uuid4())
            if not allow_dashes:
                main_slug = main_slug.replace('-', '_')
            slug = main_slug
            count = 1
            while obj.objects.filter(slug=slug, **extra_filters).exists():
                slug = slugify("%s %d" % (main_slug, count))
                if not allow_dashes:
                    slug = slug.replace('-', '_')
                count += 1
            self.slug = slug
        elif self.pk and on_edit:
            main_slug = slugify(name)[:45]  # limits the slug to 45 chars as slug use 50
            if not allow_dashes:
                main_slug = main_slug.replace('-', '_')
            slug = main_slug
            count = 1
            while obj.objects.filter(slug=slug, **extra_filters).exclude(pk=self.pk).exists():
                slug = slugify("%s %d" % (main_slug, count))
                if not allow_dashes:
                    slug = slug.replace('-', '_')
                count += 1
            self.slug = slug

    def set_order_field(self, obj=None, extra_filters=None, order_field='order'):
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
