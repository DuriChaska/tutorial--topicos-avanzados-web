from django.contrib import admin
from .models import Carrera, ImagenAlumno, Materia, Alumno, Inscripcion, Card

admin.site.register(Carrera)
admin.site.register(Materia)
admin.site.register(Alumno)
admin.site.register(Inscripcion)
admin.site.register(ImagenAlumno)
admin.site.register(Card)  # Register the Card model in the admin interface