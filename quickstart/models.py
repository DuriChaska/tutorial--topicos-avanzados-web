from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import (
    RegexValidator,
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    FileExtensionValidator,
)

# ---------- Validadores reutilizables ----------

solo_letras = RegexValidator(
    regex=r'^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$',
    message="Este campo solo puede contener letras y espacios."
)

clave_valida = RegexValidator(
    regex=r'^[A-Z0-9\-]+$',
    message="La clave solo puede tener letras MAYÚSCULAS, números y guiones."
)

numero_control_valido = RegexValidator(
    regex=r'^[A-Z]?\d{8}$',
    message="El número de control debe tener 8 dígitos (opcionalmente con una letra al inicio, ej. C23150326)."
)

ciclo_valido = RegexValidator(
    regex=r'^(ENE-JUN|AGO-DIC)\d{4}$',
    message="El ciclo debe tener el formato ENE-JUN2026 o AGO-DIC2026."
)


def validar_tamano_imagen(imagen):
    limite_mb = 2
    if imagen.size > limite_mb * 1024 * 1024:
        raise ValidationError(f"La imagen no debe pesar más de {limite_mb} MB.")


# ---------- Modelos ----------

class Carrera(models.Model):
    nombre = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3), solo_letras]
    )
    clave = models.CharField(
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(2), clave_valida]
    )
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Materia(models.Model):
    nombre = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)]
    )
    clave = models.CharField(
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(2), clave_valida]
    )
    creditos = models.IntegerField(
        validators=[
            MinValueValidator(1, message="La materia debe tener al menos 1 crédito."),
            MaxValueValidator(10, message="La materia no puede tener más de 10 créditos."),
        ]
    )
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name="materias")

    def __str__(self):
        return self.nombre


class Alumno(models.Model):
    nombre = models.CharField(max_length=100, validators=[MinLengthValidator(2), solo_letras])
    apellido_paterno = models.CharField(max_length=100, validators=[MinLengthValidator(2), solo_letras])
    apellido_materno = models.CharField(max_length=100, blank=True, null=True, validators=[solo_letras])
    numero_control = models.CharField(
        max_length=20,
        unique=True,
        validators=[numero_control_valido]
    )
    email = models.EmailField(unique=True)  # EmailField ya valida el formato
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, blank=True, null=True, related_name="alumnos")

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno or ''}".strip()


class Inscripcion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name="inscripciones")
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="inscripciones")
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    calificacion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0, message="La calificación no puede ser menor a 0."),
            MaxValueValidator(100, message="La calificación no puede ser mayor a 100."),
        ]
    )
    ciclo = models.CharField(max_length=11, validators=[ciclo_valido])

    class Meta:
        unique_together = ("alumno", "materia")

    def clean(self):
        # Validación entre campos: la materia debe ser de la carrera del alumno
        if self.alumno_id and self.materia_id:
            if self.alumno.carrera and self.materia.carrera != self.alumno.carrera:
                raise ValidationError({
                    "materia": "La materia no pertenece a la carrera del alumno."
                })

    def __str__(self):
        return f"{self.alumno} - {self.materia}"


class ImagenAlumno(models.Model):
    alumno = models.OneToOneField(Alumno, on_delete=models.CASCADE, related_name="foto")
    imagen = models.ImageField(
        upload_to='imagenes_alumnos/',
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            validar_tamano_imagen,
        ]
    )
    titulo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Imagen de {self.alumno}"
    
    
class Card(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='cards/', blank=True, null=True,)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.title