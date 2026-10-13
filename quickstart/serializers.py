from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import Carrera, Materia, Alumno, Inscripcion, ImagenAlumno
from django.contrib.auth.password_validation import validate_password

from .models import Card


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = '__all__'


class CarreraSerializer(serializers.ModelSerializer):
    materias = MateriaSerializer(many=True, read_only=True)

    class Meta:
        model = Carrera
        fields = ['id', 'nombre', 'clave', 'descripcion', 'materias']


class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = '__all__'


class InscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscripcion
        fields = '__all__'

    def validate(self, attrs):
        # DRF no ejecuta el clean() del modelo, así que revisamos aquí
        # que la materia pertenezca a la carrera del alumno
        alumno = attrs.get("alumno") or getattr(self.instance, "alumno", None)
        materia = attrs.get("materia") or getattr(self.instance, "materia", None)
        if alumno and materia and alumno.carrera and materia.carrera != alumno.carrera:
            raise serializers.ValidationError(
                {"materia": "La materia no pertenece a la carrera del alumno."}
            )
        return attrs


class ImagenAlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenAlumno
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese correo.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese nombre de usuario.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'title', 'image', 'description']
        read_only_fields = ['id']
