from common.admin import get_modeladmin
from firmware.actions import get_firmware
from firmware.models import BaseImage, FirmwareConfig, FirmwareConfigUCI
from nodes.models import Node


class BaseImageInline(admin.TabularInliner):
    model = BaseImage
    extra = 0


class FirmwareConfigUCIInline(admin.TabularInline):
    model = FirmwareConfigUCI
    extra = 0

class FirmwareConfigAdmin(admin.ModelAdmin):
    inlines = [BaseImageInline, FirmwareConfigUCIInline]


admin.site.register(FirmwareConfig, FirmwareConfigAdmin)


# Monkey-Patching
node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action('firmware', get_firmware, 'Download Firmware', 'viewsitelink')
