# completed 4 number points for the projects. 

from SPARQLWrapper import SPARQLWrapper, JSON
import datetime
import math

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    R = 6371  # Radius of the Earth in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def query_restaurants(endpoint_url, date, time, max_distance=None, reference_lat=None, reference_lon=None):
    sparql = SPARQLWrapper(endpoint_url)
    datetime_input = f"{date}T{time}:00"

    sparql.setQuery(f"""
    PREFIX schema: <https://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?restaurant ?name ?telephone ?opens ?closes ?addressCountry ?addressLocality ?latitude ?longitude ?deliveryChargePrice ?eligibleTransactionVolume ?priceCurrency WHERE {{
        ?restaurant a schema:ProfessionalService ;
                    schema:name ?name ;
                    schema:telephone ?telephone ;
                    schema:openingHoursSpecification ?ohSpec ;
                    schema:location ?location ;
                    schema:priceSpecification ?priceSpec .
        ?location schema:address ?address ;
                  schema:latitude ?latitude ;
                  schema:longitude ?longitude .
        ?address schema:addressCountry ?addressCountry ;
                 schema:addressLocality ?addressLocality .
        ?priceSpec schema:deliveryChargePrice ?deliveryChargePrice ;
                   schema:eligibleTransactionVolume ?eligibleTransactionVolume ;
                   schema:priceCurrency ?priceCurrency .
        ?ohSpec schema:opens ?opens ;
                schema:closes ?closes .

        BIND(STRDT("{datetime_input}", xsd:dateTime) AS ?inputDateTime)
        FILTER(?opens <= ?inputDateTime && ?closes > ?inputDateTime)
    }}
    """)

    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        final_results = []
        for result in results["results"]["bindings"]:
            lat = float(result["latitude"]["value"])
            lon = float(result["longitude"]["value"])
            if max_distance is not None and reference_lat is not None and reference_lon is not None:
                distance = haversine(reference_lat, reference_lon, lat, lon)
                if distance <= max_distance:
                    final_results.append(result)
            else:
                final_results.append(result)

        return final_results
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    endpoint_url = "http://localhost:3030/dataset_det/sparql"

    date = input("Enter the date (YYYY-MM-DD) (Example: 1970-01-01): ")
    time = input("Enter the time (HH:MM) (Example: 11:40): ")
    max_distance = float(input("Enter maximum distance from location in km (enter 0 for no limit) (Example: 10): "))
    reference_lat = float(input("Enter your latitude (Example: 47.2173): ")) if max_distance > 0 else None
    reference_lon = float(input("Enter your longitude (Example: -1.5520): ")) if max_distance > 0 else None

    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        datetime.datetime.strptime(time, '%H:%M')
    except ValueError:
        print("Incorrect date or time format. Please use YYYY-MM-DD for date and HH:MM for time.")
        return

    results = query_restaurants(endpoint_url, date, time, max_distance, reference_lat, reference_lon)

    if results:
        for result in results:
            name = result.get("name", {}).get("value", "N/A")
            telephone = result.get("telephone", {}).get("value", "N/A")
            opens = result.get("opens", {}).get("value", "N/A")
            closes = result.get("closes", {}).get("value", "N/A")
            addressCountry = result.get("addressCountry", {}).get("value", "N/A")
            addressLocality = result.get("addressLocality", {}).get("value", "N/A")
            latitude = result.get("latitude", {}).get("value", "N/A")
            longitude = result.get("longitude", {}).get("value", "N/A")
            deliveryChargePrice = result.get("deliveryChargePrice", {}).get("value", "N/A")
            eligibleTransactionVolume = result.get("eligibleTransactionVolume", {}).get("value", "N/A")
            priceCurrency = result.get("priceCurrency", {}).get("value", "N/A")

            print(f"Restaurant: {name}, Telephone: {telephone}, Opens at: {opens}, Closes at: {closes}, "
                  f"Address Country: {addressCountry}, Address Locality: {addressLocality}, "
                  f"Latitude: {latitude}, Longitude: {longitude}, "
                  f"Delivery Charge Price: {deliveryChargePrice}, "
                  f"Eligible Transaction Volume: {eligibleTransactionVolume}, Price Currency: {priceCurrency}")
    else:
        print("No restaurants found open at the specified date and time, within the specified distance.")

if __name__ == "__main__":
    main()

            