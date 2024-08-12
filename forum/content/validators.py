from django.core.exceptions import ValidationError

def check_max_size_file(file):
    max_size = 50
    if file.size / (1024 ** 2) > max_size:
        raise ValidationError(f'Максимальный размер файла {max_size} MB')

def url_video_validator(video):
    correct_urls = ['youtube.com/watch', 'youtube.com/shorts']

    for correct_url in correct_urls:
        if correct_url in video and correct_url != video:
            return
    raise ValidationError('Ссылка на видео должна быть только с youtube.com')
    