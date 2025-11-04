from django.shortcuts import render
from django.http import HttpResponse
from .forms import BrandForm
from . import utils
from .config import MESSAGES
from lxml import etree
import os

def add_brand(request):
    form = BrandForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = [form.cleaned_data]
        root = utils.build_xml(data)
        fname = utils.save_xml_tree(root)
        return render(request, "brands_app/add_brand.html", {"form": BrandForm(), "message": f"Сохранено в {fname}"})
    return render(request, "brands_app/add_brand.html", {"form": form})

def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        f = request.FILES["file"]
        ext = os.path.splitext(f.name)[1].lower()
        if ext != ".xml":
            return render(request, "brands_app/upload_result.html", {"error": "Только .xml"})
        p = utils.storage_path()
        os.makedirs(p, exist_ok=True)
        fname = f"{os.urandom(8).hex()}.xml"
        full = os.path.join(p, fname)
        with open(full, "wb") as dest:
            for chunk in f.chunks():
                dest.write(chunk)
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

def list_files(request):
    items = utils.read_all_xml()
    if not items:
        return render(request, "brands_app/uploaded_list.html", {"message": MESSAGES["no_files"], "items": []})
    return render(request, "brands_app/uploaded_list.html", {"items": items})
