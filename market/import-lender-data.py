import json
from models import Lender

with open('./capital-recon-lender-data.json', 'r') as file:
    lenders_data = json.load(file)
 

for lender in lenders_data:
    Lender.objects.create(
        title=lender['title'],
        data=lender,
    )

print("Lender data imported successfully!")
