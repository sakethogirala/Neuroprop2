class PROSPECT:
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("in-progress", "In Progress"),
        ("correcting", "Correcting"),
        ("completed", "Completed"),
        ("failed", "Failed")
    ]
    PURPOSE_CHOICES = [
        ("refinance", "Refinance"),
        ("construction", "Construction")
    ]
    PROPERTY_TYPE_CHOICES = [
        ("hotel", "Hotel"),
        ("self-storage", "Self Storage"),
        ("multifamily", "Multi-Familty")
    ]
