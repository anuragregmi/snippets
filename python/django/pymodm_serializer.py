from rest_framework import serializers
from pymodm import fields as pymodm_fields
from pymodm import MongoModel

class PyMODMModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that maps PyMODM fields to DRF fields.
    """

    @classmethod
    def get_field_mapping(cls):
        """
        Return a mapping of PyMODM field types to DRF field types.
        """
        return {
            pymodm_fields.CharField: serializers.CharField,
            pymodm_fields.IntegerField: serializers.IntegerField,
            pymodm_fields.FloatField: serializers.FloatField,
            pymodm_fields.BooleanField: serializers.BooleanField,
            pymodm_fields.DateTimeField: serializers.DateTimeField,
            pymodm_fields.EmailField: serializers.EmailField,
            pymodm_fields.URLField: serializers.URLField,
            pymodm_fields.ListField: serializers.ListField,
            pymodm_fields.DictField: serializers.DictField,
            pymodm_fields.EmbeddedDocumentField: serializers.JSONField,  # Simplified handling
        }

    @classmethod
    def _get_model_field(cls, model_class, field_name):
        """
        Return the PyMODM field for a given field name.
        """
        return model_class.__dict__.get(field_name)

    def build_field(self, field_name, info, model_class, nested_depth):
        """
        Build a serializer field for a given PyMODM field.
        """
        field_class, field_kwargs = super().build_field(field_name, info, model_class, nested_depth)
        pymodm_field = self._get_model_field(model_class, field_name)

        if pymodm_field:
            field_mapping = self.get_field_mapping()
            field_class = field_mapping.get(type(pymodm_field), field_class)
            field_kwargs['required'] = pymodm_field.required

            if isinstance(pymodm_field, pymodm_fields.CharField):
                field_kwargs['max_length'] = pymodm_field.max_length

        return field_class, field_kwargs

    def create(self, validated_data):
        """
        Create a new instance of the PyMODM model.
        """
        return self.Meta.model(**validated_data).save()

    def update(self, instance, validated_data):
        """
        Update an existing instance of the PyMODM model.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
