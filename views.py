# -*- coding: utf-8 -*-
# Django Decoradores:
# from django.utils.decorators import method_decorator
# from django.contrib.admin.views.decorators import staff_member_required

# Otras Librerias:
import xlwt
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
from xlsxwriter.utility import xl_range
import datetime
import calendar
import json
# import re
import time
import sys
import collections
from zipfile import ZipFile
from decimal import Decimal
import StringIO
import os

# Django ORMk1
from django.db.models import Q
from django.db.models import Max
from django.db.models import Sum
from django.db.models import Avg
from django.db.models import Count

# Django Atajos:
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect


# Django Urls:
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse

# Django Generic Views
from django.views.generic.base import View
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import TemplateView

# Django serializers:
from django.core import serializers

# Django database
# from django.db.models import Q

# Django exceptions
# from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import PermissionRequiredMixin

# from django.conf import settings
# Modelos:
from .models import Equipo
from .models import Odometro
from .models import Ubicacion
from .models import Medicion
from .models import UdmOdometro
from .models import TipoCombustible
from .models import Pozo
from .models import Asignacion
from .models import TipoOdometro
from .models import Sistema

from home.models import AnexoImagen
from home.models import AnexoArchivo
from home.models import AnexoTexto
from home.models import TipoAnexo
from home.models import indicadores

from administracion.models import Cliente
from administracion.models import Contrato
# Formularios:
from .forms import EquipoFiltersForm
from .forms import EquipoForm
from .forms import UbicacionForm
from .forms import UbicacionFiltersForm
from .forms import OdometroForm
from .forms import OdometroFiltersForm
from .forms import MedicionFiltersForm
from .forms import MedicionForm
from .forms import UdmOdometroForm
from .forms import PozoFiltersForm
from .forms import PozoForm
from .forms import AsignacionFiltersForm
from .forms import AsignacionForm2
from .forms import TipoCombustibleForm
from .forms import ProduccionFiltersForm
from .forms import TipoOdometroForm
from .forms import SistemaForm
from .forms import PozoHistoricoFiltersForm

from .forms import MedicionesFilterForm
from .forms import MedicionesPozoFilterForm
from .forms import CapturaMedcionFiltersForm

from .forms import ReportesFiltersForm

from .forms import ServicioForm

from home.forms import AnexoTextoForm
from home.forms import AnexoImagenForm
from home.forms import AnexoArchivoForm
from home.forms import TipoAnexoForm
# API Rest:
from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
# from django.contrib.auth.decorators import permission_required
from django.http import Http404

# API Rest - Serializadores:
from .serializers import EquipoSerializer
from .serializers import EquipoTreeSerilizado
from .serializers import EquipoTreeSerilizado2
from .serializers import OdometroSerializer
from .serializers import MedicionSerializer
from .serializers import UdmOdometroSerializer
from .serializers import TipoCombustibleSerializer
from .serializers import UbicacionSerializer
from .serializers import UbicacionTreeSerializado
from .serializers import PozoSerializer
from .serializers import AsignacionSerializer
from .serializers import AsignacionHistorySerializer
from .serializers import EquipoSerializer2
from .serializers import TipoOdometroSerializer
from .serializers import SistemaSerializer
from .serializers import UbicacionClienteSerializer

from home.serializers import AnexoTextoSerializer
from home.serializers import AnexoArchivoSerializer
from home.serializers import AnexoImagenSerializer

# API Rest - Paginacion:
from .pagination import GenericPagination
from .pagination import GenericPagination2
from .pagination import GenericPaginationx200
from .pagination import GenericPaginationx110

# API Rest - Filtros:
from .filters import EquipoFilter
from .filters import OdometroFilter
from .filters import MedicionFilter
from .filters import EquipoOrdenFilter
from .filters import UbicacionFilter
from .filters import PozoFilter
from .filters import EquiposAsignadosFilter
from .filters import EquiposNoAsignadosFilter
# from .filters import PozoUbicacionFilter
# from .filters import AsignacionFilter

# Utilidades
# from home.utilities import render_to_pdf
# from .permissions import PermissionExportEquipos


# ----------------- EQUIPO ----------------- #


class EquiposNoAsignadosAPI(View):

    def get(self, request, pozo):
        equipos = Equipo.objects.exclude(asignacion__pozo=pozo)

        data = serializers.serialize(
            'json',
            equipos,
            fields=[
                'pk',
                'tag',
                'descripcion'
            ]
        )

        return HttpResponse(data, content_type='application/json')


class EquiposAsignadosAPI(View):

    def get(self, request, pozo):

        equipos = Equipo.objects.filter(asignacion__pozo=pozo)
        data = serializers.serialize(
            'json',
            equipos,
            fields=[
                'pk',
                'tag',
                'descripcion',
            ]
        )

        return HttpResponse(data, content_type='application/json')


