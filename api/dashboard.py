from grappelli.dashboard import modules, Dashboard

class CustomIndexDashboard(Dashboard):
    def init_with_context(self, context):
        self.children.append(modules.AppList(
            title="Main Models",
            models=("api.models.*", "product.models.*", "category.models.*")
        ))

        self.children.append(modules.AppList(
            title="User Management",
            models=("django.contrib.auth.*",)
        ))

        self.children.append(modules.RecentActions(
            title="Recent Actions",
            limit=5,
        ))