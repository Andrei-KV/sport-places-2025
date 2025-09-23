from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings

class PublicMediaStorage(GoogleCloudStorage):
    """
    Кастомное хранилище для общедоступных медиа-файлов в Google Cloud Storage.
    Это гарантирует, что файлы сохраняются в поддиректории 'media/'.
    """
    location = 'media'
    default_acl = 'publicRead'
    file_overwrite = False
