from django.core.exceptions import ValidationError

def check_max_size_file(file):
    max_size = 50
    if file.size / (1024 ** 2) > max_size:
        raise ValidationError(f'Максимальный размер файла {max_size} MB')