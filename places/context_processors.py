from .models import Category

def categories_processor(request):
    """
    Добавляет все категории в контекст для использования в шаблонах.
    """
    all_categories = Category.objects.all().order_by('name')
    return {'categories': all_categories}