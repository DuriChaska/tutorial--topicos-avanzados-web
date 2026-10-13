from django.contrib.auth.models import Group, User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from quickstart.serializers import GroupSerializer, UserSerializer

from .models import Alumno, Carrera, ImagenAlumno, Inscripcion, Materia, Card
from .permissions import IsAdminOrReadOnly
from .serializers import (
    AlumnoSerializer,
    CarreraSerializer,
    ImagenAlumnoSerializer,
    InscripcionSerializer,
    MateriaSerializer,
    RegisterSerializer,
    CardSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class CarreraViewSet(viewsets.ModelViewSet):
    queryset = Carrera.objects.all()
    serializer_class = CarreraSerializer
    permission_classes = [IsAdminOrReadOnly]


class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    permission_classes = [permissions.IsAuthenticated]


class AlumnoViewSet(viewsets.ModelViewSet):
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["carrera"]
    search_fields = ["nombre", "apellido_paterno", "apellido_materno", "numero_control"]
    permission_classes = [permissions.IsAuthenticated]


class InscripcionViewSet(viewsets.ModelViewSet):
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ImagenAlumnoViewSet(viewsets.ModelViewSet):
    queryset = ImagenAlumno.objects.all()
    serializer_class = ImagenAlumnoSerializer
    permission_classes = [permissions.IsAuthenticated]


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.pk,
            "email": user.email,
        })


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "detail": "Usuario creado correctamente. Inicia sesión para obtener tu Token.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    if request.method == "GET":
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
            }
        )

    data = request.data
    if "email" in data:
        if User.objects.filter(email__iexact=data["email"]).exclude(id=user.id).exists():
            return Response(
                {"email": ["Ya existe un usuario con este email"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.email = data["email"]

    if "username" in data:
        if User.objects.filter(username__iexact=data["username"]).exclude(id=user.id).exists():
            return Response(
                {"username": ["Ya existe un usuario con este nombre de usuario"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.username = data["username"]

    user.save()
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })
    
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            {"detail": "sesión cerrada exitosamente."},
            status=status.HTTP_204_NO_CONTENT
        )
        
class ResetTokenView(APIView):
    permission_classes = [IsAuthenticated]
    
    def port(self, request):
        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user)
        return Response(
            {"token": token.key, "detail": "token regenerado exitosamente"},
            status=status.HTTP_200_OK
        )
        
        
class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    #exigir permisos de admin
   #permission_classes = [permissions.IsAuthenticated]