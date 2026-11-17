from django import forms
from django.db import models
from django.forms import modelform_factory


class BootstrapFormMixin:
    """Adds Bootstrap 5 classes to every widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("rows", 3)

    def full_clean(self):
        super().full_clean()
        for name in self.errors:
            if name in self.fields:
                css = self.fields[name].widget.attrs.get("class", "")
                self.fields[name].widget.attrs["class"] = f"{css} is-invalid"


class BootstrapModelForm(BootstrapFormMixin, forms.ModelForm):
    pass


def html5_widget(db_field, **kwargs):
    """Use native HTML5 date/time pickers."""
    if isinstance(db_field, models.DateTimeField):
        kwargs["widget"] = forms.DateTimeInput(attrs={"type": "datetime-local"},
                                               format="%Y-%m-%dT%H:%M")
    elif isinstance(db_field, models.DateField):
        kwargs["widget"] = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")
    elif isinstance(db_field, models.TimeField):
        kwargs["widget"] = forms.TimeInput(attrs={"type": "time"}, format="%H:%M")
    return db_field.formfield(**kwargs)


def build_form(model, fields):
    return modelform_factory(model, form=BootstrapModelForm, fields=fields,
                             formfield_callback=html5_widget)
