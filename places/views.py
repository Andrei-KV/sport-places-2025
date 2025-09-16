from django.db import models
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Place, PendingPlace, Comment, Rating, Photo, Category
from .forms import PlaceForm, CommentForm, RatingForm
from .utils import generate_place_map, generate_single_place_map
class HomePageView(TemplateView):
    template_name = 'places/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        popular_categories = Category.objects.order_by('-view_count')[:8]
        other_categories = Category.objects.exclude(
            pk__in=popular_categories.values('pk')
        ).order_by('name')
        popular_places = Place.objects.annotate(
            average_rating=models.Avg('ratings__value')
        ).filter(
            average_rating__isnull=False
        ).order_by(models.F('average_rating').desc(nulls_last=True))[:8]

        context.update({
            'popular_categories': popular_categories,
            'other_categories': other_categories,
            'popular_places': popular_places,
        })
        return context

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'places/category_detail.html'
    context_object_name = 'current_category'
    slug_url_kwarg = 'category_slug'

    def get_object(self, queryset=None):
        # Increment view count atomically
        category = super().get_object(queryset)
        Category.objects.filter(pk=category.pk).update(view_count=models.F('view_count') + 1)
        category.refresh_from_db() # Refresh the object to get the new count
        return category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        places = category.places.all().annotate(average_rating=models.Avg('ratings__value'))

        context.update({
            'places': places,
            'place_map': generate_place_map(self.request, places),
            'all_categories': Category.objects.all(),
        })
        return context

class PlaceDetailView(DetailView):
    model = Place
    template_name = 'places/place_detail.html'
    context_object_name = 'place'
    pk_url_kwarg = 'place_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        place = self.get_object()

        context.update({
            'comments': place.comments.all().order_by('-created_at'),
            'photos': place.photos.all(),
            'average_rating': place.ratings.aggregate(models.Avg('value'))['value__avg'],
            'place_map': generate_single_place_map(self.request, place),
            'comment_form': CommentForm(),
            'rating_form': RatingForm(),
        })
        return context

    def post(self, request, *args, **kwargs):
        place = self.get_object()
        if 'comment_submit' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.place = place
                new_comment.user = request.user
                new_comment.save()
                return redirect('place_detail', place_id=place.id)
        elif 'rating_submit' in request.POST:
            form = RatingForm(request.POST)
            if form.is_valid():
                value = form.cleaned_data['value']
                rating, created = Rating.objects.get_or_create(
                    place=place,
                    user=request.user,
                    defaults={'value': value}
                )
                if not created:
                    rating.value = value
                    rating.save()
                return redirect('place_detail', place_id=place.id)

        # If forms are invalid, re-render the page with errors
        return self.get(request, *args, **kwargs)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

class PlaceCreateView(LoginRequiredMixin, CreateView):
    model = PendingPlace
    form_class = PlaceForm
    template_name = 'places/add_place.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        return context

    def form_valid(self, form):
        existing_category = form.cleaned_data.get('existing_category')
        new_category_name = form.cleaned_data.get('new_category_name')
        category = None

        if new_category_name:
            category, _ = Category.objects.get_or_create(name=new_category_name)
        elif existing_category:
            category = existing_category

        form.instance.user = self.request.user
        form.instance.action = 'add'
        form.instance.category = category
        self.object = form.save()

        for photo_file in self.request.FILES.getlist('photos'):
            Photo.objects.create(image=photo_file, pending_place=self.object)

        return redirect(self.get_success_url())

class PlaceEditView(LoginRequiredMixin, CreateView):
    model = PendingPlace
    form_class = PlaceForm
    template_name = 'places/edit_place.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        self.original_place = get_object_or_404(Place, pk=self.kwargs['place_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'description': self.original_place.description,
            'latitude': self.original_place.latitude,
            'longitude': self.original_place.longitude,
        })
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['place'] = self.original_place
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.action = 'edit'
        form.instance.original_place = self.original_place
        form.instance.name = self.original_place.name # Keep original name
        form.instance.category = self.original_place.category # Keep original category
        self.object = form.save()

        for f in self.request.FILES.getlist('photos'):
            Photo.objects.create(pending_place=self.object, image=f)

        return redirect(self.get_success_url())

# The original function-based views are now replaced by the CBVs above.
# The following views are left as they are for now.
# register view is replaced by RegisterView

@login_required
def add_place(request):
    return PlaceCreateView.as_view()(request)

@login_required
def edit_place(request, place_id):
    return PlaceEditView.as_view()(request, place_id=place_id)

def register(request):
    return RegisterView.as_view()(request)
