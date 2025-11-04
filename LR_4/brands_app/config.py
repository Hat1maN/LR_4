STORAGE_DIR = "uploaded_files"  # где хранятся XML
XML_ROOT_TAG = "brands"
XML_ITEM_TAG = "brand"

FIELDS = [
    ("name", "Название марки", True, "str"),
    ("country", "Страна происхождения", True, "str"),
    ("founded", "Год основания", False, "int"),
    ("note", "Примечание", False, "str"),
    ("color", "Цвет", False, "str"),
]

MESSAGES = {
    "upload_success": "Файл успешно загружен.",
    "upload_invalid": "Файл невалиден и был удалён.",
    "no_files": "На сервере XML файлов нет.",
}
