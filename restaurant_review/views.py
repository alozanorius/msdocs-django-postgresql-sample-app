import base64
from django.views import generic 
from django.db.models import Avg, Count
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.conf import settings
from . import utils

from restaurant_review.models import Restaurant, Review

# Create your views here.
def descargar_confirmacion(request):
    return render(request, 'restaurant_review/descargar_confirmacion.html')

def descargar_excel(request):
    base64_encoded = request.session.get('excel_data')
    if base64_encoded:
        excel_data = base64.b64decode(base64_encoded)
        response = HttpResponse(excel_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="datos_de_muestra.xls"'
        return response
    else:
        return HttpResponse("No se encontró el archivo para descargar.")

def mirar_directorio(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        lista_valores = []
        for file in files:
            print(file)
            print("\n\n")
            try:
                valores = utils.extraccion_total(file)
                lista_valores.append(valores)
            except:
                print(f"Incompatibilidad de archivo: {file}")
        response_stream = utils.crear_excel_xls_con_archivo(lista_valores, "salida_django_xls")
        base64_encoded = base64.b64encode(response_stream.getvalue()).decode('utf-8')
        request.session['excel_data'] = base64_encoded
        print("Llegué acá")
        redirect_url = reverse('restaurant_review:descargar_confirmacion')
        return JsonResponse({'success': True, 'redirect_url': redirect_url})
    print(settings.DATA_UPLOAD_MAX_NUMBER_FILES)
    return render(request, 'restaurant_review/directory_read_bis.html')






def index(request):
    print('Request for index page received')
    restaurants = Restaurant.objects.annotate(avg_rating=Avg('review__rating')).annotate(review_count=Count('review'))
    lastViewedRestaurant = request.session.get("lastViewedRestaurant", False)
    return render(request, 'restaurant_review/index.html', {'LastViewedRestaurant': lastViewedRestaurant, 'restaurants': restaurants})

@cache_page(60)
def details(request, id):
    print('Request for restaurant details page received')
    restaurant = get_object_or_404(Restaurant, pk=id)
    request.session["lastViewedRestaurant"] = restaurant.name
    return render(request, 'restaurant_review/details.html', {'restaurant': restaurant})


def create_restaurant(request):
    print('Request for add restaurant page received')
    return render(request, 'restaurant_review/create_restaurant.html')


@csrf_exempt
def add_restaurant(request):
    try:
        name = request.POST['restaurant_name']
        street_address = request.POST['street_address']
        description = request.POST['description']
    except (KeyError):
        # Redisplay the form
        return render(request, 'restaurant_review/add_restaurant.html', {
            'error_message': "You must include a restaurant name, address, and description",
        })
    else:
        restaurant = Restaurant()
        restaurant.name = name
        restaurant.street_address = street_address
        restaurant.description = description
        Restaurant.save(restaurant)

        return HttpResponseRedirect(reverse('details', args=(restaurant.id,)))


@csrf_exempt
def add_review(request, id):
    restaurant = get_object_or_404(Restaurant, pk=id)
    try:
        user_name = request.POST['user_name']
        rating = request.POST['rating']
        review_text = request.POST['review_text']
    except (KeyError):
        # Redisplay the form.
        return render(request, 'restaurant_review/add_review.html', {
            'error_message': "Error adding review",
        })
    else:
        review = Review()
        review.restaurant = restaurant
        review.review_date = timezone.now()
        review.user_name = user_name
        review.rating = rating
        review.review_text = review_text
        Review.save(review)

    return HttpResponseRedirect(reverse('details', args=(id,)))
