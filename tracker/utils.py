import os

def get_doc_path(instance, filename):
    return f"documents/{instance.prospect.uid}/{filename}"
