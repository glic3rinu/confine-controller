from django.contrib import admin
from models import Sliver, SliverProp, IsolatedIface, PublicIface, PrivateIface, Slice, SliceProp, Template


class SliverPropInline(admin.TabularInline):
    model = SliverProp
    extra = 0


class IsolatedIfaceInline(admin.TabularInline):
    model = IsolatedIface
    extra = 0


class PublicIfaceInline(admin.TabularInline):
    model = PublicIface
    extra = 0


class PrivateIfaceInline(admin.TabularInline):
    model = PrivateIface
    extra = 0


class SliverAdmin(admin.ModelAdmin):
    inlines = [SliverPropInline, IsolatedIfaceInline, PublicIfaceInline, PrivateIfaceInline]


class SlicePropInline(admin.TabularInline):
    model = SliceProp
    extra = 0


class SliceAdmin(admin.ModelAdmin):
    inlines = [SlicePropInline,]


admin.site.register(Sliver, SliverAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Template)