class EquiposAsignadosAPI2(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer2
    filter_backends = (DjangoFilterBackend,)
    filter_class = EquiposAsignadosFilter


class EquiposNoAsignadosAPI2(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer2
    filter_backends = (DjangoFilterBackend, )
    filter_class = EquiposNoAsignadosFilter


class EquipoListView(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_equipos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'equipo/lista.html'

    def get(self, request, tipo):
        request.POST = {"tag": tipo}
        formulario = EquipoFiltersForm(request.POST)
        contexto = {
            'form': formulario
        }

        return render(request, self.template_name, contexto)


class EquipoCreateView(PermissionRequiredMixin, View):

    permission_required = 'activos.agregar_equipos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'equipo/formulario.html'

    def obtener_UrlImagen(self, _imagen):
        imagen = ''

        if _imagen:
            imagen = _imagen.url

        return imagen

    def get(self, request):
        formulario = EquipoForm()
        form_ubicacion = UbicacionForm()
        contexto = {
            'form': formulario,
            'form_u': form_ubicacion,
            'operation': "Nuevo",
            'equipo_id': 0
        }

        return render(request, self.template_name, contexto)

    def post(self, request):
        url_imagen = ""
        formulario = EquipoForm(request.POST, request.FILES)
        form_ubicacion = UbicacionForm()

        if formulario.is_valid():

            datos_formulario = formulario.cleaned_data
            equipo = Equipo()
            equipo.tag = datos_formulario.get('tag')
            equipo.descripcion = datos_formulario.get('descripcion')
            equipo.serie = datos_formulario.get('serie')
            equipo.especialidad = datos_formulario.get('especialidad')
            equipo.marca = datos_formulario.get('marca')
            equipo.modelo = datos_formulario.get('modelo')
            equipo.horsepower = datos_formulario.get('horsepower')
            equipo.geometria = datos_formulario.get('geometria')
            equipo.tipo_combustible = datos_formulario.get('tipo_combustible')
            equipo.tipo_equipo = datos_formulario.get('tipo_equipo')
            equipo.estado = datos_formulario.get('estado')
            equipo.contrato = datos_formulario.get('contrato')
            equipo.padre = datos_formulario.get('padre')
            equipo.empresa = datos_formulario.get('empresa')
            equipo.responsable = datos_formulario.get('responsable')
            equipo.sistema = datos_formulario.get('sistema')
            equipo.ubicacion = datos_formulario.get('ubicacion')
            equipo.imagen = datos_formulario.get('imagen')
            url_imagen = self.obtener_UrlImagen(equipo.imagen)
            equipo.save()

            return redirect(
                reverse('activos:equipos_lista', kwargs={'tipo': ""})
            )

        contexto = {
            'form': formulario,
            'form_u': form_ubicacion,
            'imagen': url_imagen,
            'operation': "Nuevo"
        }
        return render(request, self.template_name, contexto)


class EquipoUpdateView(PermissionRequiredMixin, View):

    permission_required = 'activos.editar_equipos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'equipo/formulario.html'
        self.tag = ''

    def obtener_UrlImagen(self, _imagen):
        imagen = ''

        if _imagen:
            imagen = _imagen.url

        return imagen

    def get(self, request, pk):
        equipo = get_object_or_404(Equipo, pk=pk)
        self.tag = equipo.tag

        formulario = EquipoForm(
            instance=equipo
        )
        form_u = UbicacionForm()

        contexto = {
            'form': formulario,
            'form_u': form_u,
            'tag': self.tag,
            'operation': "Editar",
            'equipo_id': equipo.id,
            'imagen': self.obtener_UrlImagen(equipo.imagen)
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        equipo = get_object_or_404(Equipo, pk=pk)
        self.tag = equipo.tag

        formulario = EquipoForm(
            request.POST,
            request.FILES,
            instance=equipo
        )
        form_u = UbicacionForm()

        if formulario.is_valid():

            equipo = formulario.save(commit=False)
            equipo.save()

            return redirect(
                reverse('activos:equipos_lista', kwargs={'tipo': ""})
            )

        contexto = {
            'form': formulario,
            'form_u': form_u,
            'tag': self.tag,
            'operation': "Editar",
            'equipo_id': equipo.id,
            'imagen': self.obtener_UrlImagen(equipo.imagen)
        }
        return render(request, self.template_name, contexto)


class EquipoFichaTecnica(PermissionRequiredMixin, View):

    permission_required = 'activos.ver_equipos'
    raise_exception = True

    def obtener_UrlImagen(self, _imagen):
        imagen = ''

        if _imagen:
            imagen = _imagen.url

        return imagen

    def get(self, request, pk, tipo):
        if tipo == "1":
            template_name = 'equipo/ficha_tecnica.html'
        else:
            template_name = 'equipo/ficha_tecnica_print.html'
        equipo = get_object_or_404(Equipo, pk=pk)
        hoy = datetime.datetime.today()
        hijos = Equipo.objects.filter(
            padre__tag=equipo.tag).exclude(tag__icontains="BJ")
        tipo = 0
        if any(substring in equipo.tag for substring in ["EBH", "EBCP"]):
            tipo = 1
        elif any(
            substring in equipo.tag for substring in [
                "GE", "VDF", "MBCP", "MC", "ME", "BT"]):
            tipo = 2
        elif any(substring in equipo.tag for substring in ["JTP", "FWKO"]):
            tipo = 3
        elif any(substring in equipo.tag for substring in ["DBCP", "BOP"]):
            tipo = 4
        elif any(substring in equipo.tag for substring in ["BJ"]):
            tipo = 5
        elif any(substring in equipo.tag for substring in ["HO"]):
            tipo = 6
        contexto = {
            'equipo': equipo,
            'hoy': hoy,
            'hijos': hijos,
            'imagen': self.obtener_UrlImagen(equipo.imagen),
            'tipo': tipo
        }

        return render(request, template_name, contexto)


class EquipoMedicion(View):

    def __init__(self):
        self.template_name = "equipo/medicion/lista.html"

    def get(self, request, pk):

        equipo = get_object_or_404(Equipo, pk=pk)

        odometros = Odometro.objects.filter(equipo=equipo)

        if len(odometros) > 0:
            odometro = odometros.first()
        else:
            odometro = -1

        contexto = {
            'equipo': equipo,
            'odometro': odometro,
            'odometros': odometros
        }

        return render(request, self.template_name, contexto)


class EquipoAPI(viewsets.ModelViewSet):
    queryset = Equipo.objects.all().order_by("estado")
    serializer_class = EquipoSerializer
    pagination_class = GenericPaginationx200

    filter_backends = (DjangoFilterBackend,)
    filter_class = EquipoFilter


class EquipoExcelAPI(viewsets.ModelViewSet):
    queryset = Equipo.objects.all().order_by("-created_date")
    serializer_class = EquipoSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = EquipoFilter
    # permission_classes = (IsAuthenticated, PermissionExportEquipos)


class EquipoArbol(PermissionRequiredMixin, View):

    permission_required = 'activos.ver_estructura_equipo'
    raise_exception = True

    def __init__(self):
        self.template_name = "equipo/arbol.html"

    def get(self, request, pk):
        equipo = get_object_or_404(Equipo, pk=pk)

        contexto = {
            "equipo": equipo
        }

        return render(request, self.template_name, contexto)


class EquipoTreeAPI(View):

    def get(self, request, pk):

        daddies = Equipo.objects.filter(pk=pk)

        serializador = EquipoTreeSerilizado()
        lista_json = serializador.get_Json(daddies)

        return HttpResponse(
            lista_json,
            content_type="application/json"
        )


class EquipoTreeAPI2(View):

    def get(self, request, q):

        daddies = Equipo.objects.filter(
            Q(tag__icontains=q) |
            Q(descripcion__icontains=q)
        )

        serializador = EquipoTreeSerilizado2()
        lista_json = serializador.get_Json(daddies)

        return HttpResponse(
            lista_json,
            content_type="application/json"
        )


class EquipoHistory(View):

    def __init__(self):
        self.template_name = 'equipo/historia.html'

    def get(self, request, pk):

        registros = Equipo.history.filter(id=pk).order_by("-history_date")
        contexto = {
            'operation': "Historia",
            'equipo_id': pk,
            'registros': registros
        }

        return render(request, self.template_name, contexto)


class EquipoOrdenAPI(viewsets.ModelViewSet):
    queryset = Equipo.objects.filter(estado="ACT")
    serializer_class = EquipoSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = EquipoOrdenFilter


# ----------------- EQUIPO - ANEXO ----------------- #

class AnexoTextoView(PermissionRequiredMixin, View):

    permission_required = 'activos.ver_anexos_equipos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'equipo/anexos/anexos_texto.html'

    def get(self, request, pk):
        id_equipo = pk
        anexos = AnexoTexto.objects.filter(equipo=id_equipo)
        equipo = Equipo.objects.get(id=id_equipo)
        form = AnexoTextoForm()

        contexto = {
            'form': form,
            'id': id_equipo,
            'equipo': equipo,
            'anexos': anexos,
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        id_equipo = pk
        form = AnexoTextoForm(request.POST)
        anexos = AnexoTexto.objects.filter(equipo=id_equipo)
        equipo = Equipo.objects.get(id=id_equipo)

        if form.is_valid():
            texto = form.save(commit=False)
            texto.equipo_id = id_equipo
            texto.save()
            anexos = AnexoTexto.objects.filter(equipo=id_equipo)
            form = AnexoTextoForm()
        return render(request, 'equipo/anexos/anexos_texto.html',
                      {'form': form, 'id': id_equipo, 'anexos': anexos,
                       'equipo': equipo})


class AnexoImagenView(PermissionRequiredMixin, View):

    permission_required = 'activos.ver_anexos_equipos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'equipo/anexos/anexos_imagen.html'

    def get(self, request, pk):
        id_equipo = pk
        anexos = AnexoImagen.objects.filter(equipo=id_equipo)
        equipo = Equipo.objects.get(id=id_equipo)
        form = AnexoImagenForm()

        contexto = {
            'form': form,
            'id': id_equipo,
            'equipo': equipo,
            'anexos': anexos,
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        id_equipo = pk
        anexos = AnexoImagen.objects.filter(equipo=id_equipo)
        equipo = Equipo.objects.get(id=id_equipo)
        form = AnexoImagenForm(request.POST, request.FILES)

        if form.is_valid():

            imagen_anexo = AnexoImagen()
            imagen_anexo.descripcion = request.POST['descripcion']
            if 'ruta' in request.POST:
                imagen_anexo.ruta = request.POST['ruta']
            else:
                imagen_anexo.ruta = request.FILES['ruta']
            imagen_anexo.equipo_id = id_equipo
            imagen_anexo.save()
            form = AnexoImagenForm()
            anexos = AnexoImagen.objects.filter(equipo=id_equipo)
            # return render(request, self.template_name,
            #               {'form': form, 'id': id_equipo, 'anexos': anexos,
            #                'equipo': equipo})
        contexto = {
            'form': form,
            'id': id_equipo,
            'equipo': equipo,
            'anexos': anexos,
        }
        return render(request, self.template_name, contexto)


class AnexoArchivoView(PermissionRequiredMixin, View):

    permission_required = 'activos.ver_anexos_equipos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'equipo/anexos/anexos_archivo.html'

    def get(self, request, pk):
        id_equipo = pk
        anexos = AnexoArchivo.objects.filter(equipo=id_equipo)
        equipo = Equipo.objects.get(id=id_equipo)
        form = AnexoArchivoForm()

        contexto = {
            'form': form,
            'id': id_equipo,
            'equipo': equipo,
            'anexos': anexos,
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        id_equipo = pk
        equipo = Equipo.objects.get(id=id_equipo)
        form = AnexoArchivoForm(request.POST, request.FILES)
        anexos = AnexoArchivo.objects.filter(equipo=id_equipo)

        if form.is_valid():
            archivo_anexo = AnexoArchivo()
            archivo_anexo.descripcion = request.POST['descripcion']
            if 'archivo' in request.POST:
                archivo_anexo.archivo = request.POST['archivo']
            else:
                archivo_anexo.archivo = request.FILES['archivo']
            archivo_anexo.equipo_id = id_equipo
            archivo_anexo.save()
            anexos = AnexoArchivo.objects.filter(equipo=id_equipo)
            form = AnexoArchivoForm()

        contexto = {
            'form': form,
            'id': id_equipo,
            'equipo': equipo,
            'anexos': anexos,
        }

        return render(request, self.template_name, contexto)


class AnexoTextoAPI(viewsets.ModelViewSet):
    queryset = AnexoTexto.objects.all()
    serializer_class = AnexoTextoSerializer
    pagination_class = GenericPagination


class AnexoArchivoAPI(viewsets.ModelViewSet):
    queryset = AnexoArchivo.objects.all()
    serializer_class = AnexoArchivoSerializer
    pagination_class = GenericPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('equipo',)


class AnexoImagenAPI(viewsets.ModelViewSet):
    queryset = AnexoImagen.objects.all()
    serializer_class = AnexoImagenSerializer
    pagination_class = GenericPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('equipo',)

# ------------ TIPO DE COMBUSTIBLE -------------- #


class TipoCombustibleListView(TemplateView):
    template_name = 'tipo_combustible/lista.html'


class TipoCombustibleCreateView(CreateView):
    model = TipoCombustible
    form_class = TipoCombustibleForm
    template_name = 'tipo_combustible/formulario.html'
    success_url = reverse_lazy('activos:tipo_combustible_lista')
    operation = "Nuevo"

    def get_context_data(self, **kwargs):
        contexto = super(
            TipoCombustibleCreateView,
            self).get_context_data(**kwargs)
        contexto['operation'] = self.operation
        return contexto


class TipoCombustibleUpdateView(UpdateView):
    model = TipoCombustible
    form_class = TipoCombustibleForm
    template_name = 'tipo_combustible/formulario.html'
    success_url = reverse_lazy('activos:tipo_combustible_lista')
    operation = "Editar"

    def get_context_data(self, **kwargs):
        contexto = super(
            TipoCombustibleUpdateView,
            self).get_context_data(**kwargs)
        contexto['operation'] = self.operation
        return contexto


class TipoCombustibleByPageAPI(viewsets.ModelViewSet):
    queryset = TipoCombustible.objects.all()
    serializer_class = TipoCombustibleSerializer
    pagination_class = GenericPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('nombre', 'descripcion', 'marca',)


class TipoCombustibleAPI(viewsets.ModelViewSet):
    queryset = TipoCombustible.objects.all()
    serializer_class = TipoCombustibleSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('nombre', 'descripcion', 'marca',)

# ------------- ---- ODOMETRO ----------------- #


class OdometroListView(PermissionRequiredMixin, View):

    permission_required = 'activos.ver_odometros'
    raise_exception = True

    def __init__(self):
        self.template_name = 'odometro/lista.html'

    def get(self, request):
        formulario = OdometroFiltersForm()

        contexto = {
            'form': formulario
        }

        return render(request, self.template_name, contexto)

    def post(self, request):
        return render(request, self.template_name, {})


class OdometroCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'activos.agregar_odometros'
    raise_exception = True

    model = Odometro
    form_class = OdometroForm
    template_name = 'odometro/formulario.html'
    success_url = reverse_lazy('activos:odometros_lista')
    operation = "Nuevo"

    def get_context_data(self, **kwargs):
        contexto = super(OdometroCreateView, self).get_context_data(**kwargs)
        contexto['operation'] = self.operation
        return contexto


class OdometroUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'activos.editar_odometros'
    raise_exception = True

    model = Odometro
    form_class = OdometroForm
    template_name = 'odometro/formulario.html'
    success_url = reverse_lazy('activos:odometros_lista')
    operation = "Editar"

    def get_context_data(self, **kwargs):
        contexto = super(OdometroUpdateView, self).get_context_data(**kwargs)
        contexto['operation'] = self.operation
        return contexto


class OdometroAPI(viewsets.ModelViewSet):
    queryset = Odometro.objects.all()
    serializer_class = OdometroSerializer
    pagination_class = GenericPaginationx200
    filter_backends = (DjangoFilterBackend,)
    filter_class = OdometroFilter


class OdometroExcelAPI(viewsets.ModelViewSet):
    queryset = Odometro.objects.all()
    serializer_class = OdometroSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = OdometroFilter

# ----------------- TIPO ODOMETRO ----------------- #


class TipoOdometroListView(PermissionRequiredMixin, TemplateView):
    permission_required = 'activos.ver_tipo_odometros'
    raise_exception = True

    template_name = 'tipo_odometro/lista.html'


class TipoOdometroCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'activos.agregar_tipo_odometros'
    raise_exception = True

    model = TipoOdometro
    form_class = TipoOdometroForm
    template_name = 'tipo_odometro/formulario.html'
    success_url = reverse_lazy('activos:tipos_odometro_lista')
    operation = "Nueva"

    def get_context_data(self, **kwargs):
        contexto = super(
            TipoOdometroCreateView,
            self
        ).get_context_data(**kwargs)
        contexto['operation'] = self.operation
        return contexto


class TipoOdometroUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'activos.editar_tipo_odometros'
    raise_exception = True

    model = TipoOdometro
    form_class = TipoOdometroForm
    template_name = 'tipo_odometro/formulario.html'
    success_url = reverse_lazy('activos:tipos_odometro_lista')
    operation = "Editar"

    def get_context_data(self, **kwargs):
        contexto = super(
            TipoOdometroUpdateView,
            self
        ).get_context_data(**kwargs)
        contexto['operation'] = self.operation
        return contexto


class TipoOdometroAPI(viewsets.ModelViewSet):
    queryset = TipoOdometro.objects.all()
    serializer_class = TipoOdometroSerializer

    filter_backends = (filters.SearchFilter,)
    search_fields = ('clave', 'descripcion',)


class TipoOdometroAPI2(viewsets.ModelViewSet):
    queryset = TipoOdometro.objects.all()
    serializer_class = TipoOdometroSerializer

    filter_backends = (filters.SearchFilter,)
    filter_fields = ('id',)


# ----------------- UDM ODOMETRO ----------------- #

class UdmOdometroListView(PermissionRequiredMixin, TemplateView):
    permission_required = 'activos.ver_udm_odometros'
    raise_exception = True

    template_name = 'udm_odometro/lista.html'


class UdmOdometroCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'activos.agregar_udm_odometros'
    raise_exception = True

    model = UdmOdometro
    form_class = UdmOdometroForm
    template_name = 'udm_odometro/formulario.html'
    success_url = reverse_lazy('activos:udms_odometro_lista')
    operation = "Nueva"

    def get_context_data(self, **kwargs):
        contexto = super(
            UdmOdometroCreateView,
            self
        ).get_context_data(**kwargs)
        contexto['operation'] = self.operation
        return contexto


class UdmOdometroUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'activos.editar_udm_odometros'
    raise_exception = True

    model = UdmOdometro
    form_class = UdmOdometroForm
    template_name = 'udm_odometro/formulario.html'
    success_url = reverse_lazy('activos:udms_odometro_lista')
    operation = "Editar"

    def get_context_data(self, **kwargs):
        contexto = super(
            UdmOdometroUpdateView,
            self
        ).get_context_data(**kwargs)
        contexto['operation'] = self.operation
        return contexto


class UdmOdometroAPI(viewsets.ModelViewSet):
    queryset = UdmOdometro.objects.all()
    serializer_class = UdmOdometroSerializer

    filter_backends = (filters.SearchFilter,)
    search_fields = ('clave', 'descripcion',)


class UdmOdometroAPI2(viewsets.ModelViewSet):
    queryset = UdmOdometro.objects.all()
    serializer_class = UdmOdometroSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id',)


# ----------------- MEDICIONES ----------------- #

class MedicionView(PermissionRequiredMixin, View):

    permission_required = 'activos.agregar_mediciones'
    raise_exception = True

    def __init__(self):
        self.template_name = 'medicion/grid.html'

    def get(self, request):
        formulario_medicion = MedicionesFilterForm()
        clave = "RP"
        odometros = Odometro.objects.filter(
            tipos__clave=clave).order_by('id')
        pozos = Pozo.objects.all().order_by('id')
        mediciones = list(Medicion.objects.filter(
            odometro__tipos__clave=clave).order_by('-fecha', '-id'))
        lista = []
        cambios = False
        bandera = 0
        odometros_observavciones = Odometro.objects.filter(tipos__clave="O")
        for p in pozos:
            nodo = self.crea_Nodo(p.nombre, p.id)
            for o in odometros:
                for oo in odometros_observavciones:
                    if oo.id == o.id:
                        bandera = 1
                for m in mediciones:
                    if m.odometro_id == o.id and m.pozo_id == p.id:
                        if cambios is not True:
                            fecha = m.fecha.strftime("%Y/%m/%d %H:%M")
                            if bandera == 1:
                                nodo_odometro = self.crea_NodoOdometro(
                                    o.descripcion,
                                    o.id,
                                    m.observaciones,
                                    fecha,
                                    bandera)
                            else:
                                nodo_odometro = self.crea_NodoOdometro(
                                    o.descripcion,
                                    o.id,
                                    ('%f' % m.lectura).rstrip('0').rstrip('.'),
                                    fecha,
                                    bandera)
                            nodo["lista_odometro"].append(nodo_odometro)
                            mediciones.remove(m)
                            cambios = True
                if cambios is not True:
                    nodo_odometro = self.crea_NodoOdometro(
                        o.descripcion, o.id, '-', '', bandera)
                    nodo["lista_odometro"].append(nodo_odometro)
                else:
                    cambios = False
                bandera = 0
            lista.append(nodo)

        contexto = {
            'form': formulario_medicion,
            'odometros': odometros,
            'lista_odometros': [],
            'lista_pozos': [],
            'lista': lista,
        }
        return render(request, self.template_name, contexto)

    def post(self, request):
        formulario = MedicionesFilterForm(request.POST)

        pozos = request.POST.getlist('pozo')
        odometros = request.POST.getlist('odometro')
        tipo = request.POST.get('tipos')

        pozos_lista = [int(item) for item in pozos]
        odometros_lista = [int(item) for item in odometros]

        pozos_list = json.dumps(pozos_lista)
        odometros_list = json.dumps(odometros_lista)

        if len(pozos) == 0:
            pozos = []
            lista_pozos = Pozo.objects.all()
            for l in lista_pozos:
                pozos.append(l.pk)
        else:
            lista_pozos = Pozo.objects.filter(pk__in=pozos)

        if len(odometros) == 0:
            odometros = []
            if tipo == "0":
                lista_odometros = Odometro.objects.all()
            else:
                lista_odometros = Odometro.objects.filter(tipos__id=tipo)
            for l in lista_odometros:
                odometros.append(l.pk)
        else:
            if tipo == "0":
                lista_odometros = Odometro.objects.filter(pk__in=odometros)
            else:
                lista_odometros = Odometro.objects.filter(tipos__id=tipo)

        mediciones = list(Medicion.objects.filter(
            pozo__id__in=pozos,
            odometro__id__in=odometros).order_by('-fecha', '-id'))

        odometros_observavciones = Odometro.objects.filter(tipos__clave="O")

        lista = []
        cambios = False
        bandera = 0
        for p in lista_pozos:
            nodo = self.crea_Nodo(p.nombre, p.id)
            for o in lista_odometros:
                for oo in odometros_observavciones:
                    if oo.id == o.id:
                        bandera = 1
                for m in mediciones:
                    if m.odometro_id == o.id and m.pozo_id == p.id:
                        if cambios is not True:
                            fecha = m.fecha.strftime("%Y/%m/%d %H:%M")
                            if bandera == 1:
                                nodo_odometro = self.crea_NodoOdometro(
                                    o.descripcion,
                                    o.id,
                                    m.observaciones,
                                    fecha,
                                    bandera)
                            else:
                                nodo_odometro = self.crea_NodoOdometro(
                                    o.descripcion,
                                    o.id,
                                    ('%f' % m.lectura).rstrip('0').rstrip('.'),
                                    fecha,
                                    bandera)
                            nodo["lista_odometro"].append(nodo_odometro)
                            mediciones.remove(m)
                            cambios = True
                if cambios is not True:
                    nodo_odometro = self.crea_NodoOdometro(
                        o.descripcion, o.id, '-', '', bandera)
                    nodo["lista_odometro"].append(nodo_odometro)
                else:
                    cambios = False
                bandera = 0
            lista.append(nodo)

        contexto = {
            'form': formulario,
            'odometros': lista_odometros,
            'lista': lista,
            'lista_pozos': pozos_list,
            'lista_odometros': odometros_list,
        }
        return render(request, self.template_name, contexto)

    def crea_Nodo(self, pozo, id_pozo):
        nodo = {}
        nodo["pozo"] = pozo
        nodo["id_pozo"] = id_pozo
        nodo["lista_odometro"] = []
        return nodo

    def crea_NodoOdometro(self, odometro, id_odometro, medicion, fecha, ban):
        nodo_odometro = {}
        nodo_odometro["odometro"] = odometro
        nodo_odometro["id_odometro"] = id_odometro
        nodo_odometro["medicion"] = medicion
        nodo_odometro["fecha"] = fecha
        nodo_odometro["es_observacion"] = ban
        return nodo_odometro


class MedicionPozoView(PermissionRequiredMixin, View):

    permission_required = 'activos.editar_mediciones'
    raise_exception = True

    def __init__(self):
        self.template_name = 'medicion/historial.html'

    def get(self, request, pk, clave):
        formulario_medicion = MedicionesPozoFilterForm()
        id_pozo = pk
        pozo = {}
        pozo["nombre"] = "Historial de Mediciones"
        pozo["pk"] = 0
        lista = []
        odometros = []
        odometros_lista = []
        hoy = datetime.datetime.today().strftime("%Y-%m-%d")
        if int(id_pozo) != 0:
            pozo = Pozo.objects.get(pk=id_pozo)
            mediciones = Medicion.objects.filter(
                pozo__id=id_pozo,
                odometro__tipos__id=clave,
                fecha__gte=hoy).order_by('fecha')
            odometros = self.crea_Lista_Odometro(
                Odometro.objects.filter(tipos=clave))
            mediciones_lista = list(mediciones)
            if len(mediciones) > 0:
                fecha_inicio = mediciones[0].fecha
                fecha_fin = mediciones[len(mediciones) - 1].fecha
                lista_ordenada_fecha = self.crea_Lista_ordenada_fecha(
                    mediciones_lista)
                lista_fechas = self.crea_Lista_fechas_datetime(
                    fecha_inicio, fecha_fin)
                lista = self.crea_Lista(
                    lista_ordenada_fecha,
                    lista_fechas,
                    odometros,
                    pozo.pk)

        contexto = {
            'form': formulario_medicion,
            'pozo': pozo,
            'tipo_id': clave,
            'lista': lista,
            'odometros': odometros,
            'odometros_lista': odometros_lista,
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk, clave):

        boton = ""
        if request.POST.get('buscar'):
            boton = "buscar"
        else:
            boton = "exportar"
        nombre = request.user.get_full_name()
        puesto = request.user.profile.puesto

        formulario = MedicionesPozoFilterForm(request.POST)

        l_odometros = request.POST.getlist('odometro')
        fecha_inicio = request.POST["fecha_inicio"]
        fecha_fin = request.POST["fecha_fin"]
        tipo = request.POST.get('tipos')
        pozo_id = request.POST.get('pozo')
        id_pozo = pk

        lista = []
        odometros_lista = []
        odos = []
        odometros = []
        mediciones = []

        if int(id_pozo) == 0:
            pozo = {}
            pozo["nombre"] = "Historial de Mediciones"
            pozo["pk"] = 0
        else:
            if int(pozo_id) == 0:
                pozo = Pozo.objects.get(pk=pozo_id)
        if int(pozo_id) != 0:
            pozo = Pozo.objects.get(pk=pozo_id)
            if len(l_odometros) == 0:
                odometros = []
                l_odometros = []
                if tipo == "0":
                    odos = Odometro.objects.all()
                else:
                    odos = Odometro.objects.filter(tipos=tipo)
                for o in odos:
                    nodo = {}
                    nodo["id"] = o.pk
                    nodo["descripcion"] = o.descripcion
                    nodo["clasificacion"] = o.clasificacion
                    nodo["udm"] = o.udm.clave
                    nodo["suma"] = Decimal(0.0)
                    nodo["numero"] = Decimal(0.0)
                    nodo["promedio"] = Decimal(0.0)
                    odometros.append(nodo)
                    l_odometros.append(o.pk)

            else:
                odometros = []
                if tipo == "0":
                    odos = Odometro.objects.filter(id__in=l_odometros)
                else:
                    odos = Odometro.objects.filter(tipos=tipo)
                    l_odometros = []
                for o in odos:
                    nodo = {}
                    nodo["id"] = o.pk
                    nodo["descripcion"] = o.descripcion
                    nodo["clasificacion"] = o.clasificacion
                    nodo["udm"] = o.udm
                    nodo["suma"] = Decimal(0.0)
                    nodo["numero"] = Decimal(0.0)
                    nodo["promedio"] = Decimal(0.0)
                    odometros.append(nodo)
                    if tipo != "0":
                        l_odometros.append(o.pk)
                odometros_lista = json.dumps(
                    [int(item) for item in l_odometros])

            fecha_i = fecha_inicio + ' 00:00'
            fecha_f = fecha_fin + ' 23:59'

            mediciones = Medicion.objects.filter(
                pozo__id=pozo_id,
                odometro__id__in=l_odometros,
                fecha__gte=fecha_i,
                fecha__lte=fecha_f).order_by('fecha', 'odometro_id')

        if len(mediciones) > 0:
            if boton == "buscar":
                mediciones_lista = list(mediciones)
                lista_ordenada_fecha = self.crea_Lista_ordenada_fecha(
                    mediciones_lista)
                lista_fechas = self.crea_Lista_fechas(fecha_inicio, fecha_fin)
                lista = self.crea_Lista(
                    lista_ordenada_fecha, lista_fechas, odometros, pozo.pk)
                contexto = {
                    'form': formulario,
                    'pozo': pozo,
                    'lista': lista,
                    'odometros': odometros,
                    'odometros_lista': odometros_lista
                }
                return render(request, self.template_name, contexto)
        else:
            contexto = {
                'form': formulario,
                'pozo': pozo,
                'lista': lista,
                'odometros': odometros,
                'odometros_lista': odometros_lista
            }
            return render(request, self.template_name, contexto)

    def crea_Lista_Odometro(self, odometros):

        lista_odometros = []
        for o in odometros:
            nodo = {}
            nodo["id"] = o.pk
            nodo["descripcion"] = o.descripcion
            nodo["clasificacion"] = o.clasificacion
            nodo["udm"] = o.udm.clave
            nodo["suma"] = Decimal(0.0)
            nodo["numero"] = Decimal(0.0)
            nodo["promedio"] = Decimal(0.0)
            lista_odometros.append(nodo)
        return lista_odometros

    def crea_Lista(self, lista_ordenada_fecha, lista_fechas, odometros, id_pozo):

        lista = []
        for f in lista_fechas:
            if len(lista_ordenada_fecha) > 0:
                if f == lista_ordenada_fecha[0]["fecha"]:
                    self.crea_Registro(
                        lista,
                        odometros,
                        lista_ordenada_fecha[0]["lista_mediciones"],
                        f,
                        id_pozo)
                    lista_ordenada_fecha.remove(lista_ordenada_fecha[0])
            else:
                nodo = self.crea_Nodo_vacio(f, odometros)
                lista.append(nodo)
        return lista

    def crea_Registro(self, lista, odometros, lista_mediciones, fecha, id_pozo):
        count = 0
        tam_lista = len(lista_mediciones)
        cambios = False
        bandera = 0
        # odometros_observavciones = Odometro.objects.filter(tipos__clave="O")
        while tam_lista > 0:
            nodo = {}
            nodo["fecha"] = fecha
            nodo["id_pozo"] = id_pozo
            nodo["lista_odo"] = []
            for o in odometros:
                # for oo in odometros_observavciones:
                #     if oo.id == o["id"]:
                #         bandera = 1
                if o["clasificacion"] == "TEX":
                    bandera = 1
                while count < tam_lista and cambios is not True:
                    if o["id"] == lista_mediciones[count].odometro_id:
                        o["suma"] = o["suma"] + lista_mediciones[count].lectura
                        o["numero"] = o["numero"] + 1
                        nodo_odo = {}
                        nodo_odo["id_odo"] = o["id"]
                        nodo_odo["fecha_real"] = lista_mediciones[count].fecha
                        nodo_odo["fecha"] = lista_mediciones[
                            count].fecha.strftime("%Y-%m-%d")
                        nodo_odo["hora"] = lista_mediciones[
                            count].fecha.strftime("%H:%M")
                        if bandera == 1:
                            nodo_odo["lectura"] = lista_mediciones[
                                count].observaciones
                        else:
                            nodo_odo["lectura"] = ('%f' % lista_mediciones[
                                count].lectura).rstrip('0').rstrip('.')
                        nodo_odo["observaciones"] = lista_mediciones[
                            count].observaciones
                        nodo_odo["es_observacion"] = bandera
                        nodo_odo["id_med"] = lista_mediciones[count].id
                        nodo_odo["odometro"] = o["descripcion"]
                        nodo["lista_odo"].append(nodo_odo)
                        lista_mediciones.remove(lista_mediciones[count])
                        tam_lista = len(lista_mediciones)
                        cambios = True
                    count = count + 1
                if cambios is not True:
                    nodo_odo = {}
                    nodo_odo["id_odo"] = o["id"]
                    nodo_odo["feca_real"] = ""
                    nodo_odo["fecha"] = ""
                    nodo_odo["hora"] = ""
                    nodo_odo["lectura"] = ""
                    nodo_odo["observaciones"] = ""
                    nodo_odo["es_observacion"] = ""
                    nodo_odo["id_med"] = 0
                    nodo_odo["odometro"] = ""
                    nodo["lista_odo"].append(nodo_odo)
                count = 0
                bandera = 0
                cambios = False
            lista.append(nodo)

    def crea_Nodo_vacio(self, fecha, odometros):
        nodo = {}
        nodo["fecha"] = fecha
        nodo["lista_odo"] = []
        for o in odometros:
            nodo_odo = {}
            nodo_odo["id_odo"] = o["id"]
            nodo_odo["feca_real"] = ""
            nodo_odo["fecha"] = ""
            nodo_odo["hora"] = ""
            nodo_odo["lectura"] = ""
            nodo_odo["observaciones"] = ""
            nodo_odo["id_med"] = 0
            nodo["lista_odo"].append(nodo_odo)
        return nodo

    def crea_Lista_ordenada_fecha(self, mediciones):

        lista = []
        es_primero = True
        count = 0
        for m in mediciones:
            if es_primero:
                nodo = self.crea_Nodo_nuevo(m)
                es_primero = False
            else:
                if nodo["fecha"] == m.fecha.strftime("%Y-%m-%d"):
                    nodo["lista_mediciones"].append(m)
                else:
                    lista.append(nodo)
                    nodo = self.crea_Nodo_nuevo(m)
            count += 1
        if count > 0:
            lista.append(nodo)
        return lista

    def crea_Lista_fechas(self, fecha_inicio, fecha_fin):

        lista = []
        f_ini = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d")
        f_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d")
        while f_ini <= f_fin:
            lista.append(f_ini.strftime("%Y-%m-%d"))
            f_ini = f_ini + datetime.timedelta(days=1)
        return lista

    def crea_Lista_fechas_datetime(self, fecha_inicio, fecha_fin):

        lista = []
        while fecha_inicio <= fecha_fin:
            lista.append(fecha_inicio.strftime("%Y-%m-%d"))
            fecha_inicio = fecha_inicio + datetime.timedelta(days=1)
        return lista

    def crea_Nodo_nuevo(self, medicion):

        nodo = {}
        nodo["fecha"] = medicion.fecha.strftime("%Y-%m-%d")
        nodo["lista_mediciones"] = []
        nodo["lista_mediciones"].append(medicion)
        return nodo


class MedicionesAPI(viewsets.ModelViewSet):
    queryset = Medicion.objects.all().order_by('-fecha')
    serializer_class = MedicionSerializer
    pagination_class = GenericPagination
    filter_backends = (DjangoFilterBackend,)
    # filter_class = MedicionFilter


class CapturaMedicionView(PermissionRequiredMixin, View):
    permission_required = 'activos.agregar_mediciones'
    raise_exception = True

    def __init__(self):
        self.template_name = 'medicion/captura_mediciones.html'

    def get(self, request):
        formulario = CapturaMedcionFiltersForm()
        contexto = {
            'form': formulario
        }
        return render(request, self.template_name, contexto)

    def post(self, request):
        formulario = CapturaMedcionFiltersForm(request.POST)
        pozo_id = request.POST['pozo']
        tipo_id = int(request.POST['tipos'])

        pozo = None
        odometros = None
        lista_odometros = []
        lista_mediciones = []

        if tipo_id != 0:
            odometros = Odometro.objects.filter(tipos__id=tipo_id)
        else:
            odometros = Odometro.objects.all()
        if pozo_id != 0:
            pozo = Pozo.objects.get(pk=pozo_id)

        for o in odometros:
            lista_odometros.append(o.pk)
        ult_fechas_reg = Medicion.objects.values('odometro').annotate(
            max_fecha=Max('fecha')).order_by()
        mega_query = Q()
        for r in ult_fechas_reg:
            mega_query |= (
                Q(odometro__exact=r['odometro']) & Q(fecha=r['max_fecha']))
        resultados = Medicion.objects.filter(mega_query).filter(
            pozo=pozo_id,
            odometro__in=lista_odometros).order_by('odometro', 'fecha')
        c = 0
        cambios = False
        for o in odometros:
            while c < len(resultados) and cambios is not True:
                if o.clave == resultados[c].odometro.clave:
                    medicion = {}
                    medicion['id'] = resultados[c].pk
                    medicion['odometro_pk'] = resultados[c].odometro.pk
                    medicion['odometro'] = resultados[c].odometro.descripcion
                    medicion['odometro_udm'] = resultados[c].odometro.udm.clave
                    medicion['observaciones'] = resultados[c].observaciones
                    medicion['odometro_clasificacion'] = resultados[c].odometro.clasificacion
                    medicion['pozo_pk'] = resultados[c].pozo.pk
                    medicion['fecha'] = resultados[c].fecha.strftime('%d/%m/%Y %H:%M')
                    if resultados[c].odometro.clasificacion == 'TEX':
                        medicion['lectura'] = resultados[c].observaciones
                    if resultados[c].odometro.clasificacion == 'NUM':
                        medicion['lectura'] = resultados[c].lectura
                    lista_mediciones.append(medicion)
                    cambios = True
                c = c + 1
            cambios = False
            c = 0

        for odometro in odometros:
            r = resultados.filter(odometro=odometro).exists()
            if r is not True:
                medicion = {}
                medicion['id'] = ''
                medicion['odometro_pk'] = odometro.pk
                medicion['odometro'] = odometro.descripcion
                medicion['odometro_udm'] = odometro.udm.clave
                medicion['observaciones'] = "-"
                medicion['odometro_clasificacion'] = odometro.clasificacion
                medicion['pozo_pk'] = pozo.pk
                medicion['fecha'] = ''
                medicion['lectura'] = ''
                lista_mediciones.append(medicion)

        contexto = {
            'form': formulario,
            'pozo': pozo,
            'odometros': odometros,
            'resultados': lista_mediciones,
        }

        return render(request, self.template_name, contexto)


# ----------------- MEDICION ----------------- #


class MedicionOdometroView(View):

    def __init__(self):
        self.template_name = 'medicion/lista.html'

    def get(self, request, pk):
        formulario_medicion = MedicionForm()
        id_odometro = pk
        odometro = Odometro.objects.get(id=id_odometro)
        formulario = MedicionFiltersForm()

        contexto = {
            'formulario_medicion': formulario_medicion,
            'form': formulario,
            'id_odometro': id_odometro,
            'odometro': odometro,
        }

        return render(request, self.template_name, contexto)


class MedicionAPI(viewsets.ModelViewSet):
    queryset = Medicion.objects.all().order_by('fecha')
    serializer_class = MedicionSerializer
    pagination_class = GenericPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = MedicionFilter

    def create(self, request, *args, **kwargs):
        fecha = request.data["fecha"].split("T")[0]
        fecha = fecha + " " + request.data["fecha"].split("T")[1]
        pozo_id = request.data["pozo"]
        odo_id = request.data["odometro"]
        odometro = Odometro.objects.get(pk=odo_id)
        mediciones = Medicion.objects.filter(
            odometro__clave=odometro.clave, fecha=fecha, pozo__pk=pozo_id)
        if len(mediciones) > 0:
            partial = kwargs.pop('partial', False)
            instance = mediciones.first()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MedicionAPI2(viewsets.ModelViewSet):
    queryset = Medicion.objects.all().order_by('-fecha')
    serializer_class = MedicionSerializer
    pagination_class = GenericPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = MedicionFilter


class MedicionExcelAPI(viewsets.ModelViewSet):
    queryset = Medicion.objects.all().order_by('-fecha')
    serializer_class = MedicionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = MedicionFilter


class MedicionesTelemetria(APIView):

    def get(self, request):
        print request.data
        print "aqui tambien"

    def post(self, request):
        print request.data
        print "aqui"
        return HttpResponse("Se genero data")
        # serializer = MedicionSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------ SERVICIO A OFRECER ------------------- #


class ServicioView(View):
    def __init__(self):
        self.template_name = "servicio/lista.html"

    def get(self, request):
        formulario = ServicioForm()
        contexto = {
            'form': formulario
        }
        return render(request, self.template_name, contexto)


# ------------------ UBICACION ------------------------ #


class UbicacionListView(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_ubicacion'
    raise_exception = True

    def __init__(self):
        self.template_name = "ubicacion/lista.html"

    def get(self, request):
        formulario = UbicacionFiltersForm()
        contexto = {
            'form': formulario
        }
        return render(request, self.template_name, contexto)


class UbicacionCreateView(PermissionRequiredMixin, View):
    permission_required = 'activos.agregar_ubicacion'
    raise_exception = True

    def __init__(self):
        self.template_name = "ubicacion/formulario.html"

    def get(self, request):
        formulario = UbicacionForm()
        contexto = {
            'form': formulario,
            'operation': 'Nuevo'
        }
        return render(request, self.template_name, contexto)

    def post(self, request):
        formulario = UbicacionForm(request.POST)
        if formulario.is_valid():
            datos_formulario = formulario.cleaned_data

            ubicacion = Ubicacion()
            ubicacion.nombre = datos_formulario.get('nombre')
            ubicacion.tipo = datos_formulario.get('tipo')
            #ubicacion.clave = datos_formulario.get('clave')
            ubicacion.padre = datos_formulario.get('padre')
            ubicacion.estado = datos_formulario.get('estado')
            ubicacion.latitud = datos_formulario.get('latitud')
            ubicacion.longitud = datos_formulario.get('longitud')
            ubicacion.save()

            return redirect(reverse('activos:ubicaciones_lista'))

        contexto = {
            'form': formulario,
            'operation': 'Nuevo'
        }
        return render(request, self.template_name, contexto)


class UbicacionUpdateView(PermissionRequiredMixin, View):
    permission_required = 'activos.editar_ubicacion'
    raise_exception = True

    def __init__(self):
        self.template_name = "ubicacion/formulario.html"

    def get(self, request, pk):
        ubicacion = get_object_or_404(Ubicacion, pk=pk)
        formulario = UbicacionForm(instance=ubicacion)

        contexto = {
            'form': formulario,
            'operation': 'Editar'
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk):

        ubicacion = get_object_or_404(Ubicacion, pk=pk)

        formulario = UbicacionForm(
            request.POST,
            instance=ubicacion
        )

        if formulario.is_valid():

            ubicacion = formulario.save(commit=False)
            ubicacion.save()

            return redirect(
                reverse('activos:ubicaciones_lista')
            )

        contexto = {
            'form': formulario,
            'operation': 'Editar'
        }
        return render(request, self.template_name, contexto)


class UbicacionTreeAPI2(View):

    def get(self, request, q):

        daddies = Ubicacion.objects.filter(
            Q(nombre__icontains=q) |
            Q(clave__icontains=q) |
            Q(tipo__icontains=q)
        )

        serializador = UbicacionTreeSerializado()
        lista_json = serializador.get_Json(daddies)

        return HttpResponse(
            lista_json,
            content_type="application/json"
        )


class UbicacionByPageAPI(viewsets.ModelViewSet):
    queryset = Ubicacion.objects.all().order_by('created_date')
    serializer_class = UbicacionSerializer
    pagination_class = GenericPaginationx200
    filter_backends = (DjangoFilterBackend,)
    filter_class = UbicacionFilter


class UbicacionAPI(viewsets.ModelViewSet):
    queryset = Ubicacion.objects.all().order_by('created_date')
    serializer_class = UbicacionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = (
        'id',
        'nombre',
        # 'clave',
        'tipo',
        'latitud',
        'longitud',
        'estado',
        'padre'
    )


class UbicacionClienteAPI(viewsets.ModelViewSet):
    queryset = Ubicacion.objects.all()
    serializer_class = UbicacionClienteSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('cliente',)


class UbicacionClienteView(View):
    def __init__(self):
        self.template_name = "ubicacion/lista_by_cliente.html"

    def get(self, request, pk):
        cliente = Cliente.objects.get(pk=pk)
        formulario = UbicacionForm()
        contexto = {
            'form': formulario,
            'cliente': cliente
        }
        return render(request, self.template_name, contexto)

# ------------------ POZOS ------------------------ #


class PozoListView(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_pozos'
    raise_exception = True

    def __init__(self):
        self.template_name = "pozo/lista.html"

    # @permission_required('activos.ver_pozos', raise_exception=True)
    def get(self, request):
        # permiso = request.user.has_perm('activos.ver_pozos')
        # if request.user.is_staff or permiso:
        formulario = PozoFiltersForm()

        contexto = {
            'form': formulario
        }

        return render(request, self.template_name, contexto)
        # else:
        #     raise PermissionDenied


class PozoCreateView(PermissionRequiredMixin, View):
    permission_required = 'activos.agregar_pozos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'pozo/formulario.html'

    def obtener_UrlImagen(self, _imagen):
        imagen = ''

        if _imagen:
            imagen = _imagen.url

        return imagen

    def get(self, request):
        formulario = PozoForm()
        form_u = UbicacionForm()

        contexto = {
            'form': formulario,
            'form_u': form_u,
            'operation': 'Nuevo',
            'pozo_id': 0
        }

        return render(request, self.template_name, contexto)

    def post(self, request):
        formulario = PozoForm(request.POST)
        form_u = UbicacionForm()

        if formulario.is_valid():

            datos_formulario = formulario.cleaned_data
            pozo = Pozo()
            pozo.nombre = datos_formulario.get('nombre')
            pozo.direccion = datos_formulario.get('direccion')
            pozo.ubicacion = datos_formulario.get('ubicacion')
            pozo.ultima_intervencion = datos_formulario.get(
                'ultima_intervencion'
            )
            pozo.latitud = datos_formulario.get('latitud')
            pozo.longitud = datos_formulario.get('longitud')

            pozo.geometria = datos_formulario.get('geometria')
            pozo.fecha_inicio_perforacion = datos_formulario.get(
                'fecha_inicio_perforacion'
            )
            pozo.fecha_terminacion = datos_formulario.get(
                'fecha_terminacion')
            pozo.estado = datos_formulario.get('estado')
            pozo.comentarios = datos_formulario.get('comentarios')
            pozo.created_by = request.user.profile
            pozo.estado_mecanico = datos_formulario.get('estado_mecanico')
            url_estado_mecanico = self.obtener_UrlImagen(
                pozo.estado_mecanico)

            pozo.save()

            return redirect(reverse(
                'activos:pozos_lista')
            )

        contexto = {
            'form': formulario,
            'form_u': form_u,
            'operation': 'Nuevo',
            'estad_mecanico': url_estado_mecanico
        }

        return render(request, self.template_name, contexto)


class PozoUpdateView(PermissionRequiredMixin, View):

    permission_required = 'activos.editar_pozos'
    raise_exception = True

    def __init__(self):
        self.template_name = "pozo/formulario.html"

    def obtener_UrlImagen(self, _imagen):
        imagen = ''

        if _imagen:
            imagen = _imagen.url

        return imagen

    def get(self, request, pk):
        pozo = get_object_or_404(Pozo, pk=pk)

        formulario = PozoForm(instance=pozo)
        form_u = UbicacionForm()

        contexto = {
            'form': formulario,
            'form_u': form_u,
            'operation': 'Editar',
            'pozo_id': pk,
            'pozo': pozo,
            'estado_mecanico': self.obtener_UrlImagen(pozo.estado_mecanico)
        }
        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        pozo = get_object_or_404(Pozo, pk=pk)

        formulario = PozoForm(
            request.POST,
            request.FILES,
            instance=pozo
        )
        form_u = UbicacionForm()
        if formulario.is_valid():

            pozo = formulario.save(commit=False)
            pozo.save()

            return redirect(
                reverse('activos:pozos_lista')
            )

        contexto = {
            'form': formulario,
            'form_u': form_u,
            'operation': 'Editar',
            'estado_mecanico': self.obtener_UrlImagen(pozo.estado_mecanico)
        }
        return render(request, self.template_name, contexto)


class PozoMedicion(View):

    def __init__(self):
        self.template_name = "pozo/medicion/lista.html"

    def get(self, request, pk):

        pozo = get_object_or_404(Pozo, pk=pk)
        odometros = Odometro.objects.filter(pozos=pozo)
        # odometros = Odometro.objects.filter(pozo=pozo).exclude(clave__icontains="CONSUMO")

        if len(odometros) > 0:
            odometro = odometros.first()
        else:
            odometro = -1

        contexto = {
            'pozo': pozo,
            'odometro': odometro,
            'odometros': odometros
        }

        return render(request, self.template_name, contexto)


class PozoResumenAPI(View):

    def get(self, request, pk):

        mediciones = Medicion.objects.raw('''
            select
            *
            from
            (
                select
                medicion.id,
                DATE_FORMAT(medicion.fecha, '%d/%m/%Y') as fecha,
                pozo.q_bruto_diseno,
                pozo.q_neto_diseno,
                (select medicion.lectura where odometro.clave = "Q NETO NUVOIL") as q_neto_nuvoil,
                (select medicion.lectura where odometro.clave = "Q BRUTO NUVOIL") as q_bruto_nuvoil,
                (select medicion.lectura where odometro.clave = "Q NETO PEMEX") as q_neto_pemex,
                (select medicion.lectura where odometro.clave = "Q BRUTO PEMEX") as q_bruto_pemex,
                (select medicion.lectura where odometro.clave = "PORCENTAJE AGUA") as porcentaje_agua,
                medicion.observaciones

                from activos_medicion as medicion
                inner join activos_odometro as odometro on odometro.id = medicion.odometro_id
                inner join activos_pozo as pozo on pozo.id = %s

                           where pozo_id = %s

                           and odometro.clave in ("Q NETO NUVOIL", "Q BRUTO NUVOIL", "Q NETO PEMEX", "PORCENTAJE AGUA")

                           order by fecha asc

            ) resumen''', [pk, pk])

        data = serializers.serialize(
            'json',
            mediciones,
        )

        return HttpResponse(data, content_type='application/json')


class PozoResumenView(View):

    def __init__(self):
        self.template_name = "pozo/medicion/resumen.html"

    def get(self, request, pk):
        formulario = ProduccionFiltersForm()
        pozo = get_object_or_404(Pozo, pk=pk)

        contexto = {
            'form': formulario,
            'pozo': pozo,
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk):

        if request.POST.get('buscar'):
            boton = request.POST.get('buscar')
        else:
            boton = request.POST.get('exportar')

        if boton == "buscar":
            formulario = ProduccionFiltersForm(request.POST)
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            f_inicio = datetime.datetime.strptime(
                fecha_inicio, '%m/%d/%Y').date()
            f_fin = datetime.datetime.strptime(fecha_fin, '%m/%d/%Y').date()

            pozo = get_object_or_404(Pozo, pk=pk)
            mediciones = Medicion.objects.raw('''
            select
                    resumen.id,
                    STR_TO_DATE(resumen.fechita, %s) as fecha,
                    resumen.q_bruto_diseno,
                    resumen.q_neto_diseno,
                    sum(resumen.q_neto_nuvoil) as q_neto_nuvoil,
                    sum(resumen.q_bruto_nuvoil) as q_bruto_nuvoil,
                    sum(resumen.q_neto_pemex) as q_neto_pemex,
                    sum(resumen.porcentaje_agua) as porcentaje_agua

                from
                (
                    select
                    1 as id,
                    DATE_FORMAT(medicion.fecha, %s) as fechita,
                    pozo.q_bruto_diseno as q_bruto_diseno,
                    pozo.q_neto_diseno as q_neto_diseno,
                    (select medicion.lectura where odometro.clave = "Q NETO NUVOIL") as q_neto_nuvoil,
                    (select medicion.lectura where odometro.clave = "Q BRUTO NUVOIL") as q_bruto_nuvoil,
                    (select medicion.lectura where odometro.clave = "Q NETO PEMEX") as q_neto_pemex,
                    (select medicion.lectura where odometro.clave = "PORCENTAJE AGUA") as porcentaje_agua,
                    medicion.observaciones as observaciones

                    from activos_medicion as medicion
                    inner join activos_odometro as odometro on odometro.id = medicion.odometro_id
                    inner join activos_pozo as pozo on pozo.id = %s

                               where pozo_id = %s
                               and odometro.clave in ("Q NETO NUVOIL", "Q BRUTO NUVOIL", "Q NETO PEMEX", "PORCENTAJE AGUA")
                               and medicion.fecha >= %s
                               and medicion.fecha <= %s
                        order by fecha asc

                ) resumen
                group by
                    resumen.fechita''', ['%d/%m/%Y', '%d/%m/%Y', pk, pk, f_inicio, f_fin])

            count_records = len(list(mediciones))

            if count_records == 0:
                mediciones = None

            contexto = {
                'form': formulario,
                'pozo': pozo,
                'mediciones': mediciones
            }

            return render(request, self.template_name, contexto)

        else:
            formulario = ProduccionFiltersForm(request.POST)
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            f_inicio = datetime.datetime.strptime(
                fecha_inicio, '%m/%d/%Y').date()
            f_fin = datetime.datetime.strptime(fecha_fin, '%m/%d/%Y').date()
            obj_pozo = Pozo.objects.get(pk=pk)
            response = HttpResponse(content_type='application/ms-excel')
            response[
                'Content-Disposition'] = 'attachment; filename="reporte_produccion.xls"'

            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet(obj_pozo.nombre, cell_overwrite_ok=True)

            date_format = xlwt.XFStyle()
            date_format.num_format_str = 'dd/mm/yyyy'

            # Sheet header, first row
            row_num = 0

            font_style = xlwt.XFStyle()

            columns = [
                'Fecha',
                'Q Bruto Diseño (BPD)',
                'Q Neto Diseño (BPD)',
                'Q Bruto',
                '% Agua',
                'Q Neto',
                'Medicion',
                'Observaciones',

            ]

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()

            rows = Medicion.objects.raw('''
            select
                    resumen.id,
                    STR_TO_DATE(resumen.fechita, %s) as fecha,
                    resumen.q_bruto_diseno,
                    resumen.q_neto_diseno,
                    sum(resumen.q_neto_nuvoil) as q_neto_nuvoil,
                    sum(resumen.q_bruto_nuvoil) as q_bruto_nuvoil,
                    sum(resumen.q_neto_pemex) as q_neto_pemex,
                    sum(resumen.porcentaje_agua) as porcentaje_agua

                from
                (
                    select
                    1 as id,
                    DATE_FORMAT(medicion.fecha, %s) as fechita,
                    pozo.q_bruto_diseno as q_bruto_diseno,
                    pozo.q_neto_diseno as q_neto_diseno,
                    (select medicion.lectura where odometro.clave = "Q NETO NUVOIL") as q_neto_nuvoil,
                    (select medicion.lectura where odometro.clave = "Q BRUTO NUVOIL") as q_bruto_nuvoil,
                    (select medicion.lectura where odometro.clave = "Q NETO PEMEX") as q_neto_pemex,
                    (select medicion.lectura where odometro.clave = "PORCENTAJE AGUA") as porcentaje_agua,
                    medicion.observaciones as observaciones

                    from activos_medicion as medicion
                    inner join activos_odometro as odometro on odometro.id = medicion.odometro_id
                    inner join activos_pozo as pozo on pozo.id = %s

                               where pozo_id = %s


                               and odometro.clave in ("Q NETO NUVOIL", "Q BRUTO NUVOIL", "Q NETO PEMEX", "PORCENTAJE AGUA")
                               and medicion.fecha >= %s
                               and medicion.fecha <= %s
                        order by fecha asc

                ) resumen
                group by
                    resumen.fechita''', ['%d/%m/%Y', '%d/%m/%Y', pk, pk, f_inicio, f_fin])

            for row in rows:

                row_num += 1

                ws.write(row_num, 0, row.fecha, date_format)
                ws.write(row_num, 1, row.q_bruto_diseno, font_style)
                ws.write(row_num, 2, row.q_neto_diseno, font_style)
                ws.write(row_num, 3, row.q_bruto_nuvoil, font_style)
                ws.write(row_num, 4, row.porcentaje_agua, font_style)
                ws.write(row_num, 5, row.q_neto_nuvoil, font_style)
                ws.write(row_num, 6, row.q_neto_pemex, font_style)
                ws.write(row_num, 7, row.observaciones, font_style)

            row_num += 1
            ws.write(row_num, 0, "Promedio", font_style)
            row_num += 1
            ws.write(row_num, 7, "REVISÓ", font_style)
            row_num += 2
            ws.write(row_num, 7, "ING. EDI GABINO GOMEZ BARRA", font_style)
            row_num += 1
            ws.write(
                row_num, 7, "SUPERVISOR DE INSTALACIÓN Y OPERACIÓN", font_style)
            wb.save(response)

            return response


class PozoHistory(PermissionRequiredMixin, View):

    permission_required = 'activos.ver_historial_pozos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'pozo/historia.html'

    def get(self, request, pk):

        registros = Pozo.history.filter(id=pk).order_by("-history_date")

        contexto = {
            'operation': "Historia",
            'pozo_id': pk,
            'registros': registros
        }

        return render(request, self.template_name, contexto)


class PozoByPageAPI(viewsets.ModelViewSet):
    queryset = Pozo.objects.all().order_by('estado', "fecha_instalacion")
    serializer_class = PozoSerializer
    pagination_class = GenericPaginationx200
    filter_backends = (DjangoFilterBackend,)
    filter_class = PozoFilter


class PozoAPI(viewsets.ModelViewSet):
    queryset = Pozo.objects.all().order_by('estado', "fecha_instalacion")
    serializer_class = PozoSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PozoFilter


# ----------------- POZOS - FICHA TECNICA ----------------- #


class PozoFichaTecnica(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_ficha_tecnica'
    raise_exception = True

    def get(self, request, pk, tipo):
        if tipo == "1":
            template_name = 'pozo/ficha_tecnica.html'
        else:
            template_name = 'pozo/ficha_tecnica_print.html'
        hoy = datetime.datetime.today()
        pozo = Pozo.objects.get(pk=pk)
        mediciones = list(Medicion.objects.filter(
            pozo__id=pk,
            odometro__tipos__clave="DP").order_by('-fecha'))
        odometros = Odometro.objects.filter(
            tipos__clave="DP").order_by('tipos__clave')
        nodo = {}
        lista = []
        tam_lista_med = len(mediciones)
        cambios = False
        c = 0
        for o in odometros:
            odo_tipo = o.tipos.all()[1].clave
            nodo = {}
            nodo["clave_tipo"] = odo_tipo
            while c < tam_lista_med and cambios is not True:
                if o.clave == mediciones[c].odometro.clave:
                    lectura = (
                        '%f' % mediciones[c].lectura).rstrip('0').rstrip('.')
                    nodo["lectura"] = lectura
                    nodo["fecha"] = mediciones[c].fecha.strftime("%d/%m/%Y")
                    nodo["odometro"] = o.descripcion
                    nodo["udm"] = o.udm.descripcion
                    cambios = True
                c = c + 1
            if cambios is not True:
                lectura = ""
                nodo["lectura"] = lectura
                nodo["fecha"] = ""
                nodo["odometro"] = o.descripcion
                nodo["udm"] = o.udm.descripcion
            c = 0
            cambios = False
            lista.append(nodo)

        contexto = {
            'pozo': pozo,
            'lista': lista,
            'fecha': hoy
        }
        return render(request, template_name, contexto)


class PozoAnexoPC(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_ficha_tecnica'
    raise_exception = True

    def get(self, request, pk, tipo):
        if tipo == "1":
            template_name = 'pozo/anexo_pc.html'
        else:
            template_name = 'pozo/anexo_pc_print.html'
        hoy = datetime.datetime.today()
        pozo = Pozo.objects.get(pk=pk)
        mediciones = list(Medicion.objects.filter(
            pozo__id=pk,
            odometro__tipos__clave="DPC").order_by('-fecha'))
        odometros = Odometro.objects.filter(
            tipos__clave="DPC").order_by('tipos__clave')
        nodo = {}
        lista = []
        tam_lista_med = len(mediciones)
        cambios = False
        c = 0
        for o in odometros:
            odo_tipo = o.tipos.all()[1].clave
            nodo = {}
            nodo["clave_tipo"] = odo_tipo
            while c < tam_lista_med and cambios is not True:
                if o.clave == mediciones[c].odometro.clave:
                    lectura = (
                        '%f' % mediciones[c].lectura).rstrip('0').rstrip('.')
                    nodo["lectura"] = lectura
                    nodo["fecha"] = mediciones[c].fecha.strftime("%d/%m/%Y")
                    nodo["odometro"] = o.descripcion
                    nodo["udm"] = o.udm.descripcion
                    cambios = True
                c = c + 1
            if cambios is not True:
                lectura = ""
                nodo["lectura"] = lectura
                nodo["fecha"] = ""
                nodo["odometro"] = o.descripcion
                nodo["udm"] = o.udm.descripcion
            c = 0
            cambios = False
            lista.append(nodo)
        num_act = 0
        num_act1 = 1
        if pozo.costo_total_mxn:
            pozo.costo_total_mxn = float(pozo.costo_total_mxn)
            pozo.costo_total_mxn = (
                '%f' % pozo.costo_total_mxn).rstrip('0').rstrip('.')
        if pozo.costo_total_usd:
            pozo.costo_total_usd = float(pozo.costo_total_usd)
            pozo.costo_total_usd = (
                '%f' % pozo.costo_total_usd).rstrip('0').rstrip('.')

        if pozo.actividades_pc:
            pozo.actividades_pc = pozo.actividades_pc.split(",")
            num_act = len(pozo.actividades_pc)
            num_act1 = len(pozo.actividades_pc) + 1
        else:
            pozo.actividades_pc = []
        contexto = {
            'pozo': pozo,
            'lista': lista,
            'fecha': hoy,
            'num_act': num_act,
            'num_act1': num_act1,
        }
        return render(request, template_name, contexto)


class PozoArchivos(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_ficha_tecnica'
    raise_exception = True

    def __init__(self):
        self.template_name = 'pozo/archivos.html'

    def get(self, request, pk):
        anexos_archivo = AnexoArchivo.objects.filter(pozo=pk)
        anexos_imagen = AnexoImagen.objects.filter(pozo=pk)
        pozo = Pozo.objects.get(id=pk)
        tipo_anexos = TipoAnexo.objects.all()
        lista_ta = []
        bandera = 0
        for ta in tipo_anexos:
            for anexo in anexos_archivo:
                if bandera != 1:
                    if ta == anexo.tipo_anexo:
                        lista_ta.append(ta)
                        bandera = 1
            bandera = 0

        contexto = {
            'tipo_anexos': lista_ta,
            'pozo': pozo,
            'anexos_archivo': anexos_archivo,
            'anexos_imagen': anexos_imagen,
        }

        return render(request, self.template_name, contexto)


class PozoArchivosZip(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_ficha_tecnica'
    raise_exception = True

    def get(self, request, pk):
        anexos_archivo = AnexoArchivo.objects.filter(pozo=pk)
        # anexos_imagen = AnexoImagen.objects.filter(pozo=pk)
        pozo = Pozo.objects.get(pk=pk)
        zip_subdir = pozo.nombre
        zip_filename = "%s.zip" % zip_subdir
        s = StringIO.StringIO()
        filzip = ZipFile(s, 'w')
        for anexo in anexos_archivo:
            fdir, fname = os.path.split(anexo.archivo.url)
            zip_path = os.path.join(zip_subdir, fname)
            # super_path = os.path.join(settings.BASE_DIR, anexo.archivo.url)
            filzip.write(anexo.archivo.path, zip_path)
        # for anexo in anexos_imagen:
        #     fdir, fname = os.path.split(anexo.ruta.url)
        #     zip_path = os.path.join(zip_subdir, fname)
        #     # super_path = os.path.join(settings.BASE_DIR, anexo.archivo.url)
        #     filzip.write(anexo.ruta.path, zip_path)
        filzip.close()

        if filzip:
            respuesta = HttpResponse(
                s.getvalue(),
                content_type='application/x-zip-compressed')
            filename = zip_filename
            content = "inline; filename='%s'" % (filename)
            respuesta['Content-Disposition'] = content
            return respuesta
        else:
            return HttpResponse("No se pudo generar el Archivo ZIP")


class PozoUbicacion(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_ficha_tecnica'
    raise_exception = True

    def __init__(self):
        self.template_name = 'pozo/ubicacion.html'

    def get(self, request, pk):
        pozo = Pozo.objects.get(id=pk)
        contexto = {
            'pozo': pozo
        }

        return render(request, self.template_name, contexto)


class PozoHistoricoProduccion(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_ficha_tecnica'
    raise_exception = True

    def __init__(self):
        self.template_name = 'pozo/historico.html'

    def get(self, request, pk, tipo):
        pozo = Pozo.objects.get(id=pk)
        form = PozoHistoricoFiltersForm()

        contexto = {
            'form': form,
            'pozo': pozo,
            'tipo': tipo
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk, tipo):
        pozo = Pozo.objects.get(id=pk)
        fecha_inicio = request.POST["fecha_inicio"]
        fecha_fin = request.POST["fecha_fin"]
        if fecha_inicio and fecha_fin:
            fecha_inicio = fecha_inicio + " 00:00"
            fecha_fin = fecha_fin + " 23:59"
        is_first = False
        response = HttpResponse(content_type='application/vnd.ms-excel')
        cont_dis = "attachment; filename=Produccion %s.xlsx" % pozo.nombre
        response['Content-Disposition'] = cont_dis
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet("Detalle")
        format_title = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#D9D9D9'})
        format_title.set_text_wrap()
        format_subtitle = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        format_subtitle.set_text_wrap()
        format_number = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        format_number.set_text_wrap()
        grafica1 = workbook.add_chart({'type': 'line'})
        odometros = Odometro.objects.filter(
            clave__in=["PBR", "PA", "PNR"])
        c = 1
        f = 2
        fg = 0
        num_odos = len(odometros)
        worksheet.write(
            1, 0, "Fecha", format_subtitle)
        worksheet.merge_range(
            0, 0, 0, num_odos, pozo.nombre, format_title)
        for o in odometros:
            worksheet.write(f - 1, c, o.descripcion, format_subtitle)
            if fecha_inicio and fecha_fin:
                mediciones = Medicion.objects.filter(
                    pozo__pk=pk,
                    fecha__gte=fecha_inicio, fecha__lte=fecha_fin,
                    odometro__clave=o.clave).order_by("fecha")
            else:
                mediciones = Medicion.objects.filter(
                    pozo__pk=pk,
                    odometro__clave=o.clave).order_by("fecha")
            for m in mediciones:
                if is_first is not True:
                    fecha = m.fecha.strftime("%d/%m/%Y")
                    worksheet.write(f, 0, fecha, format_subtitle)
                worksheet.write(f, c, m.lectura, format_number)
                f = f + 1
            if is_first is not True:
                fg = f
                is_first = True
            c = c + 1
            f = 2

        grafica1.add_series({
            'values': ['Detalle', 2, 1, fg - 1, 1],
            'categories': ['Detalle', 2, 0, fg - 1, 0],
            'name': ['Detalle', 1, 1, 1, 1],
            'marker': {'type': 'diamond', 'border': {'color': '#000000'}, 'fill': {'color': '#000000'}},
            'line': {'color': '#000000'},
            'data_labels': {'series_name': False, 'position': 'above'},
        })
        grafica1.add_series({
            'values': ['Detalle', 2, 2, fg - 1, 2],
            'categories': ['Detalle', 2, 0, fg - 1, 0],
            'name': ['Detalle', 1, 2, 1, 2],
            'marker': {'type': 'diamond'},
            'y2_axis': 1,
            'marker': {'type': 'diamond', 'border': {'color': '#6EA6D7'}, 'fill': {'color': '#6EA6D7'}},
            'line': {'color': '#6EA6D7'},
            'data_labels': {'series_name': False, 'position': 'above'},
        })
        grafica1.add_series({
            'values': ['Detalle', 2, 3, fg - 1, 3],
            'categories': ['Detalle', 2, 0, fg - 1, 0],
            'name': ['Detalle', 1, 3, 1, 3],
            'marker': {'type': 'diamond'},
            'data_labels': {'series_name': False, 'position': 'above'},
            'marker': {'type': 'diamond', 'border': {'color': '#D8A835'}, 'fill': {'color': '#D8A835'}},
            'line': {'color': '#D8A835'},
        })
        grafica1.set_x_axis({'interval_unit': 10})
        grafica1.set_y2_axis({
            'name': 'Porcentaje de agua (%)'})
        grafica1.set_y_axis({
            'name': 'Producción (BPD)'.decode("utf-8")})
        grafica1.set_legend({'position': 'bottom'})
        ancho_grafica = (num_odos + 9) * 66
        grafica1.set_size({'width': ancho_grafica, 'height': 300})
        worksheet.insert_chart(2, num_odos + 3, grafica1)
        workbook.close()
        return response


class PozoHistoricoOperativo(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_ficha_tecnica'
    raise_exception = True

    def __init__(self):
        self.template_name = 'pozo/historico_ope.html'

    def get(self, request, pk):
        pozo = Pozo.objects.get(id=pk)
        form = PozoHistoricoFiltersForm()

        contexto = {
            'form': form,
            'pozo': pozo,
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        pozo = Pozo.objects.get(id=pk)
        fecha_inicio = request.POST["fecha_inicio"]
        fecha_fin = request.POST["fecha_fin"]
        if fecha_inicio and fecha_fin:
            fecha_inicio = fecha_inicio + " 00:00"
            fecha_fin = fecha_fin + " 23:59"
        is_first = False
        response = HttpResponse(content_type='application/vnd.ms-excel')
        if pozo.sistema.clave == "BCP":
            ext_aparejo = pozo.ext_aparejo
            prof_bomba = pozo.prof_bomba
            tem_referencia = pozo.tem_referencia
            cont_dis = "attachment; filename=Operacion %s.xlsx" % pozo.nombre
            response['Content-Disposition'] = cont_dis
            workbook = xlsxwriter.Workbook(response, {'in_memory': True})
            worksheet = workbook.add_worksheet("Detalle")
            format_title = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D9D9D9'})
            format_title.set_text_wrap()
            format_subtitle = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'})
            format_subtitle.set_text_wrap()
            format_number = workbook.add_format({
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'})
            format_number.set_text_wrap()
            grafica1 = workbook.add_chart({'type': 'line'})
            grafica2 = workbook.add_chart({'type': 'line'})
            odometros = Odometro.objects.filter(
                tipos__clave="ROBCP").exclude(clave="OBCP").order_by("clave")
            c = 1
            f = 2
            fg = 0
            num_odos = len(odometros)
            worksheet.write(
                1, 0, "Fecha", format_subtitle)
            worksheet.merge_range(
                0, 0, 0, num_odos + 3, pozo.nombre, format_title)
            worksheet.write(
                f - 1, num_odos + 1, "Temp de referencia", format_subtitle)
            worksheet.write(
                f - 1, num_odos + 2, "Exte aparejo", format_subtitle)
            worksheet.write(
                f - 1, num_odos + 3, "Prof de bomba", format_subtitle)
            for o in odometros:
                worksheet.write(f - 1, c, o.descripcion, format_subtitle)
                if fecha_inicio and fecha_fin:
                    mediciones = Medicion.objects.filter(
                        pozo__pk=pk,
                        fecha__gte=fecha_inicio, fecha__lte=fecha_fin,
                        odometro__clave=o.clave).order_by("fecha")
                else:
                    mediciones = Medicion.objects.filter(
                        pozo__pk=pk,
                        odometro__clave=o.clave).order_by("fecha")
                for m in mediciones:
                    if is_first is not True:
                        fecha = m.fecha.strftime("%Y-%m-%d %H:%M")
                        worksheet.write(f, 0, fecha, format_subtitle)
                        worksheet.write(
                            f, num_odos + 1, tem_referencia, format_number)
                        worksheet.write(
                            f, num_odos + 2, ext_aparejo, format_number)
                        worksheet.write(
                            f, num_odos + 3, prof_bomba, format_number)
                    worksheet.write(f, c, m.lectura, format_number)
                    f = f + 1
                if is_first is not True:
                    fg = f
                    is_first = True
                c = c + 1
                f = 2

            grafica1.add_series({
                'values': ['Detalle', 2, 7, fg - 1, 7],
                'categories': ['Detalle', 2, 0, fg - 1, 0],
                'name': ['Detalle', 1, 7, 1, 7],
                'marker': {'type': 'diamond'},
                'data_labels': {'series_name': False, 'position': 'above'},
            })
            grafica1.add_series({
                'values': ['Detalle', 2, 3, fg - 1, 3],
                'categories': ['Detalle', 2, 0, fg - 1, 0],
                'name': ['Detalle', 1, 3, 1, 3],
                'marker': {'type': 'diamond'},
                'y2_axis': 1,
                'data_labels': {'series_name': False, 'position': 'above'},
            })
            grafica1.add_series({
                'values': ['Detalle', 2, num_odos + 2, fg - 1, num_odos + 2],
                'categories': ['Detalle', 2, 0, fg - 1, 0],
                'name': ['Detalle', 1, num_odos + 2, 1, num_odos + 2],
                'marker': {'type': 'diamond'},
                'y2_axis': 1,
                'data_labels': {'series_name': False, 'position': 'above'},
            })
            grafica1.add_series({
                'values': ['Detalle', 2, num_odos + 3, fg - 1, num_odos + 3],
                'categories': ['Detalle', 2, 0, fg - 1, 0],
                'name': ['Detalle', 1, num_odos + 3, 1, num_odos + 3],
                'marker': {'type': 'diamond'},
                'y2_axis': 1,
                'data_labels': {'series_name': False, 'position': 'above'},
            })
            grafica2.add_series({
                'values': ['Detalle', 2, 1, fg - 1, 1],
                'categories': ['Detalle', 2, 0, fg - 1, 0],
                'name': ['Detalle', 1, 1, 1, 1],
                'marker': {'type': 'diamond'},
                'data_labels': {'series_name': False, 'position': 'above'},
            })
            grafica2.add_series({
                'values': ['Detalle', 2, 9, fg - 1, 9],
                'categories': ['Detalle', 2, 0, fg - 1, 0],
                'name': ['Detalle', 1, 9, 1, 9],
                'marker': {'type': 'diamond'},
                'data_labels': {'series_name': False, 'position': 'above'},
            })
            grafica2.add_series({
                'values': ['Detalle', 2, 10, fg - 1, 10],
                'categories': ['Detalle', 2, 0, fg - 1, 0],
                'name': ['Detalle', 1, 10, 1, 10],
                'marker': {'type': 'diamond'}
            })
            grafica2.add_series({
                'values': ['Detalle', 2, 8, fg - 1, 8],
                'categories': ['Detalle', 2, 0, fg - 1, 0],
                'name': ['Detalle', 1, 8, 1, 8],
                'marker': {'type': 'diamond'},
                'y2_axis': 1
            })
            grafica2.add_series({
                'values': ['Detalle', 2, num_odos + 1, fg - 1, num_odos + 1],
                'categories': ['Detalle', 2, 0, fg - 1, 0],
                'name': ['Detalle', 1, num_odos + 1, 1, num_odos + 1],
                'marker': {'type': 'diamond'},
                'y2_axis': 1
            })
            grafica1.set_x_axis({'interval_unit': 5})
            grafica2.set_x_axis({'interval_unit': 5})
            grafica1.set_y_axis({
                'name': 'Torque (Lb/Pie)'})
            grafica1.set_y2_axis({
                'name': 'Ext aparejo / Prof Bomba / Nivel Fluido (Mts)',
                'reverse': True})
            grafica2.set_y_axis({
                'name': 'Amps / Vel. del motor (RPM) / Volts'.decode('utf-8')})
            grafica2.set_y2_axis({
                'name': 'Temp. BCP / Temp. de referencia (°C)'.decode('utf-8')})
            grafica1.set_legend({'position': 'bottom'})
            grafica2.set_legend({'position': 'bottom'})
            ancho_grafica = (num_odos + 3) * 66
            grafica1.set_size({'width': ancho_grafica, 'height': 300})
            grafica2.set_size({'width': ancho_grafica, 'height': 300})
            worksheet.insert_chart(2, num_odos + 5, grafica1)
            worksheet.insert_chart(18, num_odos + 5, grafica2)
            workbook.close()
            return response
        else:
            pozo = Pozo.objects.get(id=pk)
            form = PozoHistoricoFiltersForm(request.POST)

            contexto = {
                'form': form,
                'pozo': pozo,
            }

            return render(request, self.template_name, contexto)


class PozoGraficaProduccion(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_ficha_tecnica'
    raise_exception = True

    def __init__(self):
        self.template_name = 'pozo/grafica.html'

    def get(self, request, pk, tipo):
        pozo = Pozo.objects.get(id=pk)
        form = PozoHistoricoFiltersForm()
        contexto = {
            'form': form,
            'pozo': pozo,
            'tipos': tipo
        }

        return render(request, self.template_name, contexto)


class PozoAsignaciones(PermissionRequiredMixin, View):

    permission_required = 'activos.ver_ficha_tecnica'
    raise_exception = True

    def __init__(self):
        self.template_name = "pozo/asignaciones.html"

    def get(self, request, pk):
        pozo = get_object_or_404(Pozo, pk=pk)

        contexto = {
            "pozo": pozo
        }

        return render(request, self.template_name, contexto)


class PozoEquipoTreeAPI(View):

    def get(self, request, pk):
        asignaciones = Asignacion.objects.filter(pozo__id=pk)
        print asignaciones
        equipos = []
        for a in asignaciones:
            equipos.append(a.equipo.id)
        daddies = Equipo.objects.filter(pk__in=equipos)

        serializador = EquipoTreeSerilizado()
        lista_json = serializador.get_Json(daddies)

        return HttpResponse(
            lista_json,
            content_type="application/json"
        )


class PozoUbicacionPI(viewsets.ModelViewSet):

    queryset = Pozo.objects.all()
    serializer_class = PozoSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id',)

    def list(self, request, *args, **kwargs):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)

        latitud = str(serializer.data[0].items()[5][1])
        longitud = str(serializer.data[0].items()[6][1])

        lista = []
        nodo = collections.OrderedDict()
        nodo["latitud"] = 0
        nodo["longitud"] = 0
        if len(latitud) > 0 and len(longitud) > 0:
            latitud_decimal = self.parse_coordenadas_to_decimal(latitud, 0)
            longitud_decimal = self.parse_coordenadas_to_decimal(
                longitud, 1)
            nodo["latitud"] = latitud_decimal
            nodo["longitud"] = longitud_decimal
        lista.append(nodo)

        return Response(lista)

    def parse_coordenadas_to_decimal(self, latitud, tipo):

        grados_la = latitud.split("°")[0]
        latitud = latitud.replace(grados_la + "°", "")
        minutos_la = latitud.split("'")[0]
        latitud = latitud.replace(minutos_la + "'", "").replace('"', "")
        latitud = latitud.replace("N", "").replace("O", "")
        segundos_la = latitud.split("''")[0]
        latitud = latitud.replace(segundos_la + "''", "")
        grados_la = Decimal(grados_la)
        minutos_la = Decimal(minutos_la)
        segundos_la = Decimal(segundos_la)
        latitud_decimal = grados_la + (minutos_la / 60) + (segundos_la / 3600)
        if tipo == 1:
            latitud_decimal = latitud_decimal * -1
        return latitud_decimal


class PozoHistoricoOpeDiaAPI(viewsets.ModelViewSet):
    queryset = Medicion.objects.all().order_by('fecha')
    serializer_class = MedicionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = MedicionFilter

    def list(self, request, *args, **kwargs):
        lista = []
        odometros = []
        is_first = False
        queryset = self.filter_queryset(self.get_queryset())
        if request.query_params:
            if request.query_params['pozo']:
                id_pozo = int(request.query_params['pozo'])
                pozo = Pozo.objects.get(pk=id_pozo)
                if pozo.sistema:
                    if pozo.sistema.clave == "BCP":
                        odometros = Odometro.objects.filter(
                            clave__in=["T", "NDF"])
        if odometros:
            for o in odometros:
                if is_first is not True:
                    nodo_pb = {}
                    nodo_pb["name"] = "Prof bomba"
                    nodo_pb["data"] = []
                    nodo_pb["marker"] = {}
                    nodo_pb["marker"]["enabled"] = True
                    nodo_pb["marker"]["radius"] = 3
                    nodo_ea = {}
                    nodo_ea["name"] = "Ext aparejo"
                    nodo_ea["data"] = []
                    nodo_ea["marker"] = {}
                    nodo_ea["marker"]["enabled"] = True
                    nodo_ea["marker"]["radius"] = 3
                    pb = pozo.prof_bomba
                    ea = pozo.ext_aparejo
                nodo = {}
                nodo["name"] = o.descripcion
                nodo["data"] = []
                nodo["marker"] = {}
                nodo["marker"]["enabled"] = True
                nodo["marker"]["radius"] = 3
                if o.clave == "T":
                    nodo["yAxis"] = 1
                mediciones = queryset.filter(
                    odometro__clave=o.clave)
                for m in mediciones:
                    fecha = time.mktime(m.fecha.timetuple()) * 1000
                    datos = []
                    datos.append(fecha)
                    datos.append(m.lectura)
                    nodo["data"].append(datos)
                    if is_first is not True:
                        datos_pb = []
                        datos_pb.append(fecha)
                        datos_pb.append(pb)
                        datos_ea = []
                        datos_ea.append(fecha)
                        datos_ea.append(ea)
                        nodo_pb["data"].append(datos_pb)
                        nodo_ea["data"].append(datos_ea)
                if is_first is not True:
                    is_first = True
                    lista.append(nodo_pb)
                    lista.append(nodo_ea)
                lista.append(nodo)

        return Response(lista)


class PozoHistoricoOpeDiaAPI2(viewsets.ModelViewSet):
    queryset = Medicion.objects.all().order_by('fecha')
    serializer_class = MedicionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = MedicionFilter

    def list(self, request, *args, **kwargs):
        lista = []
        odometros = []
        is_first = False
        queryset = self.filter_queryset(self.get_queryset())
        if request.query_params:
            if request.query_params['pozo']:
                id_pozo = int(request.query_params['pozo'])
                pozo = Pozo.objects.get(pk=id_pozo)
                if pozo.sistema:
                    if pozo.sistema.clave == "BCP":
                        odometros = Odometro.objects.filter(
                            clave__in=["AMP", "VDM", "V", "TLD"])
        for o in odometros:
            if is_first is not True:
                nodo_tr = {}
                nodo_tr["name"] = "Temp de referencia"
                nodo_tr["data"] = []
                nodo_tr["marker"] = {}
                nodo_tr["marker"]["enabled"] = True
                nodo_tr["marker"]["radius"] = 3
                tr = pozo.tem_referencia
            nodo = {}
            nodo["name"] = o.descripcion
            nodo["data"] = []
            nodo["marker"] = {}
            nodo["marker"]["enabled"] = True
            nodo["marker"]["radius"] = 3
            if o.clave == "V" or o.clave == "AMP" or o.clave == "VDM":
                    nodo["yAxis"] = 1
            mediciones = queryset.filter(
                odometro__clave=o.clave)
            for m in mediciones:
                fecha = time.mktime(m.fecha.timetuple()) * 1000
                datos = []
                datos.append(fecha)
                datos.append(m.lectura)
                nodo["data"].append(datos)
                if is_first is not True:
                    datos_tr = []
                    datos_tr.append(fecha)
                    datos_tr.append(tr)
                    nodo_tr["data"].append(datos_tr)
            if is_first is not True:
                is_first = True
                lista.append(nodo_tr)
            lista.append(nodo)
        return Response(lista)


class PozoHistoricoOpeDiaByPageAPI(viewsets.ModelViewSet):
    queryset = Medicion.objects.filter(
        odometro__tipos__clave="ROBCP").exclude(
        odometro__clave="OBCP").order_by('fecha')
    serializer_class = MedicionSerializer
    pagination_class = GenericPaginationx110
    filter_backends = (DjangoFilterBackend,)
    filter_class = MedicionFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            lista = []
            size_data = len(serializer.data)
            if size_data > 0:
                fecha_inicio = serializer.data[0].items()[4][1]
                fecha_fin = serializer.data[size_data - 1].items()[4][1]
                lista = self.crea_Lista(
                    fecha_inicio, fecha_fin, serializer.data)
            return self.get_paginated_response(lista)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def crea_Lista(self, fecha_inicio, fecha_fin, datos):
        lista = []
        fecha_inicio = fecha_inicio.split("T")[0]
        fecha_fin = fecha_fin.split("T")[0]
        f_ini = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d")
        f_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d")
        lista_ord_fecha = self.crea_Lista_ordenada_fecha(datos)
        num_datos = len(lista_ord_fecha)
        while f_ini <= f_fin:
            if num_datos > 0:
                fecha = lista_ord_fecha[0]["fecha"]
                if f_ini.strftime("%Y-%m-%d") == fecha:
                    self.crea_Registro(
                        lista,
                        lista_ord_fecha[0]["lista_mediciones"],
                        f_ini.strftime("%Y-%m-%d"))
                    lista_ord_fecha.remove(lista_ord_fecha[0])
                    num_datos = len(lista_ord_fecha)
            f_ini = f_ini + datetime.timedelta(days=1)
        return lista

    def crea_Lista_ordenada_fecha(self, mediciones):

        lista = []
        es_primero = True
        count = 0
        for m in mediciones:
            if es_primero:
                nodo = self.crea_Nodo_nuevo(m)
                es_primero = False
            else:
                fecha = m.items()[4][1].split("T")[0]
                fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
                if nodo["fecha"] == fecha.strftime("%Y-%m-%d"):
                    nodo["lista_mediciones"].append(m)
                else:
                    lista.append(nodo)
                    nodo = self.crea_Nodo_nuevo(m)
            count += 1
        if count > 0:
            lista.append(nodo)
        return lista

    def crea_Nodo_nuevo(self, medicion):
        nodo = {}
        fecha = medicion.items()[4][1].split("T")[0]
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
        nodo["fecha"] = fecha.strftime("%Y-%m-%d")
        nodo["lista_mediciones"] = []
        nodo["lista_mediciones"].append(medicion)
        return nodo

    def crea_Registro(self, lista, lista_mediciones, fecha):
        odometros = Odometro.objects.filter(
            tipos__clave="ROBCP").exclude(clave="OBCP")
        # odometros_diseno = Odometro.objects.filter(clave__in=["PBD", "PND"])
        count = 0
        tam_lista = len(lista_mediciones)
        cambios = False
        lista_nodo = []
        is_first = False
        # import ipdb
        while tam_lista > 0:
            # lista_nodo.append(('fecha', fecha))
            for o in odometros:
                while count < tam_lista and cambios is not True:
                    # ipdb.set_trace()
                    if o.id == lista_mediciones[count].items()[2][1]:
                        if is_first is not True:
                            fecha_m1 = lista_mediciones[count].items()[4][1].split("T")[0] + " " +lista_mediciones[count].items()[4][1].split("T")[1][:5]
                            lista_nodo.append(('fecha', fecha_m1))
                            is_first = True
                        clave = str(o.clave)
                        # lectura = int(lista_mediciones[count].items()[5][1])
                        lectura = float(lista_mediciones[count].items()[5][1])
                        lectura = ('%f' % lectura).rstrip('0').rstrip('.')
                        # lectura = int(lectura)
                        lista_nodo.append((clave, lectura))
                        lista_mediciones.remove(lista_mediciones[count])
                        tam_lista = len(lista_mediciones)
                        cambios = True
                    count = count + 1
                count = 0
                cambios = False
            is_first = False
            nodo = collections.OrderedDict(lista_nodo)
            lista.append(nodo)
            # import ipdb
            # ipdb.set_trace()


class PozoHistoricoDiaAPI(viewsets.ModelViewSet):
    queryset = Medicion.objects.filter(
        odometro__clave__in=["PBR", "PNR", "PA"]).order_by('fecha')
    serializer_class = MedicionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = MedicionFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        lista = []
        size_data = len(serializer.data)
        if size_data > 0:
            fecha_inicio = serializer.data[0].items()[4][1]
            fecha_fin = serializer.data[size_data - 1].items()[4][1]
            lista = self.crea_Lista(
                fecha_inicio, fecha_fin, serializer.data)
        return Response(lista)

    def crea_Lista(self, fecha_inicio, fecha_fin, datos):
        lista = []
        fecha_inicio = fecha_inicio.split("T")[0]
        fecha_fin = fecha_fin.split("T")[0]
        f_ini = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d")
        f_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d")
        lista_ord_fecha = self.crea_Lista_ordenada_fecha(datos)
        num_datos = len(lista_ord_fecha)
        while f_ini <= f_fin:
            if num_datos > 0:
                fecha = lista_ord_fecha[0]["fecha"]
                if f_ini.strftime("%Y-%m-%d") == fecha:
                    self.crea_Registro(
                        lista,
                        lista_ord_fecha[0]["lista_mediciones"],
                        f_ini.strftime("%Y-%m-%d"))
                    lista_ord_fecha.remove(lista_ord_fecha[0])
                    num_datos = len(lista_ord_fecha)
            f_ini = f_ini + datetime.timedelta(days=1)
        return lista

    def crea_Lista_ordenada_fecha(self, mediciones):

        lista = []
        es_primero = True
        count = 0
        for m in mediciones:
            if es_primero:
                nodo = self.crea_Nodo_nuevo(m)
                es_primero = False
            else:
                fecha = m.items()[4][1].split("T")[0]
                fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
                if nodo["fecha"] == fecha.strftime("%Y-%m-%d"):
                    nodo["lista_mediciones"].append(m)
                else:
                    lista.append(nodo)
                    nodo = self.crea_Nodo_nuevo(m)
            count += 1
        if count > 0:
            lista.append(nodo)
        return lista

    def crea_Nodo_nuevo(self, medicion):
        nodo = {}
        fecha = medicion.items()[4][1].split("T")[0]
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
        nodo["fecha"] = fecha.strftime("%Y-%m-%d")
        nodo["lista_mediciones"] = []
        nodo["lista_mediciones"].append(medicion)
        return nodo

    def crea_Registro(self, lista, lista_mediciones, fecha):
        odometros = Odometro.objects.filter(clave__in=["PBR", "PNR", "PA"])
        odometros_diseno = Odometro.objects.filter(clave__in=["PBD", "PND"])
        count = 0
        tam_lista = len(lista_mediciones)
        cambios = False
        lista_nodo = []
        # import ipdb
        while tam_lista > 0:
            lista_nodo.append(('fecha', fecha))
            for o in odometros:
                while count < tam_lista and cambios is not True:
                    # ipdb.set_trace()
                    if o.id == lista_mediciones[count].items()[2][1]:
                        clave = str(o.clave)
                        # lectura = int(lista_mediciones[count].items()[5][1])
                        lectura = float(lista_mediciones[count].items()[5][1])
                        # lectura = ('%f' % lectura).rstrip('0').rstrip('.')
                        lectura = int(lectura)
                        lista_nodo .append((clave, lectura))
                        lista_mediciones.remove(lista_mediciones[count])
                        tam_lista = len(lista_mediciones)
                        cambios = True
                    count = count + 1
                count = 0
                cambios = False
            nodo = collections.OrderedDict(lista_nodo)
            lista.append(nodo)
            # ipdb.set_trace()


class PozoHistoricoDiaByPageAPI(viewsets.ModelViewSet):
    queryset = Medicion.objects.filter(
        odometro__clave__in=["PBR", "PNR", "PA"]).order_by('fecha')
    serializer_class = MedicionSerializer
    pagination_class = GenericPagination2
    filter_backends = (DjangoFilterBackend,)
    filter_class = MedicionFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            lista = []
            size_data = len(serializer.data)
            if size_data > 0:
                fecha_inicio = serializer.data[0].items()[4][1]
                fecha_fin = serializer.data[size_data - 1].items()[4][1]
                lista = self.crea_Lista(
                    fecha_inicio, fecha_fin, serializer.data)
            return self.get_paginated_response(lista)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def crea_Lista(self, fecha_inicio, fecha_fin, datos):
        lista = []
        fecha_inicio = fecha_inicio.split("T")[0]
        fecha_fin = fecha_fin.split("T")[0]
        f_ini = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d")
        f_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d")
        lista_ord_fecha = self.crea_Lista_ordenada_fecha(datos)
        num_datos = len(lista_ord_fecha)
        while f_ini <= f_fin:
            if num_datos > 0:
                fecha = lista_ord_fecha[0]["fecha"]
                if f_ini.strftime("%Y-%m-%d") == fecha:
                    self.crea_Registro(
                        lista,
                        lista_ord_fecha[0]["lista_mediciones"],
                        f_ini.strftime("%Y-%m-%d"))
                    lista_ord_fecha.remove(lista_ord_fecha[0])
                    num_datos = len(lista_ord_fecha)
            f_ini = f_ini + datetime.timedelta(days=1)
        return lista

    def crea_Lista_ordenada_fecha(self, mediciones):

        lista = []
        es_primero = True
        count = 0
        for m in mediciones:
            if es_primero:
                nodo = self.crea_Nodo_nuevo(m)
                es_primero = False
            else:
                fecha = m.items()[4][1].split("T")[0]
                fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
                if nodo["fecha"] == fecha.strftime("%Y-%m-%d"):
                    nodo["lista_mediciones"].append(m)
                else:
                    lista.append(nodo)
                    nodo = self.crea_Nodo_nuevo(m)
            count += 1
        if count > 0:
            lista.append(nodo)
        return lista

    def crea_Nodo_nuevo(self, medicion):
        nodo = {}
        fecha = medicion.items()[4][1].split("T")[0]
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
        nodo["fecha"] = fecha.strftime("%Y-%m-%d")
        nodo["lista_mediciones"] = []
        nodo["lista_mediciones"].append(medicion)
        return nodo

    def crea_Registro(self, lista, lista_mediciones, fecha):
        odometros = Odometro.objects.filter(clave__in=["PBR", "PNR", "PA"])
        odometros_diseno = Odometro.objects.filter(clave__in=["PBD", "PND"])
        count = 0
        tam_lista = len(lista_mediciones)
        cambios = False
        lista_nodo = []
        # import ipdb
        while tam_lista > 0:
            lista_nodo.append(('fecha', fecha))
            for o in odometros:
                while count < tam_lista and cambios is not True:
                    # ipdb.set_trace()
                    if o.id == lista_mediciones[count].items()[2][1]:
                        clave = str(o.clave)
                        # lectura = int(lista_mediciones[count].items()[5][1])
                        lectura = float(lista_mediciones[count].items()[5][1])
                        # lectura = ('%f' % lectura).rstrip('0').rstrip('.')
                        lectura = int(lectura)
                        lista_nodo .append((clave, lectura))
                        lista_mediciones.remove(lista_mediciones[count])
                        tam_lista = len(lista_mediciones)
                        cambios = True
                    count = count + 1
                count = 0
                cambios = False
            nodo = collections.OrderedDict(lista_nodo)
            lista.append(nodo)
            # ipdb.set_trace()


class PozoHistoricoMesAPI(viewsets.ModelViewSet):
    queryset = Medicion.objects.filter(
        odometro__clave__in=["PBR", "PNR", "PA"]).order_by('fecha')
    serializer_class = MedicionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = MedicionFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        lista = []
        fecha_inicio = datetime.datetime.today().strftime("%Y-%m-%d")
        fecha_fin = datetime.datetime.today().strftime("%Y-%m-%d")
        if request.query_params:
            if request.query_params['fecha_inicio']:
                fecha_inicio = request.query_params['fecha_inicio']
        if request.query_params:
            if request.query_params['fecha_fin']:
                fecha_fin = request.query_params['fecha_fin']
        size_data = len(serializer.data)
        if size_data > 0:
            lista = self.crea_Lista(
                fecha_inicio, fecha_fin, serializer.data, size_data)
        return Response(lista)

    def crea_Lista(self, fecha_inicio, fecha_fin, datos, num_datos):
        odometros = Odometro.objects.filter(clave__in=["PBR", "PNR", "PA"])
        lista_odometros = []
        for o in odometros:
            nodo = {}
            nodo["id"] = o.id
            nodo["clave"] = o.clave
            nodo["suma"] = 0.0
            nodo["num"] = 0
            lista_odometros.append(nodo)
        lista = []
        f_ini = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d")
        f_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d")
        promedio = 0
        while f_ini < f_fin and num_datos > 0:
            lista_nodo = []
            f_fin_mes = self.add_months(f_ini, 1)
            fecha = datos[0].items()[4][1].split("T")[0]
            fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
            while fecha <= f_fin_mes and num_datos > 0:
                for o in lista_odometros:
                    if o["id"] == datos[0].items()[2][1]:
                        o["suma"] = o["suma"] + float(datos[0].items()[5][1])
                        o["num"] = o["num"] + 1
                datos.remove(datos[0])
                num_datos = len(datos)
                if num_datos > 0:
                    fecha = datos[0].items()[4][1].split("T")[0]
                    fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
            lista_nodo.append(('fecha', f_fin_mes.strftime("%Y-%m-%d")))
            for o in lista_odometros:
                if o["suma"] != 0 and o["num"] != 0:
                    promedio = o["suma"] / o["num"]
                lista_nodo.append((o["clave"], int(promedio)))
                o["suma"] = 0.0
                o["num"] = 0
                promedio = 0
            nodo = collections.OrderedDict(lista_nodo)
            lista.append(nodo)
            f_ini = self.add_months(f_ini, 1)
        return lista

    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return datetime.datetime(year, month, day)


class PozoHistoricoAnioAPI(viewsets.ModelViewSet):
    queryset = Medicion.objects.filter(
        odometro__clave__in=["PBR", "PNR", "PA"]).order_by('fecha')
    serializer_class = MedicionSerializer
    # pagination_class = GenericPagination2
    filter_backends = (DjangoFilterBackend,)
    filter_class = MedicionFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        lista = []
        fecha_inicio = datetime.datetime.today().strftime("%Y-%m-%d")
        fecha_fin = datetime.datetime.today().strftime("%Y-%m-%d")
        if request.query_params:
            if request.query_params['fecha_inicio']:
                fecha_inicio = request.query_params['fecha_inicio']
        if request.query_params:
            if request.query_params['fecha_fin']:
                fecha_fin = request.query_params['fecha_fin']
        size_data = len(serializer.data)
        if size_data > 0:
            lista = self.crea_Lista(
                fecha_inicio, fecha_fin, serializer.data, size_data)
        return Response(lista)

    def crea_Lista(self, fecha_inicio, fecha_fin, datos, num_datos):
        odometros = Odometro.objects.filter(clave__in=["PBR", "PNR", "PA"])
        lista_odometros = []
        for o in odometros:
            nodo = {}
            nodo["id"] = o.id
            nodo["clave"] = o.clave
            nodo["suma"] = 0.0
            nodo["num"] = 0
            lista_odometros.append(nodo)
        lista = []
        f_ini = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d")
        f_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d")
        promedio = 0
        while f_ini < f_fin and num_datos > 0:
            lista_nodo = []
            f_fin_anio = self.add_months(f_ini, 12)
            print f_fin_anio
            fecha = datos[0].items()[4][1].split("T")[0]
            fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
            while fecha <= f_fin_anio and num_datos > 0:
                for o in lista_odometros:
                    if o["id"] == datos[0].items()[2][1]:
                        o["suma"] = o["suma"] + float(datos[0].items()[5][1])
                        o["num"] = o["num"] + 1
                datos.remove(datos[0])
                num_datos = len(datos)
                if num_datos > 0:
                    fecha = datos[0].items()[4][1].split("T")[0]
                    fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")
            lista_nodo.append(('fecha', f_fin_anio.strftime("%Y-%m-%d")))
            for o in lista_odometros:
                if o["suma"] != 0 and o["num"] != 0:
                    promedio = o["suma"] / o["num"]
                lista_nodo.append((o["clave"], int(promedio)))
                o["suma"] = 0.0
                o["num"] = 0
                promedio = 0
            nodo = collections.OrderedDict(lista_nodo)
            lista.append(nodo)
            f_ini = self.add_months(f_ini, 12)
        return lista

    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return datetime.datetime(year, month, day)


# ----------------- POZO - ANEXO ----------------- #


class PozoAnexoTextoView(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_anexos_pozos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'pozo/anexos/anexos_texto.html'

    def get(self, request, pk):
        id_pozo = pk
        anexos = AnexoTexto.objects.filter(pozo=id_pozo)
        pozo = Pozo.objects.get(id=id_pozo)
        form = AnexoTextoForm()

        contexto = {
            'form': form,
            'id': id_pozo,
            'pozo': pozo,
            'anexos': anexos,
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        id_pozo = pk
        form = AnexoTextoForm(request.POST)
        anexos = AnexoTexto.objects.filter(pozo=id_pozo)
        pozo = Pozo.objects.get(id=id_pozo)

        if form.is_valid():
            texto = form.save(commit=False)
            texto.pozo_id = id_pozo
            texto.save()
            anexos = AnexoTexto.objects.filter(pozo=id_pozo)
            form = AnexoTextoForm()
        return render(request, 'pozo/anexos/anexos_texto.html',
                      {'form': form, 'id': id_pozo, 'anexos': anexos,
                       'pozo': pozo})


class PozoAnexoImagenView(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_anexos_pozos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'pozo/anexos/anexos_imagen.html'

    def get(self, request, pk):
        id_pozo = pk
        anexos = AnexoImagen.objects.filter(pozo=id_pozo)
        pozo = Pozo.objects.get(id=id_pozo)
        form = AnexoImagenForm()

        contexto = {
            'form': form,
            'id': id_pozo,
            'pozo': pozo,
            'anexos': anexos,
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        id_pozo = pk
        anexos = AnexoImagen.objects.filter(pozo=id_pozo)
        pozo = Pozo.objects.get(id=id_pozo)
        form = AnexoImagenForm(request.POST, request.FILES)

        if form.is_valid():

            imagen_anexo = AnexoImagen()
            imagen_anexo.descripcion = request.POST['descripcion']
            if 'ruta' in request.POST:
                imagen_anexo.ruta = request.POST['ruta']
            else:
                imagen_anexo.ruta = request.FILES['ruta']
            imagen_anexo.pozo_id = id_pozo
            imagen_anexo.save()
            anexos = AnexoImagen.objects.filter(pozo=id_pozo)
            form = AnexoImagenForm()
        contexto = {
            'form': form,
            'id': id_pozo,
            'pozo': pozo,
            'anexos': anexos,
        }
        return render(request, self.template_name, contexto)


class PozoAnexoArchivoView(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_anexos_pozos'
    raise_exception = True

    def __init__(self):
        self.template_name = 'pozo/anexos/anexos_archivo.html'

    def get(self, request, pk):
        id_pozo = pk
        anexos = AnexoArchivo.objects.filter(pozo=id_pozo)
        pozo = Pozo.objects.get(id=id_pozo)
        form = AnexoArchivoForm()
        form_t = TipoAnexoForm()

        contexto = {
            'form': form,
            'form_t': form_t,
            'id': id_pozo,
            'pozo': pozo,
            'anexos': anexos,
        }

        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        id_pozo = pk
        pozo = Pozo.objects.get(id=id_pozo)
        form = AnexoArchivoForm(request.POST, request.FILES)
        anexos = AnexoArchivo.objects.filter(pozo=id_pozo)

        if form.is_valid():
            archivo_anexo = AnexoArchivo()
            archivo_anexo.descripcion = request.POST['descripcion']
            if 'archivo' in request.POST:
                archivo_anexo.archivo = request.POST['archivo']
            else:
                archivo_anexo.archivo = request.FILES['archivo']
            archivo_anexo.pozo_id = id_pozo
            archivo_anexo.tipo_anexo_id = request.POST['tipo_anexo']
            archivo_anexo.save()
            anexos = AnexoArchivo.objects.filter(pozo=id_pozo)
            form = AnexoArchivoForm()

        contexto = {
            'form': form,
            'id': id_pozo,
            'pozo': pozo,
            'anexos': anexos,
        }

        return render(request, self.template_name, contexto)


class PozoAnexoTextoAPI(viewsets.ModelViewSet):
    queryset = AnexoTexto.objects.all()
    serializer_class = AnexoTextoSerializer
    pagination_class = GenericPagination


class PozoAnexoArchivoAPI(viewsets.ModelViewSet):
    queryset = AnexoArchivo.objects.all()
    serializer_class = AnexoArchivoSerializer
    pagination_class = GenericPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('pozo',)


class PozoAnexoImagenAPI(viewsets.ModelViewSet):
    queryset = AnexoImagen.objects.all()
    serializer_class = AnexoImagenSerializer
    pagination_class = GenericPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('pozo',)

# ----------------- ASIGNACIONES ------------------ #


class AsignacionListView(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_asignaciones'
    raise_exception = True

    def __init__(self):
        self.template_name = 'asignacion/lista.html'

    def get(self, request, pozo, equipo):

        valores_iniciales = {}

        if pozo != 0:
            valores_iniciales['pozo'] = pozo

        if equipo != 0:
            valores_iniciales['equipo'] = equipo

            formulario = AsignacionFiltersForm(initial=valores_iniciales)

            contexto = {
                'form': formulario
            }

            return render(request, self.template_name, contexto)


class AsignacionCreateView(PermissionRequiredMixin, View):
    permission_required = 'activos.agregar_asignaciones'
    raise_exception = True

    def __init__(self):
        self.template_name = "asignacion/formulario.html"

    def get(self, request, pozo):
        pozo = get_object_or_404(Pozo, pk=pozo)
        formulario = AsignacionForm2()
        contexto = {
            'form': formulario,
            'pozo': pozo,
            'operation': 'Nuevo'
        }
        return render(request, self.template_name, contexto)

    def post(self, request, pozo):
        inst_pozo = get_object_or_404(Pozo, pk=pozo)
        lista = []
        equipos = request.POST.getlist('equipos')
        for equipo in equipos:
            inst_equipo = Equipo.objects.get(id=equipo)
            asignacion = Asignacion.objects.filter(
                pozo=inst_pozo,
                equipo=inst_equipo
            )
            if len(asignacion) != 0:
                lista.append(inst_equipo)
            else:
                Asignacion.objects.create(
                    pozo=inst_pozo, equipo=inst_equipo)

        return redirect(
            reverse('activos:asignaciones_lista',
                    kwargs={'pozo': pozo, 'equipo': 0})
        )


class AsignacionByPageAPI(viewsets.ModelViewSet):
    queryset = Asignacion.objects.all().order_by('pk')
    serializer_class = AsignacionSerializer
    pagination_class = GenericPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('pozo', 'equipo')


class AsignacionAPI(viewsets.ModelViewSet):
    queryset = Asignacion.objects.all().order_by('pk')
    serializer_class = AsignacionSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('pozo', 'equipo')


class AsignacionHistory(PermissionRequiredMixin, View):

    permission_required = 'activos.ver_historial_asignaciones'
    raise_exception = True

    def __init__(self):
        self.template_name = 'asignacion/historia.html'

    def get(self, request, pozo):
        pozo = Pozo.objects.get(pk=pozo)
        registros = Asignacion.history.filter(
            pozo=pozo,
        ).order_by("-history_date")

        contexto = {
            'operation': "Historia",
            'pozo_id': pozo,
            'registros': registros,
            'pozo': pozo
        }

        return render(request, self.template_name, contexto)


class AsignacionHistoryAPI(viewsets.ModelViewSet):
    queryset = Asignacion.history.all()
    serializer_class = AsignacionHistorySerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('pozo', 'equipo', 'history_type')


# ----------------- SISTEMA ------------------ #

class SistemaListView(PermissionRequiredMixin, TemplateView):
    permission_required = 'activos.ver_sistemas'
    raise_exception = True
    template_name = 'sistema/lista.html'


class SistemaCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'activos.agregar_sistemas'
    raise_exception = True

    model = Sistema
    form_class = SistemaForm
    template_name = 'sistema/formulario.html'
    success_url = reverse_lazy('activos:sistemas_lista')
    operation = "Nueva"

    def get_context_data(self, **kwargs):
        contexto = super(
            SistemaCreateView,
            self
        ).get_context_data(**kwargs)
        contexto['operation'] = self.operation
        return contexto


class SistemaUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'activos.editar_sistemas'
    raise_exception = True

    model = Sistema
    form_class = SistemaForm
    template_name = 'sistema/formulario.html'
    success_url = reverse_lazy('activos:sistemas_lista')
    operation = "Editar"

    def get_context_data(self, **kwargs):
        contexto = super(
            SistemaUpdateView,
            self
        ).get_context_data(**kwargs)
        contexto['operation'] = self.operation
        return contexto


class SistemaAPI(viewsets.ModelViewSet):
    queryset = Sistema.objects.all()
    serializer_class = SistemaSerializer

    filter_backends = (filters.SearchFilter,)
    search_fields = ('clave', 'descripcion',)


class SistemaAPI2(viewsets.ModelViewSet):
    queryset = Sistema.objects.all()
    serializer_class = SistemaSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id',)


# ----------------- REPORTES ------------------ #


class reportesView(PermissionRequiredMixin, View):
    permission_required = 'activos.ver_mediciones'
    raise_exception = True

    def __init__(self):
        self.template_name = 'reportes/reportes.html'

    def get(self, request):
        formulario = ReportesFiltersForm()
        contexto = {
            'form': formulario
        }
        return render(request, self.template_name, contexto)

    def post(self, request):

        # Formulario
        formulario = ReportesFiltersForm(request.POST)
        # Obtiene los datos de formulario
        fecha = request.POST["fecha"]
        id_tipo = request.POST["tipo"]
        id_contrato = request.POST["contrato"]
        # se obtiene el tipo, ubicacion y contrato
        tipo = TipoOdometro.objects.get(pk=id_tipo)
        contrato = Contrato.objects.get(pk=id_contrato)
        # se establece la fecha inicial y final del mes
        fecha_inicio = datetime.datetime.strptime(fecha, "%Y-%m")
        fecha_fin = self.add_months(fecha_inicio, 1)
        fecha_fin = fecha_fin - datetime.timedelta(days=1)
        # Variable para almacenar los pozos
        pozos = []
        # Lista con meses del anio en espanol
        months = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"]
        # respuesta que se enviara
        response = HttpResponse(content_type='application/vnd.ms-excel')
        if tipo.clave == "RP" or tipo.clave == "RO" or tipo.clave == "RE":
            id_ubicacion = request.POST["ubicacion"]
            ubicacion = Ubicacion.objects.get(pk=id_ubicacion)
            # Se obtiene los pozos de la ubicacion seleccionada
            if ubicacion.tipo == "CAM":
                pozos = self.get_Pozos(ubicacion, fecha_inicio, fecha_fin)
            elif ubicacion.tipo == "SEC":
                campos = Ubicacion.objects.filter(padre=ubicacion.id)
                camp = []
                for campo in campos:
                    camp.append(campo.nombre)
                pozos = pozos + self.get_Pozos(camp, fecha_inicio, fecha_fin)
            elif ubicacion.tipo == "BLO":
                sectores = Ubicacion.objects.filter(padre=ubicacion.id)
                camp = []
                for sector in sectores:
                    campos = Ubicacion.objects.filter(padre=sector.id)
                    for campo in campos:
                        camp.append(campo.nombre)
                pozos = pozos + self.get_Pozos(camp, fecha_inicio, fecha_fin)
        if tipo.clave == "RP":
            # Se obtienen los odometros del reporte
            odometros = Odometro.objects.filter(tipos__clave="RP")
            # Se asigna nombre al archivo
            cont_dis = "attachment; filename=Reporte de produccion.xlsx"
            response['Content-Disposition'] = cont_dis
            # se crea un libro de excel y una hoja llamada RESUMEN
            workbook = xlsxwriter.Workbook(response, {'in_memory': True})
            worksheet = workbook.add_worksheet("RESUMEN")
            grafica_pb = workbook.add_chart({
                'type': 'area',
                'subtype': 'stacked'
            })
            grafica_pn = workbook.add_chart({
                'type': 'area',
                'subtype': 'stacked'
            })
            # Estilos para celdas
            format_title = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D9D9D9'})
            format_title.set_text_wrap()
            format_subtitle = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'})
            format_subtitle.set_text_wrap()
            format_number = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '####'})
            format_number.set_text_wrap()
            format_number_t = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '####',
                'fg_color': '#EEECE1'})
            format_number_t.set_text_wrap()
            format_firma = workbook.add_format({
                'bold': 1,
                'align': 'center',
                'valign': 'vcenter'})
            format_firma.set_text_wrap()
            format_obs = workbook.add_format({
                'bold': 1,
                'border': 1,
                'fg_color': 'white'})
            format_totals = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#EEECE1'})
            format_totals.set_text_wrap()
            format_pers = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#1F497D',
                'num_format': '####',
                'font_color': 'white'})
            format_pers.set_text_wrap()
            worksheet.set_row(4, 60)
            # Variables para control de información
            num_pozos = len(pozos)
            last_col_title = (num_pozos * 2) + 3
            titulo = contrato.nombre + " Contrato No. " + contrato.numero
            subtitulo = "RESUMEN DE PRODUCCIÓN"
            # Se obtiene un listado de fechas a partir de la fecha seleccionada
            lista_fechas, num_f = self.crea_Lista_f(fecha_inicio, fecha_fin)
            # Se pone el titulo, sutitulo y dia
            worksheet.merge_range(
                0, 0, 0, last_col_title, titulo, format_title)
            worksheet.merge_range(
                1, 0, 1,
                last_col_title, subtitulo.decode('utf-8'), format_subtitle)
            worksheet.merge_range(
                3, 1, 4, 1, "Dia", format_title)
            c = 2
            # se obtiene el nombre del mes de la fecha seleccionada en espanol
            nombre_mes = months[fecha_inicio.month - 1]
            fr = 5
            # import ipdb
            # ipdb.set_trace()
            for pozo in pozos:
                # ecabezados de columnas
                worksheet.merge_range(
                    3, c, 3, c + 1, pozo.nombre, format_title)
                worksheet.write(4, c, "Q BRUTO (BPD)", format_title)
                worksheet.write(4, c + 1, "Q NETO (BPD)", format_title)
                # titulo, subtitulo  y encabezados de hojas secundarias
                titulo = "REPORTE DE OPERACIÓN"
                subtitulo = nombre_mes + " " + str(fecha_inicio.year)
                worksheetPozo = workbook.add_worksheet(pozo.nombre)
                worksheetPozo.merge_range(
                    0, 0, 0, 8, titulo.decode('utf-8'), format_title)
                worksheetPozo.merge_range(
                    1, 0, 1, 8, subtitulo, format_subtitle)
                worksheetPozo.write(2, 0, "Fecha", format_title)
                worksheetPozo.write(2, 1, "Pozo", format_title)
                worksheetPozo.write(
                    2, 2, "Q BRUTO DISEÑO [BPD]".decode('utf-8'), format_title)
                worksheetPozo.write(
                    2, 3, "Q NETO DISEÑO [BPD]".decode('utf-8'), format_title)
                worksheetPozo.write(2, 4, "Q BRUTO [BPD]", format_title)
                worksheetPozo.write(2, 5, "% AGUA PEP", format_title)
                worksheetPozo.write(2, 6, "Q NETO [BPD]", format_title)
                worksheetPozo.write(
                    2, 7, "MEDICIÓN [BPD]".decode('utf-8'), format_title)
                worksheetPozo.write(2, 8, "OBSERVACIONES (2)", format_title)
                # Se cambio ancho y alto de celdas
                worksheetPozo.set_row(2, 60)
                worksheetPozo.set_column(1, 1, 20)
                worksheetPozo.set_column(7, 7, 20)
                worksheetPozo.set_column(8, 8, 80)
                # Se obtien las mediciones del reporte de produccion
                fecha_filter = fecha_fin.strftime("%Y-%m-%d")
                fecha_filter = fecha_filter + " 23:59"
                med = list(Medicion.objects.filter(
                    pozo=pozo.id,
                    fecha__gte=fecha_inicio.strftime("%Y-%m-%d"),
                    fecha__lte=fecha_filter,
                    odometro__tipos__clave="RP").order_by("-fecha"))
                # Se obtiene la produccion bruta y neta de diseno
                pbd = Medicion.objects.filter(
                    pozo=pozo.id,
                    odometro__clave="PBD").order_by("-fecha")
                if len(pbd) > 0:
                    pbd = pbd[0].lectura
                else:
                    pbd = ""
                pnd = Medicion.objects.filter(
                    pozo=pozo.id,
                    odometro__clave="PND").order_by("-fecha")
                if len(pnd) > 0:
                    pnd = pnd[0].lectura
                else:
                    pnd = ""
                # variable de control
                f = 3
                fr = 5
                cr = 2
                count = 0
                cambios = False
                # ciclo para iterar fechas
                for fecha in lista_fechas:
                    # Se asigna los datos de la columna dia y pozo
                    worksheetPozo.write(f, 0, fecha.day, format_subtitle)
                    worksheetPozo.write(f, 1, pozo.nombre, format_subtitle)
                    # fecha en string
                    lfecha = fecha.strftime("%Y-%m-%d")
                    # se itera odometros del reporte de produccion
                    for o in odometros:
                        # se itera las mediciones hasta encontrar
                        # la medicion por odometro y fecha
                        while count < len(med) and cambios is not True:
                            # Fecha de medicion actual
                            mfecha = med[count].fecha.strftime("%Y-%m-%d")
                            # se compara la fecha y odometro
                            # con la medicion actual
                            clave = med[count].odometro.clave
                            if o.clave == clave and lfecha == mfecha:
                                # Se compara la clave de odometro para saber
                                # a que columna pertenece
                                if o.clave == "PBR":
                                    worksheetPozo.write(
                                        f, cr, pbd, format_subtitle)
                                    worksheetPozo.write(
                                        f, cr + 1, pnd, format_subtitle)
                                    if med[count].lectura == 0:
                                        worksheet.write(
                                            fr, c,
                                            med[count].lectura,
                                            format_subtitle)
                                        worksheetPozo.write(
                                            f, cr + 2,
                                            med[count].lectura,
                                            format_subtitle)
                                    else:
                                        worksheet.write(
                                            fr, c,
                                            med[count].lectura, format_number)
                                        worksheetPozo.write(
                                            f, cr + 2,
                                            med[count].lectura, format_number)
                                elif o.clave == "PA":
                                    worksheetPozo.write(
                                        f, cr + 3,
                                        med[count].lectura,
                                        format_subtitle)
                                elif o.clave == "PNR":
                                    if med[count].lectura == 0:
                                        worksheet.write(
                                            fr, c + 1,
                                            med[count].lectura,
                                            format_subtitle)
                                        worksheetPozo.write(
                                            f, cr + 4,
                                            med[count].lectura,
                                            format_subtitle)
                                    else:
                                        worksheet.write(
                                            fr, c + 1,
                                            med[count].lectura, format_number)
                                        worksheetPozo.write(
                                            f, cr + 4,
                                            med[count].lectura, format_number)
                                elif o.clave == "OP":
                                    worksheetPozo.write(
                                        f, cr + 6,
                                        med[count].observaciones,
                                        format_obs)
                                elif o.clave == "MP":
                                    worksheetPozo.write(
                                        f, cr + 5,
                                        med[count].lectura, format_subtitle)
                                cambios = True
                            count = count + 1
                        # si no se encuentra la medicion se pone una celda
                        # vacia
                        if cambios is not True:
                            if o.clave == "PBR":
                                worksheetPozo.write(
                                    f, cr, "", format_subtitle)
                                worksheetPozo.write(
                                    f, cr + 1, "", format_subtitle)
                                worksheet.write(fr, c, "", format_subtitle)
                                worksheetPozo.write(
                                    f, cr + 2,
                                    "", format_subtitle)
                            elif o.clave == "PA":
                                worksheetPozo.write(
                                    f, cr + 3,
                                    "", format_subtitle)
                            elif o.clave == "PNR":
                                worksheet.write(fr, c + 1, "", format_subtitle)
                                worksheetPozo.write(
                                    f, cr + 4,
                                    "", format_subtitle)
                            elif o.clave == "OP":
                                worksheetPozo.write(
                                    f, cr + 6,
                                    "",
                                    format_obs)
                            elif o.clave == "MP":
                                worksheetPozo.write(
                                    f, cr + 5,
                                    "", format_subtitle)
                        count = 0
                        cambios = False
                    f = f + 1
                    fr = fr + 1
                # Promedio por cada hoja secundaria de pozo
                worksheetPozo.set_row(f, 60)
                worksheetPozo.merge_range(
                    f, 0, f, 1, "PROMEDIO MENSUAL", format_title)
                while cr < 8:
                    range_pro = xl_range(3, cr, f - 1, cr)
                    formula_pro = '=AVERAGE(' + range_pro + ')'
                    worksheetPozo.write_formula(
                        f, cr, formula_pro, format_number)
                    cr = cr + 1
                # se asigana la celdas para saver quien es el
                # el responsable de la ubicacion seleccionada
                worksheetPozo.write(
                    f, 8, "REVISÓ".decode('utf-8'), format_firma)
                if ubicacion.responsable:
                    worksheetPozo.write(
                        f + 2, 8,
                        ubicacion.responsable.user.get_full_name(),
                        format_firma)
                    worksheetPozo.write(
                        f + 1, 8,
                        "_________________________________________________________________________",
                        format_firma)
                    worksheetPozo.write(
                        f + 3, 8,
                        ubicacion.responsable.puesto, format_firma)
                # se asigna el % de agua por pozo al resumen
                cell = xl_rowcol_to_cell(f, 5)
                formula_pa = "='" + pozo.nombre + "'!" + cell
                worksheet.merge_range(
                    fr + 1, c, fr + 1, c + 1, formula_pa, format_pers)
                # se asigna valores a la grafica de produccion bruta
                grafica_pb.add_series({
                    'values': ['RESUMEN', 5, c, fr - 1, c],
                    'name': ['RESUMEN', 3, c, 3, c],
                    'data_labels': {'series_name': True, 'position': 'above'},
                })
                # se asigna valores a la grafica de produccion neta
                grafica_pn.add_series({
                    'values': ['RESUMEN', 5, c + 1, fr - 1, c + 1],
                    'name': ['RESUMEN', 3, c, 3, c],
                    'data_labels': {'series_name': True, 'position': 'above'},
                })
                c = c + 2
            # se asigna un ancho de grafica a partir del numero de pozos
            ancho_grafica = last_col_title * 66
            # Etiquetas de la grafica de produccion bruta
            grafica_pb.set_title(
                {'name': 'Producción Bruta (BPD)'.decode('utf-8')})
            grafica_pb.set_x_axis({'name': 'Días'.decode('utf-8')})
            grafica_pb.set_y_axis({'name': 'BPD'})
            grafica_pb.set_size({'width': ancho_grafica, 'height': 576})
            # Se agrega la grafica de produccion bruta a RESUMEN
            worksheet.insert_chart(
                fr + 3, 0, grafica_pb)
            # Etiquetas de la grafica de produccion neta
            grafica_pn.set_title(
                {'name': 'Producción Neta (BPD)'.decode('utf-8')})
            grafica_pn.set_x_axis({'name': 'Días'.decode('utf-8')})
            grafica_pn.set_y_axis({'name': 'BPD'})
            grafica_pn.set_size({'width': ancho_grafica, 'height': 576})
            # Se agrega la grafica de produccion neta a RESUMEN
            worksheet.insert_chart(
                fr + 31, 0, grafica_pn)
            # encabezados de totales por fecha del RESUMEN
            worksheet.write(4, c, "TOTAL BRUTA (BPD)", format_title)
            worksheet.write(4, c + 1, "TOTAL NETA (BPD)", format_title)
            # Se asigna el nombre del mes al RESUMEN
            worksheet.merge_range(
                5, 0, num_f + 5, 0, nombre_mes, format_subtitle)
            f = 5
            # se itera el numero de fechas
            for n in range(1, len(lista_fechas) + 1):
                # se crea la formula para totales brutos y netos
                i = 2
                cell_bruto = xl_rowcol_to_cell(f, i)
                cell_neto = xl_rowcol_to_cell(f, i + 1)
                formula_bruto = '=IF(' + cell_bruto + '="","",('
                formula_neto = '=IF(' + cell_neto + '="","",('
                while i < c - 2:
                    cell_bruto = xl_rowcol_to_cell(f, i)
                    cell_neto = xl_rowcol_to_cell(f, i + 1)
                    formula_bruto = formula_bruto + cell_bruto + '+'
                    formula_neto = formula_neto + cell_neto + '+'
                    i = i + 2
                cell_bruto = xl_rowcol_to_cell(f, i)
                cell_neto = xl_rowcol_to_cell(f, i + 1)
                formula_bruto = formula_bruto + cell_bruto + '))'
                formula_neto = formula_neto + cell_neto + '))'
                worksheet.write_formula(f, c, formula_bruto, format_number)
                worksheet.write_formula(
                    f, c + 1,
                    formula_neto, format_number)
                n_str = str(n)
                worksheet.write(f, 1, n_str, format_subtitle)
                f = f + 1
            i = 2
            # se itera el numero de columnas por pozos
            while i < c + 2:
                # se crea formula para total y promedio de produccion
                # de cada columna por pozo
                formula_total = '=SUM('
                formula_pro = '=AVERAGE('
                range_total = xl_range(5, i, f - 1, i)
                formula_total = formula_total + range_total + ')'
                formula_pro = formula_pro + range_total + ')'
                worksheet.write_formula(
                    f, i, formula_total, format_number_t)
                worksheet.write_formula(
                    f + 2, i, formula_pro, format_number_t)
                i = i + 1
            # alto de filas de promedio y total de produccion
            worksheet.set_row(num_f + 6, 40)
            worksheet.set_row(num_f + 8, 40)
            # encabezados para totales, promedios
            # y % de agua por pozo en RESUMEN
            worksheet.merge_range(
                num_f + 6, 0, num_f + 6, 1,
                "PRODUCCIÓN TOTAL (BPD)".decode('utf-8'), format_totals)
            worksheet.merge_range(
                num_f + 7, 0, num_f + 7, 1, "% AGUA", format_pers)
            worksheet.merge_range(
                num_f + 8, 0, num_f + 8, 1,
                "PRODUCCIÓN PROMEDIO (BPD)".decode('utf-8'), format_totals)
            workbook.close()
            return response
        elif tipo.clave == "RO":
            # Se obtienen los odometros del reporte
            odometros = Odometro.objects.filter(
                tipos__clave__in=["RP", "RO"]).order_by('clasificacion')
            # Se asigna nombre al archivo
            cont_dis = "attachment; filename=Reporte Operativo.xlsx"
            response['Content-Disposition'] = cont_dis
            # se crea un libro de excel y una hoja llamada RESUMEN
            workbook = xlsxwriter.Workbook(response, {'in_memory': True})
            # Estilos para celdas
            format_title = workbook.add_format({
                'bold': 1,
                'border': 1,
                'font_name': 'arial',
                'font_size': 48,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D9D9D9'})
            format_subtitle = workbook.add_format({
                'bold': 1,
                'border': 1,
                'font_size': 11,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '####',
                'font_color': '#FFFFFF',
                'fg_color': '#000000'})
            format_subtitle2 = workbook.add_format({
                'bold': 1,
                'border': 1,
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D9D9D9'})
            format_subtitle2.set_text_wrap()
            format_body = workbook.add_format({
                'bold': 1,
                'border': 1,
                'font_size': 11,
                'align': 'center',
                'num_format': '####',
                'valign': 'vcenter'})
            format_title.set_text_wrap()
            format_title_p = workbook.add_format({
                'bold': 1,
                'border': 1,
                'font_name': 'calabri',
                'font_size': 18,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D9D9D9'})
            format_subtitle_p = workbook.add_format({
                'bold': 1,
                'border': 1,
                'font_name': 'calabri',
                'font_size': 18,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FFFFFF'})
            format_title_p.set_text_wrap()
            format_obs = workbook.add_format({
                'bold': 1,
                'border': 1,
                'fg_color': 'white'})
            # Se agrega Hoja RESUMEN
            worksheet = workbook.add_worksheet("RESUMEN")
            worksheet.set_column(0, 0, 20)
            # Se obtiene un listado de fechas a partir de la fecha seleccionada
            lista_fechas, num_f = self.crea_Lista_f(fecha_inicio, fecha_fin)
            # Se obtiene el mes y anio para el titulo
            mes = months[fecha_inicio.month - 1]
            anio = str(fecha_inicio.year)
            titulo = "JET PUMP " + ubicacion.nombre + " " + mes + " " + anio
            num_col = (len(pozos) * 2)
            # Se establece el titulo y los escabezados
            worksheet.merge_range(
                0, 0, 6, num_col + 2, titulo, format_title)
            worksheet.write(7, 0, "", format_subtitle)
            worksheet.write(8, 0, "Fecha", format_subtitle2)
            worksheet.merge_range(
                7, 1, 7, 2,
                "Producción".decode('utf-8'), format_subtitle)
            worksheet.write(8, 1, "Bruta", format_subtitle2)
            worksheet.write(8, 2, "Neta", format_subtitle2)
            c = 3
            f = 9
            for fecha in lista_fechas:
                formula_tot_bruto = '=SUM('
                formula_tot_neto = '=SUM('
                for i in range(3, num_col, 2):
                    cell_bruto = xl_rowcol_to_cell(f, i)
                    cell_neto = xl_rowcol_to_cell(f, i + 1)
                    formula_tot_bruto = formula_tot_bruto + cell_bruto + "+"
                    formula_tot_neto = formula_tot_neto + cell_neto + "+"
                cell_bruto = xl_rowcol_to_cell(f, i + 2)
                cell_neto = xl_rowcol_to_cell(f, i + 3)
                formula_tot_bruto = formula_tot_bruto + cell_bruto + ")"
                formula_tot_neto = formula_tot_neto + cell_neto + ")"
                worksheet.write_formula(
                    f, 1, formula_tot_bruto, format_body)
                worksheet.write_formula(
                    f, 2, formula_tot_neto, format_body)
                worksheet.write(f, 0, fecha.day, format_body)
                f = f + 1
            range_tot_bruto = xl_range(9, 1, f - 1, 1)
            range_tot_neto = xl_range(9, 2, f - 1, 2)
            range_pro_bruto = xl_range(9, 1, f - 1, 1)
            range_pro_neto = xl_range(9, 2, f - 1, 2)
            formula_tot_bruto = '=SUM(' + range_tot_bruto + ')'
            formula_tot_neto = '=SUM(' + range_tot_neto + ')'
            formula_pro_bruto = '=AVERAGE(' + range_pro_bruto + ')'
            formula_pro_neto = '=AVERAGE(' + range_pro_neto + ')'
            worksheet.write_formula(
                f, 1, formula_tot_bruto, format_subtitle)
            worksheet.write_formula(
                f, 2, formula_tot_neto, format_subtitle)
            worksheet.write_formula(
                f + 1, 1, formula_pro_bruto, format_subtitle)
            worksheet.write_formula(
                f + 1, 2, formula_pro_neto, format_subtitle)
            worksheet.write(f, 0, "Totales", format_subtitle)
            worksheet.write(f + 1, 0, "Promedios", format_subtitle)
            for pozo in pozos:
                pbd = Medicion.objects.filter(
                    pozo=pozo.id,
                    odometro__clave="PBD").order_by("-fecha")
                if len(pbd) > 0:
                    pbd = pbd[0].lectura
                else:
                    pbd = ""
                pnd = Medicion.objects.filter(
                    pozo=pozo.id,
                    odometro__clave="PND").order_by("-fecha")
                if len(pnd) > 0:
                    pnd = pnd[0].lectura
                else:
                    pnd = ""
                worksheetPozo = workbook.add_worksheet(pozo.nombre)
                titulo = "REPORTE DE OPERACIÓN BOMBEO HIDRÁULICO "
                worksheetPozo.set_column(1, 1, 20)
                worksheetPozo.set_column(3, 3, 15)
                worksheetPozo.set_column(4, 4, 15)
                worksheetPozo.set_column(5, 5, 15)
                worksheetPozo.set_column(7, 7, 15)
                worksheetPozo.set_column(17, 17, 15)
                worksheetPozo.set_column(18, 18, 15)
                worksheetPozo.set_column(21, 21, 60)
                worksheetPozo.set_row(2, 35)
                grafica = workbook.add_chart({
                    'type': 'line',
                })
                worksheetPozo.write(2, 0, "Fecha", format_subtitle2)
                worksheetPozo.write(2, 1, "POZO", format_subtitle2)
                worksheetPozo.write(2, 2, "Partida", format_subtitle2)
                worksheetPozo.write(
                    2, 3,
                    "PRODUCCIÓN BRUTA DISEÑO [BPD]".decode("utf-8"),
                    format_subtitle2)
                worksheetPozo.write(
                    2, 4,
                    "PRODUCCIÓN NETA  DISEÑO [BPD]".decode("utf-8"),
                    format_subtitle2)
                worksheetPozo.write(
                    2, 5, "PRODUCCIÓN REAL BRUTA [BPD]".decode("utf-8"),
                    format_subtitle2)
                worksheetPozo.write(2, 6, "CORTE DE AGUA", format_subtitle2)
                worksheetPozo.write(
                    2, 7, "PRODUCCIÓN REAL NETA [BPD]".decode("utf-8"),
                    format_subtitle2)
                worksheetPozo.write(2, 8, "BONO", format_subtitle2)
                worksheetPozo.write(
                    2, 9, "MEDICIÓN [BPD]".decode("utf-8"),
                    format_subtitle2)
                worksheetPozo.write(2, 10, "P INY [Kg/cm2]", format_subtitle2)
                worksheetPozo.write(2, 11, "P TR  [Kg/cm2]", format_subtitle2)
                worksheetPozo.write(2, 12, "P SEP  [Kg/cm2]", format_subtitle2)
                worksheetPozo.write(
                    2, 13, "P CABEZAL [Kg/cm2]", format_subtitle2)
                worksheetPozo.write(
                    2, 14, "QL INYECTADO [BPD]", format_subtitle2)
                worksheetPozo.write(2, 15, "DPH", format_subtitle2)
                worksheetPozo.write(2, 16, "RPM", format_subtitle2)
                worksheetPozo.write(
                    2, 17, "NIVEL DE ACEITE DE MOTOR [GAL]", format_subtitle2)
                worksheetPozo.write(
                    2, 18,
                    "NIVEL DE ACEITE DE LUBRICACIÓN [GAL]".decode("utf-8"),
                    format_subtitle2)
                worksheetPozo.write(2, 19, "T#1", format_subtitle2)
                worksheetPozo.write(2, 20, "T#2", format_subtitle2)
                worksheetPozo.write(2, 21, "OBSERVACIONES", format_subtitle2)

                subtitulo = mes
                worksheetPozo.merge_range(
                    0, 0, 0, 21, titulo.decode('utf-8'), format_title_p)
                worksheetPozo.merge_range(
                    1, 0, 1, 21, subtitulo.decode('utf-8'), format_subtitle_p)
                worksheet.merge_range(
                    7, c, 7, c + 1, pozo.nombre, format_subtitle)
                worksheet.write(8, c, "Bruta", format_subtitle2)
                worksheet.write(8, c + 1, "Neta", format_subtitle2)
                fecha_filter = fecha_fin.strftime("%Y-%m-%d") + " 23:59"
                med = list(Medicion.objects.filter(
                    pozo=pozo.id,
                    fecha__gte=fecha_inicio.strftime("%Y-%m-%d"),
                    fecha__lte=fecha_filter,
                    odometro__tipos__clave__in=["RP", "RO"]).order_by(
                    "-fecha"))
                f = 9
                fp = 3
                count = 0
                cambios = False
                for fecha in lista_fechas:
                    fecha_str = str(fecha.day) + "-" + months[fecha.month - 1]
                    worksheetPozo.write(fp, 0, fecha_str, format_body)
                    worksheetPozo.write(fp, 1, pozo.nombre, format_body)
                    worksheetPozo.write(fp, 2, pozo.partida, format_body)
                    worksheetPozo.write(fp, 3, pbd, format_body)
                    worksheetPozo.write(fp, 4, pnd, format_body)
                    # fecha en string
                    sfecha = fecha.strftime("%Y-%m-%d")
                    for o in odometros:
                        while count < len(med) and cambios is not True:
                            mfecha = med[count].fecha.strftime("%Y-%m-%d")
                            clave = med[count].odometro.clave
                            if o.clave == clave and sfecha == mfecha:
                                if o.clave == "PBR":
                                    worksheet.write(
                                        f, c,
                                        med[count].lectura, format_body)
                                    worksheetPozo.write(
                                        fp, 5, med[count].lectura, format_body)
                                    med.remove(med[count])
                                elif o.clave == "PNR":
                                    worksheet.write(
                                        f, c + 1,
                                        med[count].lectura, format_body)
                                    worksheetPozo.write(
                                        fp, 7, med[count].lectura, format_body)
                                    med.remove(med[count])
                                elif o.clave == "PA":
                                    worksheetPozo.write(
                                        fp, 6, med[count].lectura, format_body)
                                    med.remove(med[count])
                                elif o.clave == "B":
                                    worksheetPozo.write(
                                        fp, 8, med[count].lectura, format_body)
                                    med.remove(med[count])
                                elif o.clave == "MP":
                                    worksheetPozo.write(
                                        fp, 9, med[count].lectura, format_body)
                                    med.remove(med[count])
                                elif o.clave == "PINY":
                                    worksheetPozo.write(
                                        fp, 10, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "PTR":
                                    worksheetPozo.write(
                                        fp, 11, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "PSEP":
                                    worksheetPozo.write(
                                        fp, 12, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "PCAB":
                                    worksheetPozo.write(
                                        fp, 13, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "QLINY":
                                    worksheetPozo.write(
                                        fp, 14, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "DPH":
                                    worksheetPozo.write(
                                        fp, 15, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "RPM":
                                    worksheetPozo.write(
                                        fp, 16, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "NAM":
                                    worksheetPozo.write(
                                        fp, 17, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "NAL":
                                    worksheetPozo.write(
                                        fp, 18, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "PGAST1":
                                    worksheetPozo.write(
                                        fp, 19, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "PGAST2":
                                    worksheetPozo.write(
                                        fp, 20, med[count].lectura,
                                        format_body)
                                    med.remove(med[count])
                                elif o.clave == "OP":
                                    worksheetPozo.write(
                                        fp, 21, med[count].observaciones,
                                        format_obs)
                                    med.remove(med[count])
                                cambios = True
                            count = count + 1
                        if cambios is not True:
                            if o.clave == "PBR":
                                worksheet.write(f, c, "", format_body)
                                worksheetPozo.write(fp, 5, "", format_body)
                            elif o.clave == "PNR":
                                worksheet.write(f, c + 1, "", format_body)
                                worksheetPozo.write(fp, 7, "", format_body)
                            elif o.clave == "PA":
                                worksheetPozo.write(
                                    fp, 6, "", format_body)
                            elif o.clave == "B":
                                worksheetPozo.write(
                                    fp, 8, "", format_body)
                            elif o.clave == "MP":
                                worksheetPozo.write(
                                    fp, 9, "", format_body)
                            elif o.clave == "PINY":
                                worksheetPozo.write(
                                    fp, 10, "",
                                    format_body)
                            elif o.clave == "PTR":
                                worksheetPozo.write(
                                    fp, 11, "",
                                    format_body)
                            elif o.clave == "PSEP":
                                worksheetPozo.write(
                                    fp, 12, "",
                                    format_body)
                            elif o.clave == "PCAB":
                                worksheetPozo.write(
                                    fp, 13, "",
                                    format_body)
                            elif o.clave == "QLINY":
                                worksheetPozo.write(
                                    fp, 14, "",
                                    format_body)
                            elif o.clave == "DPH":
                                worksheetPozo.write(
                                    fp, 15, "",
                                    format_body)
                            elif o.clave == "RPM":
                                worksheetPozo.write(
                                    fp, 16, "",
                                    format_body)
                            elif o.clave == "NAM":
                                worksheetPozo.write(
                                    fp, 17, "",
                                    format_body)
                            elif o.clave == "NAL":
                                worksheetPozo.write(
                                    fp, 18, "",
                                    format_body)
                            elif o.clave == "PGAST1":
                                worksheetPozo.write(
                                    fp, 19, "",
                                    format_body)
                            elif o.clave == "PGAST2":
                                worksheetPozo.write(
                                    fp, 20, "",
                                    format_body)
                            elif o.clave == "OP":
                                worksheetPozo.write(
                                    fp, 21, "",
                                    format_obs)
                        count = 0
                        cambios = False
                    f = f + 1
                    fp = fp + 1
                worksheetPozo.merge_range(
                    fp + 1, 0, fp + 2, 2,
                    "PROMEDIOS OPERATIVOS.", format_body)
                worksheetPozo.write(
                    fp + 1, 3, "BRUTA DISEÑO [BPD]".decode("utf-8"),
                    format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 4, "NETA  DISEÑO [BPD]".decode("utf-8"),
                    format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 5, "REAL BRUTA [BPD]", format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 6, "CORTE DE AGUA", format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 7, "REAL NETA [BPD]", format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 8, "BONO", format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 9, "P. INY. [Kg/cm2]", format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 10, "P. DESC. [Kg/cm2]", format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 11, "P. SEP. [Kg/cm2]", format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 12, "P. Bat. [Kg/cm2]", format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 13, "Q. Iny. [BPD]", format_subtitle2)
                worksheetPozo.write(
                    fp + 1, 14, "RPM", format_subtitle2)

                range_pro_bd = xl_range(3, 3, fp - 1, 3)
                formula_pro_bd = '=AVERAGE(' + range_pro_bd + ')'
                worksheetPozo.write_formula(
                    fp + 2, 3, formula_pro_bd, format_body)

                range_pro_nd = xl_range(3, 4, fp - 1, 4)
                formula_pro_nd = '=AVERAGE(' + range_pro_nd + ')'
                worksheetPozo.write_formula(
                    fp + 2, 4, formula_pro_nd, format_body)

                range_pro_br = xl_range(3, 5, fp - 1, 5)
                formula_pro_br = '=AVERAGE(' + range_pro_br + ')'
                worksheetPozo.write_formula(
                    fp + 2, 5, formula_pro_br, format_body)

                range_pro_pa = xl_range(3, 6, fp - 1, 6)
                formula_pro_pa = '=AVERAGE(' + range_pro_pa + ')'
                worksheetPozo.write_formula(
                    fp + 2, 6, formula_pro_pa, format_body)

                range_pro_rn = xl_range(3, 7, fp - 1, 7)
                formula_pro_rn = '=AVERAGE(' + range_pro_rn + ')'
                worksheetPozo.write_formula(
                    fp + 2, 7, formula_pro_rn, format_body)

                range_pro_b = xl_range(3, 8, fp - 1, 8)
                formula_pro_b = '=AVERAGE(' + range_pro_b + ')'
                worksheetPozo.write_formula(
                    fp + 2, 8, formula_pro_b, format_body)

                range_pro_pi = xl_range(3, 10, fp - 1, 10)
                formula_pro_pi = '=AVERAGE(' + range_pro_pi + ')'
                worksheetPozo.write_formula(
                    fp + 2, 9, formula_pro_pi, format_body)

                range_pro_pd = xl_range(3, 11, fp - 1, 11)
                formula_pro_pd = '=AVERAGE(' + range_pro_pd + ')'
                worksheetPozo.write_formula(
                    fp + 2, 10, formula_pro_pd, format_body)

                range_pro_ps = xl_range(3, 12, fp - 1, 12)
                formula_pro_ps = '=AVERAGE(' + range_pro_ps + ')'
                worksheetPozo.write_formula(
                    fp + 2, 11, formula_pro_ps, format_body)

                range_pro_pb = xl_range(3, 13, fp - 1, 13)
                formula_pro_pb = '=AVERAGE(' + range_pro_pb + ')'
                worksheetPozo.write_formula(
                    fp + 2, 12, formula_pro_pb, format_body)

                range_pro_qi = xl_range(3, 14, fp - 1, 14)
                formula_pro_qi = '=AVERAGE(' + range_pro_qi + ')'
                worksheetPozo.write_formula(
                    fp + 2, 13, formula_pro_qi, format_body)

                range_pro_rpm = xl_range(3, 15, fp - 1, 15)
                formula_pro_rpm = '=AVERAGE(' + range_pro_rpm + ')'
                worksheetPozo.write_formula(
                    fp + 2, 14, formula_pro_rpm, format_body)

                grafica.set_size({'x_scale': 2, 'y_scale': 1.5})
                grafica.add_series({
                    'values': [pozo.nombre, 3, 5, fp - 1, 5],
                    'categories': [pozo.nombre, 3, 0, fp - 1, 0],
                    'name': [pozo.nombre, 2, 5, 2, 5],
                    'marker': {'type': 'diamond'},
                    'data_labels': {
                        'value': True,
                        'font': {'name': 'calibri', 'size': 7},
                        'position': 'above'},
                })
                grafica.add_series({
                    'values': [pozo.nombre, 3, 7, fp - 1, 7],
                    'categories': [pozo.nombre, 3, 0, fp - 1, 0],
                    'name': [pozo.nombre, 2, 7, 2, 7],
                    'marker': {'type': 'diamond'},
                    'data_labels': {
                        'value': True,
                        'font': {'name': 'calibri', 'size': 7},
                        'position': 'above'},
                })
                grafica.set_title(
                    {'name': 'Producción Real'.decode('utf-8')})
                grafica.set_x_axis({'name': 'Días'.decode('utf-8')})
                grafica.set_y_axis({'name': 'BLS'})
                worksheetPozo.insert_chart(
                    3, 25, grafica)
                range_tot_bruto = xl_range(9, c, f - 1, c)
                range_tot_neto = xl_range(9, c + 1, f - 1, c + 1)
                range_pro_bruto = xl_range(9, c, f - 1, c)
                range_pro_neto = xl_range(9, c + 1, f - 1, c + 1)
                formula_tot_bruto = '=SUM(' + range_tot_bruto + ')'
                formula_tot_neto = '=SUM(' + range_tot_neto + ')'
                formula_pro_bruto = '=AVERAGE(' + range_pro_bruto + ')'
                formula_pro_neto = '=AVERAGE(' + range_pro_neto + ')'
                worksheet.write_formula(
                    f, c, formula_tot_bruto, format_subtitle)
                worksheet.write_formula(
                    f, c + 1, formula_tot_neto, format_subtitle)
                worksheet.write_formula(
                    f + 1, c, formula_pro_bruto, format_subtitle)
                worksheet.write_formula(
                    f + 1, c + 1, formula_pro_neto, format_subtitle)
                c = c + 2
            workbook.close()
            return response
        elif tipo.clave == "RE":
            cont_dis = "attachment; filename=Relacion de equipos.xlsx"
            response['Content-Disposition'] = cont_dis
            # se crea un libro de excel y una hoja llamada RESUMEN
            workbook = xlsxwriter.Workbook(response, {'in_memory': True})
            worksheet = workbook.add_worksheet("GENERAL")
            num_pozos = len(pozos)
            titulo = contrato.nombre + " No. " + contrato.numero
            fecha_hoy = datetime.datetime.today().strftime("%d/%m/%Y")
            worksheet.write(0, 0, "Contrato: ")
            worksheet.merge_range(
                0, 1, 0, 10, titulo)
            worksheet.write(1, 0, "Fecha:")
            worksheet.write(1, 1, fecha_hoy)
            format_title = workbook.add_format({
                'bold': 1,
                'border': 1,
                'font_name': 'arial',
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D9D9D9'})
            format_title.set_text_wrap()
            format_body = workbook.add_format({
                'border': 1,
                'font_name': 'arial',
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#F2F2F2'})
            format_body.set_text_wrap()
            worksheet.set_column(0, 0, 10)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(6, 6, 30)
            worksheet.set_column(11, 11, 25)
            worksheet.set_column(12, 12, 25)
            worksheet.write(4, 0, "Sector", format_title)
            worksheet.write(4, 1, "EBH", format_title)
            worksheet.write(4, 2, "Pozo", format_title)
            worksheet.write(4, 3, "Bomba Jet", format_title)
            worksheet.write(4, 5, "Housing", format_title)
            worksheet.write(4, 6, "Dirección".decode("utf-8"), format_title)
            worksheet.write(4, 7, "Latitud Norte", format_title)
            worksheet.write(4, 8, "Longitud Oeste", format_title)
            worksheet.write(
                4, 9, "No. Serie Patín".decode("utf-8"), format_title)
            worksheet.write(4, 10, "No. Serie Motor", format_title)
            worksheet.write(4, 11, "Marca y modelo del motor", format_title)
            worksheet.write(
                4, 12, "Marca y modelo de la bomba triplex", format_title)
            worksheet.write(4, 13, "No. Serie Triplex", format_title)
            worksheet.write(4, 14, "Tag del Separador", format_title)
            worksheet.write(4, 15, "No. Serie Separador", format_title)
            worksheet.write(4, 16, "HP", format_title)
            worksheet.write(4, 17, "Combustible", format_title)
            worksheet.write(4, 18, "Camper", format_title)
            worksheet.write(4, 19, "Marca", format_title)
            worksheet.write(4, 20, "Perfil", format_title)
            worksheet.write(4, 21, "Modelo", format_title)
            worksheet.write(4, 4, "Geometría".decode("utf-8"), format_title)
            worksheet.write(4, 22, "Estatus", format_title)
            worksheet.write(
                4, 23, "Fecha de instalación".decode("utf-8"), format_title)
            worksheet.write(4, 24, "Fecha de arranque", format_title)
            f = 5
            sector = ""
            # eq_asig = []
            for pozo in pozos:
                if pozo.estado != "EXT":
                    sector = pozo.ubicacion.padre.nombre
                    asignaciones = Asignacion.objects.filter(pozo__id=pozo.id)
                    equipos = []
                    for a in asignaciones:
                        equipos.append(a.equipo)
                    worksheet.write(f, 0, sector, format_body)
                    if len(equipos) > 0 and len(equipos) < 2:
                        worksheet.write(f, 1, equipos[0].tag, format_body)
                        bj = Equipo.objects.filter(
                            padre__tag=equipos[0].tag, tag__icontains="BJ")
                        if bj:
                            ho = Equipo.objects.filter(
                                padre__tag=bj[0].tag, tag__icontains="HO")
                            worksheet.write(f, 3, bj[0].tag, format_body)
                            worksheet.write(f, 4, bj[0].geometria, format_body)
                            worksheet.write(f, 19, bj[0].marca, format_body)
                            worksheet.write(f, 20, bj[0].perfil, format_body)
                            worksheet.write(f, 21, bj[0].modelo, format_body)
                            if ho:
                                worksheet.write(f, 5, ho[0].tag, format_body)
                            else:
                                worksheet.write(f, 5, "", format_body)
                        else:
                            worksheet.write(f, 3, "", format_body)
                            worksheet.write(f, 4, "", format_body)
                            worksheet.write(f, 5, "", format_body)
                            worksheet.write(f, 19, "", format_body)
                            worksheet.write(f, 20, "", format_body)
                            worksheet.write(f, 21, "", format_body)
                        worksheet.write(f, 6, pozo.direccion, format_body)
                        worksheet.write(f, 7, pozo.latitud, format_body)
                        worksheet.write(f, 8, pozo.longitud, format_body)
                        jtp = Equipo.objects.filter(
                            padre__tag=equipos[0].tag, tag__icontains="JTP")
                        if jtp:
                            worksheet.write(f, 9, jtp[0].tag, format_body)
                            me = Equipo.objects.filter(
                                padre__tag=jtp[0].tag,
                                tag__icontains="ME")
                            if me:
                                worksheet.write(f, 10, me[0].serie, format_body)
                                mm = me[0].marca + " " + me[0].modelo
                                worksheet.write(f, 11, mm, format_body)
                                worksheet.write(
                                    f, 17, me[0].tipo_combustible.clave,
                                    format_body)
                            else:
                                mc = Equipo.objects.filter(
                                    padre__tag=jtp[0].tag,
                                    tag__icontains="MC")
                                if mc:
                                    worksheet.write(
                                        f, 10, mc[0].serie, format_body)
                                    mm = mc[0].marca + " " + mc[0].modelo
                                    worksheet.write(f, 11, mm, format_body)
                                    worksheet.write(
                                        f, 17, mc[0].tipo_combustible.clave,
                                        format_body)
                                else:
                                    worksheet.write(
                                        f, 10, "", format_body)
                                    worksheet.write(f, 11, "", format_body)
                                    worksheet.write(f, 17, "", format_body)
                            bt = Equipo.objects.filter(
                                padre__tag=jtp[0].tag,
                                tag__icontains="BT")
                            if bt:
                                worksheet.write(f, 13, bt[0].serie, format_body)
                                btt = bt[0].marca + " " + bt[0].modelo
                                worksheet.write(f, 12, btt, format_body)
                                worksheet.write(
                                    f, 16, bt[0].horsepower, format_body)
                            else:
                                worksheet.write(f, 13, "", format_body)
                                worksheet.write(f, 12, "", format_body)
                                worksheet.write(f, 16, "", format_body)
                        fwko = Equipo.objects.filter(
                            padre__tag=equipos[0].tag, tag__icontains="FWKO")
                        if fwko:
                            worksheet.write(f, 14, fwko[0].tag, format_body)
                            worksheet.write(f, 15, fwko[0].serie, format_body)
                        else:
                            worksheet.write(f, 14, "", format_body)
                            worksheet.write(f, 15, "", format_body)
                        worksheet.write(f, 18, pozo.camper, format_body)
                        if pozo.estado == "ACT":
                            worksheet.write(f, 22, "OPERANDO", format_body)
                        else:
                            worksheet.write(f, 22, "NO OPERANDO", format_body)
                        worksheet.write(f, 23, pozo.fecha_instalacion, format_body)
                        worksheet.write(f, 24, pozo.fecha_arranque, format_body)
                    else:
                        worksheet.write(f, 1, "", format_body)
                        worksheet.write(f, 2, "", format_body)
                        worksheet.write(f, 3, "", format_body)
                        worksheet.write(f, 4, "", format_body)
                        worksheet.write(f, 5, "", format_body)
                        worksheet.write(f, 6, "", format_body)
                        worksheet.write(f, 7, "", format_body)
                        worksheet.write(f, 8, "", format_body)
                        worksheet.write(f, 9, "", format_body)
                        worksheet.write(f, 10, "", format_body)
                        worksheet.write(f, 11, "", format_body)
                        worksheet.write(f, 12, "", format_body)
                        worksheet.write(f, 13, "", format_body)
                        worksheet.write(f, 14, "", format_body)
                        worksheet.write(f, 15, "", format_body)
                        worksheet.write(f, 16, "", format_body)
                        worksheet.write(f, 17, "", format_body)
                        worksheet.write(f, 18, "", format_body)
                        worksheet.write(f, 19, "", format_body)
                        worksheet.write(f, 20, "", format_body)
                        worksheet.write(f, 21, "", format_body)
                        worksheet.write(f, 22, "", format_body)
                        worksheet.write(f, 23, "", format_body)
                        worksheet.write(f, 24, "", format_body)
                    worksheet.write(f, 2, pozo.nombre, format_body)
                    f = f + 1
            f = f + 2
            equipos_no_asig = Equipo.objects.filter(
                tag__icontains="EBH", estado="INA")
            num_ena = len(equipos_no_asig) - 1
            worksheet.merge_range(
                f, 0, f + num_ena, 0,
                "Equipo en Stock", format_body)
            worksheet.merge_range(
                f, 2, f + num_ena, 2,
                "Equipo en Stock", format_body)
            worksheet.merge_range(
                f, 2, f + num_ena, 2,
                "Equipo en Stock", format_body)
            worksheet.merge_range(
                f, 6, f + num_ena, 8,
                "Equipo en Stock", format_body)
            worksheet.merge_range(
                f, 18, f + num_ena, 24,
                "Equipo en Stock", format_body)
            for eq in equipos_no_asig:
                worksheet.write(f, 1, eq.tag, format_body)
                bj = Equipo.objects.filter(
                    padre__tag=eq.tag, tag__icontains="BJ")
                if bj:
                    ho = Equipo.objects.filter(
                        padre__tag=bj[0].tag, tag__icontains="HO")
                    worksheet.write(f, 3, bj[0].tag, format_body)
                    worksheet.write(f, 4, bj[0].geometria, format_body)
                    if ho:
                        worksheet.write(f, 5, ho[0].tag, format_body)
                    else:
                        worksheet.write(f, 5, "", format_body)
                    # cam = Equipo.objects.filter(
                    #     padre__tag=bj[0].tag, tag__icontains="CAM")
                    # if cam:
                    #     worksheet.write(f, 19, cam[0].marca, format_body)
                    #     worksheet.write(f, 20, cam[0].perfil, format_body)
                    #     worksheet.write(f, 21, cam[0].modelo, format_body)
                    # else:
                    #     worksheet.write(f, 19, "", format_body)
                    #     worksheet.write(f, 20, "", format_body)
                    #     worksheet.write(f, 21, "", format_body)
                # worksheet.write(f, 6, pozo.direccion, format_body)
                # worksheet.write(f, 7, pozo.latitud, format_body)
                # worksheet.write(f, 8, pozo.longitud, format_body)
                jtp = Equipo.objects.filter(
                    padre__tag=eq.tag, tag__icontains="JTP")
                if jtp:
                    worksheet.write(f, 9, jtp[0].tag, format_body)
                    me = Equipo.objects.filter(
                        padre__tag=jtp[0].tag,
                        tag__icontains="ME")
                    if me:
                        worksheet.write(f, 10, me[0].serie, format_body)
                        mm = me[0].marca + " " + me[0].modelo
                        worksheet.write(f, 11, mm, format_body)
                        worksheet.write(
                            f, 17, me[0].tipo_combustible.clave,
                            format_body)
                    else:
                        mc = Equipo.objects.filter(
                            padre__tag=jtp[0].tag,
                            tag__icontains="MC")
                        if mc:
                            worksheet.write(
                                f, 10, mc[0].serie, format_body)
                            mm = mc[0].marca + " " + mc[0].modelo
                            worksheet.write(f, 11, mm, format_body)
                            worksheet.write(
                                f, 17, mc[0].tipo_combustible.clave,
                                format_body)
                        else:
                            worksheet.write(
                                f, 10, "", format_body)
                            worksheet.write(f, 11, "", format_body)
                            worksheet.write(f, 17, "", format_body)
                    bt = Equipo.objects.filter(
                        padre__tag=jtp[0].tag,
                        tag__icontains="BT")
                    if bt:
                        worksheet.write(f, 13, bt[0].serie, format_body)
                        btt = bt[0].marca + " " + bt[0].modelo
                        worksheet.write(f, 12, btt, format_body)
                        worksheet.write(
                            f, 16, bt[0].horsepower, format_body)
                    else:
                        worksheet.write(f, 13, "", format_body)
                        worksheet.write(f, 12, "", format_body)
                        worksheet.write(f, 16, "", format_body)
                fwko = Equipo.objects.filter(
                    padre__tag=eq.tag, tag__icontains="FWKO")
                if fwko:
                    worksheet.write(f, 14, fwko[0].tag, format_body)
                    worksheet.write(f, 15, fwko[0].serie, format_body)
                else:
                    worksheet.write(f, 14, "", format_body)
                    worksheet.write(f, 15, "", format_body)
                f = f + 1

            workbook.close()
            return response
        elif tipo.clave == "REJ":
            nombre_mes = months[fecha_inicio.month - 1]
            fecha_hoy = datetime.datetime.today()
            cont_dis = "attachment; filename=Reporte ejecutivo JP "
            cont_dis = cont_dis + fecha_hoy.strftime("%m -%Y") + ".xlsx"
            response['Content-Disposition'] = cont_dis
            workbook = xlsxwriter.Workbook(response, {'in_memory': True})
            worksheet = workbook.add_worksheet("Resumen")
            titulo = "Reporte ejecutivo JP " + nombre_mes
            titulo = titulo + fecha_hoy.strftime(" %Y")
            num_pozos = len(pozos)
            f = 3
            lista_fechas, num_f = self.crea_Lista_f(fecha_inicio, fecha_fin)
            format_title = workbook.add_format({
                'bold': 1,
                'border': 2,
                'font_name': 'arial',
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D9D9D9'})
            format_title.set_text_wrap()
            format_body = workbook.add_format({
                'bold': 1,
                'border': 2,
                'font_name': 'arial',
                'font_size': 10,
                'align': 'center',
                'num_format': '####',
                'valign': 'vcenter'})
            format_body.set_text_wrap()
            format_body_currency = workbook.add_format({
                'bold': 1,
                'border': 2,
                'font_name': 'arial',
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter'})
            format_body_currency.set_text_wrap()
            format_body_currency.set_num_format('"$"0.00')
            # for c in range(0, 15):
            worksheet.set_column(0, 14, 17)
            grafica_pn = workbook.add_chart({
                'type': 'line'
            })
            grafica_ei = workbook.add_chart({
                'type': 'column'
            })
            grafica_ep = workbook.add_chart({
                'type': 'column'
            })
            grafica_ppm = workbook.add_chart({
                'type': 'area',
                'subtype': 'stacked'
            })
            grafica_cum = workbook.add_chart({
                'type': 'area',
                'subtype': 'stacked'
            })
            grafica_pag = workbook.add_chart({
                'type': 'area',
                'subtype': 'stacked'
            })
            worksheet.merge_range(0, 0, 1, 14, titulo, format_title)
            worksheet.write(2, 0, "Mes", format_title)
            worksheet.write(2, 1, "Día".decode("utf-8"), format_title)
            worksheet.write(
                2, 2, "Producción Bruta  acumulada Altamira".decode("utf-8"),
                format_title)
            worksheet.write(
                2, 3, "Producción Neta acumulada Altamira".decode("utf-8"),
                format_title)
            worksheet.write(
                2, 4, "Producción Bruta  acumulada Poza Rica".decode("utf-8"),
                format_title)
            worksheet.write(
                2, 5, "Producción Neta  acumulada Poza Rica".decode("utf-8"),
                format_title)
            worksheet.write(
                2, 6, "Producción Bruta  acumulada ATG".decode("utf-8"),
                format_title)
            worksheet.write(
                2, 7, "Producción Neta acumulada ATG".decode("utf-8"),
                format_title)
            worksheet.write(
                2, 8, "Producción Bruta".decode("utf-8"), format_title)
            worksheet.write(
                2, 9, "Producción Neta".decode("utf-8"), format_title)
            worksheet.write(
                2, 10, "Equipos Instalados".decode("utf-8"), format_title)
            worksheet.write(
                2, 11, "Equipos Produciendo".decode("utf-8"), format_title)
            worksheet.write(
                2, 12, "Precio del Petróleo (DLLS/BLS)".decode("utf-8"),
                format_title)
            worksheet.write(
                2, 13, "USD -MXN".decode("utf-8"), format_title)
            worksheet.write(
                2, 14, "Gas NYMEX (USD/MMBtu)".decode("utf-8"), format_title)
            worksheet.merge_range(3, 0, num_f + 3, 0, nombre_mes, format_body)
            pozos_pr = self.get_ids_pozos(
                "Sector Poza Rica", fecha_inicio, fecha_fin)
            pozos_alt = self.get_ids_pozos(
                "Sector Altamira", fecha_inicio, fecha_fin)
            pozos_atg = self.get_ids_pozos(
                "Sector ATG", fecha_inicio, fecha_fin)
            for fecha in lista_fechas:
                worksheet.write(f, 1, fecha.strftime("%d"), format_body)
                fecha_init = fecha.strftime("%Y-%m-%d") + " 00:00"
                fecha_end = fecha.strftime("%Y-%m-%d") + " 23:59"
                med_pba_pr = Medicion.objects.filter(
                    odometro__clave="PBR",
                    pozo__pk__in=pozos_pr,
                    fecha__gte=fecha_init,
                    fecha__lte=fecha_end)
                med_pba_alt = Medicion.objects.filter(
                    odometro__clave="PBR",
                    pozo__pk__in=pozos_alt,
                    fecha__gte=fecha_init,
                    fecha__lte=fecha_end)
                med_pba_atg = Medicion.objects.filter(
                    odometro__clave="PBR",
                    pozo__pk__in=pozos_atg,
                    fecha__gte=fecha_init,
                    fecha__lte=fecha_end)
                med_pna_pr = Medicion.objects.filter(
                    odometro__clave="PNR",
                    pozo__pk__in=pozos_pr,
                    fecha__gte=fecha_init,
                    fecha__lte=fecha_end)
                med_pna_alt = Medicion.objects.filter(
                    odometro__clave="PNR",
                    pozo__pk__in=pozos_alt,
                    fecha__gte=fecha_init,
                    fecha__lte=fecha_end)
                med_pna_atg = Medicion.objects.filter(
                    odometro__clave="PNR",
                    pozo__pk__in=pozos_atg,
                    fecha__gte=fecha_init,
                    fecha__lte=fecha_end)
                pba_pr = 0
                pba_alt = 0
                pba_atg = 0
                pna_pr = 0
                pna_atg = 0
                pna_alt = 0
                pozos_op = []
                pozos_ins = []
                for m in med_pba_pr:
                    pba_pr = pba_pr + m.lectura
                    if m.lectura == 0 or m.lectura is None:
                        pozos_ins.append(m.pozo.pk)
                    else:
                        pozos_op.append(m.pozo.pk)
                        pozos_ins.append(m.pozo.pk)
                for m in med_pba_alt:
                    pba_alt = pba_alt + m.lectura
                    if m.lectura == 0 or m.lectura is None:
                        pozos_ins.append(m.pozo.pk)
                    else:
                        pozos_op.append(m.pozo.pk)
                        pozos_ins.append(m.pozo.pk)
                for m in med_pba_atg:
                    pba_atg = pba_atg + m.lectura
                    if m.lectura == 0 or m.lectura is None:
                        pozos_ins.append(m.pozo.pk)
                    else:
                        pozos_op.append(m.pozo.pk)
                        pozos_ins.append(m.pozo.pk)
                for m in med_pna_pr:
                    pna_pr = pna_pr + m.lectura
                for m in med_pna_alt:
                    pna_alt = pna_alt + m.lectura
                for m in med_pna_atg:
                    pna_atg = pna_atg + m.lectura
                if pba_pr <= 0:
                    pba_pr = ""
                if pba_atg <= 0:
                    pba_atg = ""
                if pba_alt <= 0:
                    pba_alt = ""
                if pna_pr <= 0:
                    pna_pr = ""
                if pna_alt <= 0:
                    pna_alt = ""
                if pna_atg <= 0:
                    pna_atg = ""
                worksheet.write(f, 2, pba_alt, format_body)
                worksheet.write(f, 3, pna_alt, format_body)
                worksheet.write(f, 4, pba_pr, format_body)
                worksheet.write(f, 5, pna_pr, format_body)
                worksheet.write(f, 6, pba_atg, format_body)
                worksheet.write(f, 7, pna_atg, format_body)
                pb = ''
                pb = '=IF(' + xl_rowcol_to_cell(f, 2) + '="","",('
                pb = pb + xl_rowcol_to_cell(f, 2) + '+'
                pb = pb + xl_rowcol_to_cell(f, 4) + '+'
                pb = pb + xl_rowcol_to_cell(f, 6) + ')' + ')'
                pn = ''
                pn = '=IF(' + xl_rowcol_to_cell(f, 3) + '="","",('
                pn = pn + xl_rowcol_to_cell(f, 3) + '+'
                pn = pn + xl_rowcol_to_cell(f, 5) + '+'
                pn = pn + xl_rowcol_to_cell(f, 7) + ')' + ')'
                worksheet.write_formula(f, 8, pb, format_body)
                worksheet.write_formula(f, 9, pn, format_body)
                num_eq_in = 0
                num_eq_op = 0
                pozos_ins_asig = []
                pozos_op_asig = []
                for pid in pozos_ins:
                    asignaciones = Asignacion.objects.filter(pozo__pk=pid)
                    if asignaciones:
                        pozos_ins_asig.append(pid)
                    else:
                        num_eq_in = num_eq_in + 1
                for pid in pozos_op:
                    asignaciones = Asignacion.objects.filter(pozo__pk=pid)
                    if asignaciones:
                        pozos_op_asig.append(pid)
                    else:
                        num_eq_op = num_eq_op + 1
                a_ei = Asignacion.objects.filter(
                    pozo__pk__in=pozos_ins_asig).values_list(
                    'equipo', flat=True).distinct()
                a_eo = Asignacion.objects.filter(
                    pozo__pk__in=pozos_op_asig).values_list(
                    'equipo', flat=True).distinct()

                num_eq_in = num_eq_in + len(a_ei)
                num_eq_op = num_eq_op + len(a_eo)
                for_eq_inst = '=IF(' + xl_rowcol_to_cell(f, 3) + '="","",('
                for_eq_inst = for_eq_inst + str(num_eq_in) + '))'
                for_eq_op = '=IF(' + xl_rowcol_to_cell(f, 3) + '="","",('
                for_eq_op = for_eq_op + str(num_eq_op) + '))'
                worksheet.write_formula(f, 10, for_eq_inst, format_body)
                worksheet.write_formula(f, 11, for_eq_op, format_body)
                mezcla = indicadores.objects.filter(
                    fecha__gte=fecha_init,
                    fecha__lte=fecha_end,
                    clave="mezcla").order_by("fecha").last()
                usdtomx = indicadores.objects.filter(
                    fecha__gte=fecha_init,
                    fecha__lte=fecha_end,
                    clave="divisa").order_by("fecha").last()
                nymex = indicadores.objects.filter(
                    fecha__gte=fecha_init,
                    fecha__lte=fecha_end,
                    clave="nymex").order_by("fecha").last()
                if mezcla:
                    mezcla = mezcla.valor
                else:
                    mezcla = ""
                if usdtomx:
                    usdtomx = usdtomx.valor
                else:
                    usdtomx = ""
                if nymex:
                    nymex = nymex.valor
                else:
                    nymex = ""
                worksheet.write(f, 12, mezcla, format_body_currency)
                worksheet.write(f, 13, usdtomx, format_body_currency)
                worksheet.write(f, 14, nymex, format_body_currency)
                f = f + 1
            f = num_f + 4
            worksheet.merge_range(
                f, 0, f, 1, "Producción Total".decode("utf-8"), format_title)
            worksheet.merge_range(
                f + 1, 0, f + 1, 1,
                "Producción Promedio".decode("utf-8"), format_title)
            for c in range(2, 15):
                rango = xl_range(3, c, f - 1, c)
                formula_suma = '=SUM(' + rango + ')'
                formula_promedio = '=AVERAGE(' + rango + ')'
                if c > 11:
                    worksheet.write_formula(
                        f, c, formula_suma, format_body_currency)
                    worksheet.write_formula(
                        f + 1, c, formula_promedio, format_body_currency)
                else:
                    worksheet.write_formula(
                        f, c, formula_suma, format_body)
                    worksheet.write_formula(
                        f + 1, c, formula_promedio, format_body)

            worksheet.merge_range(f + 4, 1, f + 4, 2, "Variable", format_title)
            worksheet.merge_range(
                f + 4, 3, f + 4, 10, "Dirección".decode("utf-8"), format_title)
            worksheet.merge_range(
                f + 5, 1, f + 5, 2, "Divisa USD - MXN", format_body)
            worksheet.merge_range(
                f + 6, 1, f + 6, 2, "Precio MME", format_body)
            worksheet.merge_range(
                f + 7, 1, f + 7, 2,
                "Precio de Natural Gas NYMEX", format_body)
            worksheet.merge_range(
                f + 5, 3, f + 5, 10,
                "https://www.infosel.com/informacion-financiera/divisas/".decode("utf-8"),
                format_body)
            worksheet.merge_range(
                f + 6, 3, f + 6, 10,
                "https://www.infosel.com/informacion-financiera/indicadores/".decode("utf-8"),
                format_body)
            worksheet.merge_range(
                f + 7, 3, f + 7, 10,
                "http://www.nasdaq.com/markets/commodities.aspx".decode("utf-8"),
                format_body)
            grafica_pn.add_series({
                'values': ['Resumen', 3, 9, f - 1, 9],
                'name': ['Resumen', 2, 9, 2, 9]
            })
            grafica_ei.add_series({
                'values': ['Resumen', 3, 10, f - 1, 10],
                'name': ['Resumen', 2, 10, 2, 10],
                'y2_axis': True,
            })
            grafica_ei.add_series({
                'values': ['Resumen', 3, 11, f - 1, 11],
                'name': ['Resumen', 2, 11, 2, 11],
                'y2_axis': True,
                'data_labels': {
                    'value': True,
                }
            })
            grafica_ppm.add_series({
                'values': ['Resumen', 3, 12, f - 1, 12],
                'name': ['Resumen', 2, 12, 2, 12],
                'pattern': {
                    'pattern': 'light_downward_diagonal',
                    'fg_color': 'purple',
                    'bg_color': 'white'
                },
            })
            grafica_cum.add_series({
                'values': ['Resumen', 3, 13, f - 1, 13],
                'name': ['Resumen', 2, 13, 2, 13],
                'pattern': {
                    'pattern': 'light_downward_diagonal',
                    'fg_color': 'purple',
                    'bg_color': 'white'
                },
            })
            grafica_pag.add_series({
                'values': ['Resumen', 3, 14, f - 1, 14],
                'name': ['Resumen', 2, 14, 2, 14],
                'pattern': {
                    'pattern': 'light_downward_diagonal',
                    'fg_color': 'purple',
                    'bg_color': 'white'
                },
            })
            titulo_grafica = 'GRÁFICO RELACIÓN PRODUCCIÓN - EQUIPOS BH ' + nombre_mes + " " + fecha_hoy.strftime("%Y")
            grafica_pn.combine(grafica_ei)
            grafica_pn.set_title(
                {'name': titulo_grafica.decode('utf-8')})
            grafica_pn.set_legend({'position': 'bottom'})
            grafica_pn.set_x_axis({'name': 'Días'.decode('utf-8')})
            grafica_pn.set_y_axis({'name': 'BPD'})
            grafica_pn.set_y2_axis({'name': 'Numero de equipos'})
            grafica_pn.set_size({'width': 1090, 'height': 400})
            worksheet.insert_chart(3, 16, grafica_pn)
            titulo_grafica = 'Precio del Petróleo ' + nombre_mes + " " + fecha_hoy.strftime("%Y")
            grafica_ppm.set_legend({'position': 'bottom'})
            grafica_ppm.set_title(
                {'name': titulo_grafica.decode('utf-8')})
            grafica_ppm.set_x_axis(
                {'name': 'Días'.decode('utf-8')})
            grafica_ppm.set_y_axis(
                {'name': 'PRECIO  BARRIL DE PETRÓLEO'.decode('utf-8')})
            grafica_ppm.set_size({'width': 1090, 'height': 400})
            worksheet.insert_chart(23, 16, grafica_ppm)
            titulo_grafica = 'COTIZACIÓN USD - MXN ' + nombre_mes + " " + fecha_hoy.strftime("%Y")
            grafica_cum.set_legend({'position': 'bottom'})
            grafica_cum.set_title(
                {'name': titulo_grafica.decode('utf-8')})
            grafica_cum.set_x_axis(
                {'name': 'Días'.decode('utf-8')})
            grafica_cum.set_y_axis(
                {'name': 'PRECIO DEL DÓLAR'.decode('utf-8')})
            grafica_cum.set_size({'width': 1090, 'height': 400})
            worksheet.insert_chart(3, 33, grafica_cum)
            titulo_grafica = 'PRECIO NATURAL GAS NYMEX ' + nombre_mes + " " + fecha_hoy.strftime("%Y")
            grafica_pag.set_legend({'position': 'bottom'})
            grafica_pag.set_title(
                {'name': titulo_grafica.decode('utf-8')})
            grafica_pag.set_x_axis(
                {'name': 'Días'.decode('utf-8')})
            grafica_pag.set_y_axis(
                {'name': 'PRECIO GAS NATURAL'.decode('utf-8')})
            grafica_pag.set_size({'width': 1090, 'height': 400})
            worksheet.insert_chart(23, 33, grafica_pag)
            workbook.close()
            return response
        contexto = {
            'form': formulario
        }
        return render(request, self.template_name, contexto)

    def get_ids_pozos(self, nombre, fecha_inicio, fecha_fin):
        lista_ids_pozos = []
        pozos = Pozo.objects.filter(
            ubicacion__padre__nombre=nombre, sistema__clave="BHJ")
        fec_ini = fecha_inicio.strftime("%Y-%m-%d")
        fec_fin = fecha_fin.strftime("%Y-%m-%d")
        for p in pozos:
            if p.fecha_instalacion:
                f_ins = p.fecha_instalacion.strftime("%Y-%m-%d")
                if f_ins <= fec_fin:
                    if p.fecha_desinstalacion:
                        f_des = p.fecha_desinstalacion.strftime("%Y-%m-%d")
                        if f_des > fec_ini:
                            lista_ids_pozos.append(p.pk)
                    else:
                        lista_ids_pozos.append(p.pk)
        return lista_ids_pozos

    def get_Pozos(self, ubicacion, fecha_inicio, fecha_fin):
        lista_pozos = []
        pozos = Pozo.objects.filter(
            ubicacion__nombre__in=ubicacion).order_by("fecha_instalacion")
        fec_ini = fecha_inicio.strftime("%Y-%m-%d")
        fec_fin = fecha_fin.strftime("%Y-%m-%d")
        for p in pozos:
            if p.fecha_instalacion:
                f_ins = p.fecha_instalacion.strftime("%Y-%m-%d")
                if f_ins <= fec_fin:
                    if p.fecha_desinstalacion:
                        f_des = p.fecha_desinstalacion.strftime("%Y-%m-%d")
                        if f_des > fec_ini:
                            lista_pozos.append(p)
                    else:
                        lista_pozos.append(p)
        return lista_pozos

    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return datetime.datetime(year, month, day)

    def crea_Lista_f(self, fecha_inicio, fecha_fin):
        c = 0
        lista = []
        while fecha_inicio <= fecha_fin:
            lista.append(fecha_inicio)
            fecha_inicio = fecha_inicio + datetime.timedelta(days=1)
            c = c + 1
        return lista, c - 1
