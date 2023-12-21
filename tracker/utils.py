import os

def get_doc_path(instance, filename):
    return f"documents/{instance.document_type.prospect.uid}/{filename}"
