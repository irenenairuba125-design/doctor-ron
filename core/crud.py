"""A small framework that generates list / detail / create / update / delete
views, URLs and navigation for each HMS model, with role-based access."""
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views import generic

from .forms import build_form
from .permissions import RoleRequiredMixin, has_role

REGISTRY = []  # every Module instance, used to build the sidebar


class Related:
    """A table of related records shown on a detail page."""

    def __init__(self, title, name, columns, add_url=None, param=None, add_roles=()):
        self.title, self.name, self.columns = title, name, columns
        self.add_url, self.param, self.add_roles = add_url, param, add_roles


class Action:
    """An extra button on a detail page (e.g. Discharge, Dispense)."""

    def __init__(self, label, url_name, *, icon="lightning", roles=(), condition=None,
                 method="post", style="primary", confirm="", query=None):
        self.label, self.url_name, self.icon, self.roles = label, url_name, icon, roles
        self.condition = condition or (lambda obj: True)
        self.method, self.style, self.confirm, self.query = method, style, confirm, query

    def url(self, obj):
        if self.query:  # GET link to another form, pre-filled from the object
            return f"{reverse(self.url_name)}?{self.query(obj)}"
        return reverse(self.url_name, args=[obj.pk])

BADGES = {
    # status value -> bootstrap colour
    "scheduled": "primary", "confirmed": "info", "completed": "success",
    "cancelled": "secondary", "no_show": "dark",
    "admitted": "warning", "discharged": "success", "transferred": "info", "deceased": "dark",
    "requested": "secondary", "in_progress": "warning",
    "unpaid": "danger", "partial": "warning", "paid": "success",
    "available": "success", "on_duty": "primary", "on_leave": "warning", "unavailable": "secondary",
    "active": "success", "inactive": "secondary", "suspended": "danger",
}


def label_for(model, name):
    try:
        return model._meta.get_field(name).verbose_name.capitalize()
    except FieldDoesNotExist:
        return name.replace("_", " ").capitalize().replace(" id", " ID")


def render_value(obj, name):
    """Readable HTML for an attribute: choices -> labels, statuses -> badges."""
    display = getattr(obj, f"get_{name}_display", None)
    value = getattr(obj, name, None)
    if callable(value):
        value = value()
    if display and value in BADGES:
        return format_html('<span class="badge text-bg-{}">{}</span>', BADGES[value], display())
    if display:
        return display()
    if isinstance(value, bool):
        icon = "check-circle-fill text-success" if value else "x-circle text-muted"
        return format_html('<i class="bi bi-{}"></i>', icon)
    if isinstance(value, Decimal):
        return f"{value:,.2f}"
    if value is None or value == "":
        return mark_safe('<span class="text-muted">—</span>')
    if hasattr(value, "get_absolute_url"):
        return format_html('<a href="{}">{}</a>', value.get_absolute_url(), value)
    return value


