import folium
from django.urls import reverse

def generate_place_map(request, places):
    """
    Generates a folium map with markers for a list of places.
    """
    if not places:
        return None

    # Center the map on the first place in the list
    first_place = places.first()
    m = folium.Map(location=[first_place.latitude, first_place.longitude], zoom_start=12)

    for place in places:
        yandex_maps_url = f"https://yandex.ru/maps/?rtext=~{place.latitude},{place.longitude}&z=15"
        place_detail_url = request.build_absolute_uri(reverse('place_detail', args=[place.id]))
        first_photo = place.first_photo

        if first_photo:
            photo_url = request.build_absolute_uri(first_photo.image.url)
            iframe_html = f"""
                <div style="font-family: Arial, sans-serif; width: 200px;">
                    <img src="{photo_url}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 4px;" alt="{place.name} photo">
                    <div style="padding: 10px;">
                        <h4 style="margin: 0 0 5px 0;">
                            <a href="{place_detail_url}" target="_top" style="color: #007bff; text-decoration: none;">{place.name}</a>
                        </h4>
                        <a href="{yandex_maps_url}" target="_blank" style="font-size: 0.9em; color: #555;">Построить маршрут</a>
                    </div>
                </div>
            """
        else:
            iframe_html = f"""
                <div style="font-family: Arial, sans-serif; padding: 10px;">
                    <h4 style="margin: 0 0 5px 0;">
                        <a href="{place_detail_url}" target="_top" style="color: #007bff; text-decoration: none;">{place.name}</a>
                    </h4>
                    <a href="{yandex_maps_url}" target="_blank" style="font-size: 0.9em; color: #555;">Построить маршрут</a>
                </div>
            """

        iframe = folium.IFrame(html=iframe_html, width=220, height=200)
        popup = folium.Popup(iframe, max_width=220)

        folium.Marker(
            [place.latitude, place.longitude],
            tooltip=place.name,
            popup=popup
        ).add_to(m)

    return m._repr_html_()

def generate_single_place_map(request, place):
    """
    Generates a folium map for a single place.
    """
    if not place.latitude or not place.longitude:
        return None

    m = folium.Map(location=[place.latitude, place.longitude], zoom_start=15)

    yandex_maps_url = f"https://yandex.ru/maps/?rtext=~{place.latitude},{place.longitude}&z=15"
    place_detail_url = request.build_absolute_uri(reverse('place_detail', args=[place.id]))
    first_photo = place.first_photo

    if first_photo:
        photo_url = request.build_absolute_uri(first_photo.image.url)
        iframe_html = f"""
            <div style="font-family: Arial, sans-serif; width: 200px;">
                <img src="{photo_url}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 4px;" alt="{place.name} photo">
                <div style="padding: 10px;">
                    <h4 style="margin: 0 0 5px 0;">
                        <a href="{place_detail_url}" target="_top" style="color: #007bff; text-decoration: none;">{place.name}</a>
                    </h4>
                    <a href="{yandex_maps_url}" target="_blank" style="font-size: 0.9em; color: #555;">Построить маршрут</a>
                </div>
            </div>
        """
    else:
        iframe_html = f"""
            <div style="font-family: Arial, sans-serif; padding: 10px;">
                <h4 style="margin: 0 0 5px 0;">
                    <a href="{place_detail_url}" target="_top" style="color: #007bff; text-decoration: none;">{place.name}</a>
                </h4>
                <a href="{yandex_maps_url}" target="_blank" style="font-size: 0.9em; color: #555;">Построить маршрут</a>
            </div>
        """

    iframe = folium.IFrame(html=iframe_html, width=220, height=200)
    popup = folium.Popup(iframe, max_width=220)

    folium.Marker(
        [place.latitude, place.longitude],
        tooltip=place.name,
        popup=popup
    ).add_to(m)

    return m._repr_html_()
