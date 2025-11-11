import os
import random
import string
from lxml import etree

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, '..', 'uploaded_files')
# normalize path to project root/uploaded_files
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploaded_files'))

def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return UPLOAD_DIR

def random_name(n=12):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n)) + '.xml'

def current_xml_file():
    """
    If any xml exists in uploaded_files, return the first one (sorted).
    Otherwise, create a new random file name and return full path.
    """
    ensure_upload_dir()
    files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith('.xml')]
    files.sort()
    if files:
        return os.path.join(UPLOAD_DIR, files[0])
    # create a new random file
    fname = random_name()
    path = os.path.join(UPLOAD_DIR, fname)
    # create root element
    root = etree.Element('brands')
    tree = etree.ElementTree(root)
    tree.write(path, pretty_print=True, xml_declaration=True, encoding='utf-8')
    return path

def add_brand_to_xml(data: dict):
    """
    data: dict with keys name,country,founded,note,color
    Append new <brand> element to current xml file.
    """
    path = current_xml_file()
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(path, parser)
    root = tree.getroot()
    br = etree.SubElement(root, 'brand')
    for k in ('name', 'country', 'founded', 'note', 'color'):
        v = data.get(k) if data.get(k) is not None else ''
        child = etree.SubElement(br, k)
        child.text = str(v)
    tree.write(path, pretty_print=True, xml_declaration=True, encoding='utf-8')
    return path

def read_all_xml():
    """
    Return list of dicts with keys {item: {fields...}, file: filename}
    """
    ensure_upload_dir()
    files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith('.xml')]
    files.sort()
    result = []
    parser = etree.XMLParser(remove_blank_text=True)
    for fname in files:
        full = os.path.join(UPLOAD_DIR, fname)
        try:
            tree = etree.parse(full, parser)
            root = tree.getroot()
            for b in root.findall('brand'):
                item = {}
                for child in b:
                    item[child.tag] = child.text
                result.append({'item': item, 'file': fname})
        except Exception:
            continue
    return result
