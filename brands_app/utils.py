import os, uuid
from lxml import etree
from django.conf import settings
from .config import STORAGE_DIR, XML_ROOT_TAG, XML_ITEM_TAG, FIELDS

def storage_path():
    return os.path.join(settings.BASE_DIR, STORAGE_DIR)

def build_xml(data):
    root = etree.Element(XML_ROOT_TAG)
    for d in data:
        item = etree.SubElement(root, XML_ITEM_TAG)
        for name, _, _, _ in FIELDS:
            val = d.get(name, "")
            child = etree.SubElement(item, name)
            child.text = str(val) if val is not None else ""
    return root

def save_xml_tree(root):
    p = storage_path()
    os.makedirs(p, exist_ok=True)
    fname = f"{uuid.uuid4().hex}.xml"
    full = os.path.join(p, fname)
    tree = etree.ElementTree(root)
    tree.write(full, pretty_print=True, xml_declaration=True, encoding="utf-8")
    return fname

def validate_xml_tree(tree):
    root = tree.getroot()
    if root.tag != XML_ROOT_TAG:
        return False, "Неверный корневой тег"
    for item in root.findall(XML_ITEM_TAG):
        for name, _, required, ftype in FIELDS:
            el = item.find(name)
            if required and (el is None or (el.text or "").strip() == ""):
                return False, f"Отсутствует обязательное поле {name}"
            if el is not None and ftype == "int" and el.text and not el.text.strip().isdigit():
                return False, f"Поле {name} должно быть числом"
    return True, "OK"

def read_all_xml():
    p = storage_path()
    if not os.path.isdir(p):
        return []
    res = []
    for fname in os.listdir(p):
        if not fname.lower().endswith(".xml"):
            continue
        full = os.path.join(p, fname)
        try:
            tree = etree.parse(full)
            ok, _ = validate_xml_tree(tree)
            if not ok:
                continue
            root = tree.getroot()
            for item in root.findall(XML_ITEM_TAG):
                d = {}
                for name, _, _, _ in FIELDS:
                    el = item.find(name)
                    d[name] = (el.text or "").strip() if el is not None else ""
                res.append({"file": fname, "item": d})
        except Exception:
            continue
    return res
