import random
import string

def generate_unique_code(N):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

def generate_link_code(instance):
    Klass = instance.__class__
    code = generate_unique_code(5)
    if Klass.objects.filter(code = code).exists():
        return generate_link_code(instance)
    return code

def generate_activation_code(instance):
    Klass = instance.__class__
    activation_key = generate_unique_code(20)
    if Klass.objects.filter(activation_key = activation_key).exists():
        return generate_activation_code(instance)
    return activation_key