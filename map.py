"""
pip install python-geoip
pip install python-geoip-geolite2

pip install geopy
pip install folium
"""

import geoip2.database


def produceMap(variant):
  print(f"Producing map{variant}")
  f = open(f"access{variant}.txt", 'r+')
  ips = [line.rstrip() for line in f.readlines()]
  f.close()

  countries = {}
  markersloc = {}

  print(f"{len(ips)} ips read")

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

  print(f"ips geolocated to {len(countries)} countries")

  from geopy.geocoders import Nominatim
  geolocator = Nominatim(user_agent="stand-with-ukraine")
  for country in countries:
    try:
      # Geolocate the center of the country
      loc = geolocator.geocode(country)
      if country == "Georgia":
        # Georgia is not the US state and ist not russia fixing bug in geolite db
        loc = geolocator.geocode("Tbilisi")
      # And return latitude and longitude
      markersloc[country] = (loc.latitude, loc.longitude)
    except:
      markersloc[country] = (0, 0)
      print("unable to locate " + country)

  print(f"country markers geolocated for {len(countries)} countries")

  import folium
  from folium.plugins import MarkerCluster

  # empty map
  world_map = folium.Map(tiles="cartodbpositron",location=(50,20),zoom_start=5)
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
    folium.Marker(location=[lat, long], radius=20,
                  tooltip=country,
                  icon=folium.DivIcon(
                    html=f"""<div style="{css}">{countries[country]}</div>"""),
                  ).add_to(marker_cluster)

  item_txt = """<br> <i class="fa fa-circle fa-3x" style="color:{col}"></i> &nbsp;{item}"""
  html_itms = item_txt.format(item="large group of countries", col="rgba(241, 211, 87);") \
              + item_txt.format(item="small group of countries", col="rgba(181, 226, 140);") \
              + item_txt.format(item="downloads per country", col="rgba(255,150,50, 0.8);")
  legend_html = """
       <div style="
       position: fixed; 
       bottom: 50px; left: 50px; width: 400px; height: 200px; 
       border:2px solid grey; z-index:9999; 
       padding: 1rem;
       border-radius: 2rem;
       background-color:rgba(255,255,255,0.8);
       opacity: .85;
       
       font-size:14px;
       font-weight: bold;
       
       ">
       <p>{title}</p> 
       
       {itm_txt}
  
        </div> """.format(title="Legend", itm_txt=html_itms)
  world_map.get_root().html.add_child(folium.Element(legend_html))
  world_map.save(f"map{variant}.html")


produceMap("")
produceMap("-verified")
