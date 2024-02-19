import os

def get_doc_path(instance, filename):
    if instance.document_type:
        return f"documents/{instance.document_type.prospect.uid}/{filename}"
    return f"documents/smart-sorting/{filename}" 
