"""
pip install python-geoip
pip install python-geoip-geolite2

pip install geopy
pip install folium
"""

import geoip2.database

def produceMap(variant):
  print (f"Producing map{variant}")
  f = open(f"access{variant}.txt", 'r+')
  ips = [line.rstrip() for line in f.readlines()]
  f.close()

  countries = {}
  markersloc = {}

  print (f"{len(ips)} ips read")

  with geoip2.database.Reader('GeoLite2-City.mmdb') as reader:
    for ip in ips:
      response = reader.city(ip)
      if len(response.country.names) == 0:
        print(f"IP {ip} not assignable to country")
        continue

      if not response.country.names['en'] in countries:
        countries[response.country.names['en']] = 0

      downloads = countries[response.country.names['en']]
      countries[response.country.names['en']] = downloads + 1

  print (f"ips geolocated to {len(countries)} countries")

  from geopy.geocoders import Nominatim
  geolocator = Nominatim(user_agent="stand-with-ukraine")
  for country in countries:
    try:
      # Geolocate the center of the country
      loc = geolocator.geocode(country)
      # And return latitude and longitude
      markersloc[country] = (loc.latitude, loc.longitude)
    except:
      markersloc[country] = (0,0)
      print ("unable to locate " + country)

  print (f"country markers geolocated for {len(countries)} countries")

  import folium
  from folium.plugins import MarkerCluster

  # empty map
  world_map = folium.Map(tiles="cartodbpositron")
  marker_cluster = MarkerCluster().add_to(world_map)

  css = "font-family: arial;\
  font-weight: bold;\
  color: white;\
  background: rgba(255,150,50, 0.8);\
  padding: 2rem;\
  border: 1px solid lightblue;\
  border-radius: 3rem;\
  display: table-cell;"

  for country in countries:
    lat = markersloc[country][0]
    long = markersloc[country][1]
    radius = 15
    folium.Marker(location=[lat, long],radius=20,
                  tooltip=country,
                  icon=folium.DivIcon(html=f"""<div style="{css}">{countries[country]}</div>"""),
    ).add_to(marker_cluster)

  world_map.save(f"map{variant}.html")

produceMap("")
produceMap("-verified")
