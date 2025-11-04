from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .forms import BrandForm, BrandModelForm
from . import utils
from .config import MESSAGES
from .models import Brand
from lxml import etree
import os
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db import models as dj_models
from django.http import JsonResponse
from django.contrib import messages
from .models import Brand

def add_brand(request):
    if request.method == "POST":
        form = BrandModelForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            country = form.cleaned_data['country']
            founded = form.cleaned_data['founded']
            note = form.cleaned_data['note']
            color = form.cleaned_data['color']

            # Проверка на дубль
            exists = Brand.objects.filter(
                name=name,
                country=country,
                founded=founded,
                note=note,
                color=color
            ).exists()

            if exists:
                messages.error(request, "❗ Такая запись уже существует!")
                return render(request, "brands_app/add_brand.html", {"form": form})

            form.save()
            messages.success(request, "✅ Запись успешно добавлена!")
            return redirect("brands_app:list_items")

    else:
        form = BrandModelForm()

    return render(request, "brands_app/add_brand.html", {"form": form})

def upload_file(request):
    # Оставляем без изменений (файловая загрузка XML)
    if request.method == "POST" and request.FILES.get("file"):
        f = request.FILES["file"]
        ext = os.path.splitext(f.name)[1].lower()
        if ext != ".xml":
            return render(request, "brands_app/upload_result.html", {"error": "Только .xml"})
        p = utils.storage_path()
        os.makedirs(p, exist_ok=True)
        fname = f"{os.urandom(8).hex()}{ext}"
        full = os.path.join(p, fname)
        with open(full, "wb") as fh:
            for chunk in f.chunks():
                fh.write(chunk)
        # validate
        try:
            tree = etree.parse(full)
            ok, msg = utils.validate_xml_tree(tree)
            if not ok:
                os.remove(full)
                return render(request, "brands_app/upload_result.html", {"error": MESSAGES["upload_invalid"] + f" ({msg})"})
            return render(request, "brands_app/upload_result.html", {"message": MESSAGES["upload_success"]})
        except Exception as e:
            if os.path.exists(full):
                os.remove(full)
            return render(request, "brands_app/upload_result.html", {"error": MESSAGES["upload_invalid"] + f" ({str(e)})"})
    return render(request, "brands_app/upload_result.html")

def list_items(request):
    # выбор источника: ?source=xml или ?source=db (по умолчанию xml)
    source = request.GET.get('source', 'xml')
    if source == 'db':
        brands = Brand.objects.all()
        return render(request, "brands_app/list.html", {"items": brands, "source": "db"})
    else:
        items = utils.read_all_xml()
        if not items:
            return render(request, "brands_app/uploaded_list.html", {"message": MESSAGES["no_files"], "items": []})
        return render(request, "brands_app/list.html", {"items": items, "source": "xml"})

# AJAX поиск по БД
def ajax_search(request):
    q = request.GET.get('q', '').strip()
    qs = Brand.objects.all()
    if q:
        qs = qs.filter(
            dj_models.Q(name__icontains=q) |
            dj_models.Q(country__icontains=q) |
            dj_models.Q(note__icontains=q) |
            dj_models.Q(color__icontains=q)
        )
    data = list(qs.values('id','name','country','founded','note','color'))
    return JsonResponse(data, safe=False)

# Редактирование записи в БД
def edit_brand(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == "POST":
        form = BrandModelForm(request.POST, instance=brand)
        if form.is_valid():
            # на случай — убираем storage_choice
            storage = form.cleaned_data.pop('storage_choice')
            # проверка дубля (исключая текущий pk)
            name = form.cleaned_data['name']
            country = form.cleaned_data['country']
            founded = form.cleaned_data.get('founded')
            exists = Brand.objects.filter(name__iexact=name, country__iexact=country, founded=founded).exclude(pk=brand.pk).exists()
            if exists:
                form.add_error(None, "Запись с такими полями уже существует.")
            else:
                form.save()
                return redirect(reverse('brands_app:list') + '?source=db')

    else:
        # при редактировании показываем storage_choice = db
        form = BrandModelForm(instance=brand, initial={'storage_choice': 'db'})
    return render(request, "brands_app/edit.html", {"form": form, "brand": brand})

# Удаление (AJAX POST)
@require_POST
def delete_brand(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()
    return JsonResponse({"status": "ok"})
