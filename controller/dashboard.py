from fluent_dashboard.dashboard import FluentIndexDashboard
from .modules import MyThingsDashboardModule


class CustomIndexDashboard(FluentIndexDashboard):
    """
    Custom index dashboard for controller.
    """
    def init_with_context(self, context):
        super(CustomIndexDashboard, self).init_with_context(context)
        self.children.insert(-1, MyThingsDashboardModule())