class Module:
    def __init__(self, model, *, namespace, fields, list_display, title=None, icon="circle",
                 prefix="", search_fields=(), list_filter=None, roles=(), view_roles=(),
                 detail_fields=None, related=(), actions=(), order=100, in_nav=True,
                 initial_from_query=()):
        self.model = model
        self.namespace = namespace
        self.prefix = prefix  # e.g. "medicine_" when an app has several modules
        self.fields = fields
        self.list_display = list_display
        self.title = title or model._meta.verbose_name_plural.title()
        self.singular = model._meta.verbose_name.title()
        self.icon = icon
        self.search_fields = search_fields
        self.list_filter = list_filter
        self.roles = tuple(roles)
        self.view_roles = tuple(roles) + tuple(view_roles)
        self.detail_fields = detail_fields or list_display + [
            f for f in fields if f not in list_display]
        self.related = related  # (title, related_name, [columns])
        self.actions = actions  # (label, url_name, icon, roles, condition(obj))
        self.order = order
        self.in_nav = in_nav
        self.initial_from_query = initial_from_query
        self.form_class = build_form(model, fields)
        REGISTRY.append(self)

    # ------------------------------------------------------------ helpers
    def url_name(self, action):
        return f"{self.namespace}:{self.prefix}{action}"

    def can_edit(self, user):
        return has_role(user, self.roles)

    def can_view(self, user):
        return has_role(user, self.view_roles)

    def context(self, view):
        user = view.request.user
        return {
            "module": self,
            "can_edit": self.can_edit(user),
            "list_url": reverse(self.url_name("list")),
            "create_url": reverse(self.url_name("create")),
        }

    # ------------------------------------------------------------ views
    def make_views(self):
        module = self

        class Base(RoleRequiredMixin):
            model = module.model
            allowed_roles = module.view_roles

            def get_context_data(self, **kwargs):
                ctx = super().get_context_data(**kwargs)
                ctx.update(module.context(self))
                return ctx

        class EditBase(Base):
            allowed_roles = module.roles
            form_class = module.form_class
            template_name = "core/form.html"

            def form_valid(self, form):
                messages.success(self.request, f"{module.singular} saved successfully.")
                return super().form_valid(form)

        class ListView(Base, generic.ListView):
            template_name = "core/list.html"
            paginate_by = 20

            def get_queryset(self):
                qs = super().get_queryset()
                q = self.request.GET.get("q", "").strip()
                if q and module.search_fields:
                    cond = Q()
                    for f in module.search_fields:
                        cond |= Q(**{f"{f}__icontains": q})
                    qs = qs.filter(cond)
                if module.list_filter:
                    value = self.request.GET.get(module.list_filter)
                    if value:
                        qs = qs.filter(**{module.list_filter: value})
                return qs

            def get_context_data(self, **kwargs):
                ctx = super().get_context_data(**kwargs)
                ctx["headers"] = [label_for(module.model, c) for c in module.list_display]
                ctx["rows"] = [
                    (obj, [render_value(obj, c) for c in module.list_display])
                    for obj in ctx["object_list"]
                ]
                if module.list_filter:
                    field = module.model._meta.get_field(module.list_filter)
                    ctx["filter_name"] = module.list_filter
                    ctx["filter_label"] = field.verbose_name.capitalize()
                    ctx["filter_choices"] = field.choices
                    ctx["filter_value"] = self.request.GET.get(module.list_filter, "")
                ctx["q"] = self.request.GET.get("q", "")
                query = self.request.GET.copy()
                query.pop("page", None)
                ctx["querystring"] = query.urlencode()
                return ctx

        class DetailView(Base, generic.DetailView):
            template_name = "core/detail.html"

            def get_context_data(self, **kwargs):
                ctx = super().get_context_data(**kwargs)
                obj = self.object
                user = self.request.user
                ctx["fields"] = [(label_for(module.model, f), render_value(obj, f))
                                 for f in module.detail_fields]
                ctx["related"] = []
                for rel in module.related:
                    rel_qs = list(getattr(obj, rel.name).all()[:25])
                    rel_model = getattr(obj, rel.name).model
                    add_url = None
                    if rel.add_url and has_role(user, rel.add_roles):
                        add_url = f"{reverse(rel.add_url)}?{rel.param}={obj.pk}"
                    ctx["related"].append({
                        "title": rel.title,
                        "add_url": add_url,
                        "headers": [label_for(rel_model, c) for c in rel.columns],
                        "rows": [(r, [render_value(r, c) for c in rel.columns]) for r in rel_qs],
                    })
                ctx["actions"] = [
                    {"label": a.label, "url": a.url(obj), "icon": a.icon, "method": a.method,
                     "style": a.style, "confirm": a.confirm}
                    for a in module.actions if has_role(user, a.roles) and a.condition(obj)
                ]
                ctx["update_url"] = reverse(module.url_name("update"), args=[obj.pk])
                ctx["delete_url"] = reverse(module.url_name("delete"), args=[obj.pk])
                return ctx

        class CreateView(EditBase, generic.CreateView):
            def get_initial(self):
                initial = super().get_initial()
                for name in module.initial_from_query:
                    if name in self.request.GET:
                        initial[name] = self.request.GET[name]
                return initial

        class UpdateView(EditBase, generic.UpdateView):
            pass

        class DeleteView(EditBase, generic.DeleteView):
            template_name = "core/confirm_delete.html"

            def get_success_url(self):
                return reverse(module.url_name("list"))

            def post(self, request, *args, **kwargs):
                obj = self.get_object()
                try:
                    obj.delete()
                except ProtectedError:
                    messages.error(request, f"Cannot delete this {module.singular.lower()}: "
                                            "other records depend on it.")
                    return redirect(obj.get_absolute_url())
                messages.success(request, f"{module.singular} deleted.")
                return redirect(self.get_success_url())

        return ListView, DetailView, CreateView, UpdateView, DeleteView

    @property
    def urls(self):
        lv, dv, cv, uv, delv = self.make_views()
        p = self.prefix
        base = p.rstrip("_") + "s/" if p else ""
        return [
            path(f"{base}", lv.as_view(), name=f"{p}list"),
            path(f"{base}new/", cv.as_view(), name=f"{p}create"),
            path(f"{base}<int:pk>/", dv.as_view(), name=f"{p}detail"),
            path(f"{base}<int:pk>/edit/", uv.as_view(), name=f"{p}update"),
            path(f"{base}<int:pk>/delete/", delv.as_view(), name=f"{p}delete"),
        ]


def currency():
    return settings.CURRENCY
