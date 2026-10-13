from rest_framework.routers import DefaultRouter
from .views import CarreraViewSet, ImagenAlumnoViewSet, MateriaViewSet, AlumnoViewSet, InscripcionViewSet

router = DefaultRouter()
router.register(r'carreras', CarreraViewSet)
router.register(r'materias', MateriaViewSet)
router.register(r'alumnos', AlumnoViewSet)
router.register(r'inscripciones', InscripcionViewSet)
router.register(r'imagenes', ImagenAlumnoViewSet)

urlpatterns = router.urls