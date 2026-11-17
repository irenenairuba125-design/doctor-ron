from django.conf import settings
from django.urls import reverse

from .crud import REGISTRY


def navigation(request):
    user = request.user
    items = []
    if user.is_authenticated:
        for module in sorted(REGISTRY, key=lambda m: m.order):
            if module.in_nav and module.can_view(user):
                url = reverse(module.url_name("list"))
                items.append({
                    "title": module.title,
                    "icon": module.icon,
                    "url": url,
                    "active": False,
                })
        # Highlight the most specific matching menu entry
        matches = [i for i in items if request.path.startswith(i["url"])]
        if matches:
            max(matches, key=lambda i: len(i["url"]))["active"] = True
    return {"nav_items": items, "CURRENCY": settings.CURRENCY}
