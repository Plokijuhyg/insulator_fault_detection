import folium

def generate_fault_map(fault_location, suppliers, output_file):
    m = folium.Map(location=fault_location, zoom_start=13)
    folium.Marker(location=fault_location, popup="Detected Fault", icon=folium.Icon(color='red')).add_to(m)

    for supplier in suppliers:
        # Assuming supplier has 'location' as (lat, lon) tuple
        if 'location' in supplier:
            folium.Marker(
                location=supplier['location'],
                popup=f"{supplier['name']}\n{supplier.get('description', '')}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
    m.save(output_file)
