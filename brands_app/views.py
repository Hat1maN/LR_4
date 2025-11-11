from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from .forms import BrandModelForm
from .models import Brand
from . import utils
from django.views.decorators.http import require_POST
from django.db import models as dj_models

def add_brand(request):
    if request.method == "POST":
        form = BrandModelForm(request.POST)
        if form.is_valid():
            storage = form.cleaned_data.get('storage_choice', 'db')

            data = {
                'name': form.cleaned_data.get('name','').strip(),
                'country': form.cleaned_data.get('country','').strip(),
                'founded': form.cleaned_data.get('founded'),
                'note': form.cleaned_data.get('note','').strip(),
                'color': form.cleaned_data.get('color','').strip(),
            }

            if storage == 'xml':
                path = utils.add_brand_to_xml(data)
                messages.success(request, f"Запись добавлена в XML ({path})")
                return redirect(reverse('brands_app:list_items') + '?source=xml')
            else:
                # consider duplicates by name+country+founded (case-insensitive)
                exists = Brand.objects.filter(
                    name__iexact=data['name'],
                    country__iexact=data['country'],
                    founded=data['founded']
                ).exists()
                if exists:
                    messages.error(request, "Такая запись уже существует в базе данных.")
                    return render(request, "brands_app/add_brand.html", {"form": form})
                Brand.objects.create(**data)
                messages.success(request, "Запись успешно добавлена в базу данных.")
                return redirect(reverse('brands_app:list_items') + '?source=db')
    else:
        form = BrandModelForm()
    return render(request, "brands_app/add_brand.html", {"form": form})

def upload_file(request):
    # simple file upload for xml files
    if request.method == "POST" and request.FILES.get("file"):
        f = request.FILES["file"]
        ext = f.name.split('.')[-1].lower()
        if ext != "xml":
            messages.error(request, "Только файлы .xml разрешены")
            return redirect(reverse('brands_app:add_brand'))
        ensure = utils.ensure_upload_dir()
        dest = utils.current_xml_file()  # will create or return existing file
        # append uploaded content as new brands into dest
        try:
            # parse uploaded file
            from lxml import etree
            parser = etree.XMLParser(remove_blank_text=True)
            uploaded_tree = etree.parse(f, parser)
            root_uploaded = uploaded_tree.getroot()
            # read dest
            dest_tree = etree.parse(dest, parser)
            dest_root = dest_tree.getroot()
            for brand in root_uploaded.findall('brand'):
                dest_root.append(brand)
            dest_tree.write(dest, pretty_print=True, xml_declaration=True, encoding='utf-8')
            messages.success(request, "Файл загружен и объединён с текущим XML")
            return redirect(reverse('brands_app:list_items') + '?source=xml')
        except Exception as e:
            messages.error(request, f"Ошибка при обработке XML: {e}")
            return redirect(reverse('brands_app:add_brand'))
    return render(request, "brands_app/upload_result.html")

def list_items(request):
    source = request.GET.get('source', 'xml')
    if source == 'db':
        items = Brand.objects.all()
        return render(request, "brands_app/list.html", {"items": items, "source": "db"})
    else:
        items = utils.read_all_xml()
        return render(request, "brands_app/list.html", {"items": items, "source": "xml"})

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

def edit_brand(request, id):
    brand = get_object_or_404(Brand, pk=id)
    if request.method == "POST":
        form = BrandModelForm(request.POST, instance=brand)
        if form.is_valid():
            # check duplicate excluding current
            name = form.cleaned_data['name'].strip()
            country = form.cleaned_data['country'].strip()
            founded = form.cleaned_data.get('founded')
            exists = Brand.objects.filter(name__iexact=name, country__iexact=country, founded=founded).exclude(pk=brand.pk).exists()
            if exists:
                form.add_error(None, "Запись с такими полями уже существует.")
            else:
                form.save()
                messages.success(request, "Запись обновлена")
                return redirect(reverse('brands_app:list_items') + '?source=db')
    else:
        form = BrandModelForm(instance=brand, initial={'storage_choice':'db'})
    return render(request, "brands_app/edit.html", {"form": form, "brand": brand})

@require_POST
def delete_brand(request, id):
    brand = get_object_or_404(Brand, pk=id)
    brand.delete()
    return JsonResponse({"status":"ok"})
