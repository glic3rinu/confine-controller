import resources
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(resources.NodeResource)
urlpatterns = router.urlpatterns

