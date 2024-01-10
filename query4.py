# completed 6 number points for the projects. 
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

def query_restaurants(endpoint_url, date, time, max_delivery_price=None, max_distance=None, reference_lat=None, reference_lon=None, rank_by=None):
    sparql = SPARQLWrapper(endpoint_url)
    datetime_input = f"{date}T{time}:00"

    query = f"""
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
    """
    
    if max_delivery_price is not None and max_delivery_price > 0:
        query += f"FILTER(?deliveryChargePrice <= {max_delivery_price})\n"

    query += "}\n"

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        final_results = []
        for result in results["results"]["bindings"]:
            lat = float(result["latitude"]["value"])
            lon = float(result["longitude"]["value"])
            distance = haversine(reference_lat, reference_lon, lat, lon) if reference_lat is not None and reference_lon is not None else None
            delivery_price = float(result["deliveryChargePrice"]["value"]) if result["deliveryChargePrice"]["value"] else None
            result["distance"] = distance
            result["delivery_price"] = delivery_price
            if max_distance is not None and max_distance > 0 and distance is not None:
                if distance <= max_distance:
                    final_results.append(result)
            elif max_delivery_price is None or (delivery_price is not None and delivery_price <= max_delivery_price):
                final_results.append(result)

        if rank_by == "distance":
            final_results.sort(key=lambda x: (x["distance"] is not None, x["distance"]))
        elif rank_by == "price":
            final_results.sort(key=lambda x: (x["delivery_price"] is not None, x["delivery_price"]))

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
    max_delivery_price = float(input("Enter maximum delivery price in your currency (enter 0 for no limit) (Example: 3.5): "))
    rank_by = input("Rank restaurants by 'distance'for sorting minimum distance or 'price' for sorting minimum deliveryChargePrice (leave blank for no ranking) (Example: price): ")

    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        datetime.datetime.strptime(time, '%H:%M')
    except ValueError:
        print("Incorrect date or time format. Please use YYYY-MM-DD for date and HH:MM for time.")
        return

    results = query_restaurants(endpoint_url, date, time, max_delivery_price, max_distance, reference_lat, reference_lon, rank_by)

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
            distance = result.get("distance", "N/A")
            eligibleTransactionVolume = result.get("eligibleTransactionVolume", {}).get("value", "N/A")
            priceCurrency = result.get("priceCurrency", {}).get("value", "N/A")

            print(f"Restaurant: {name}, Telephone: {telephone}, Opens at: {opens}, Closes at: {closes}, "
                  f"Address Country: {addressCountry}, Address Locality: {addressLocality}, "
                  f"Latitude: {latitude}, Longitude: {longitude}, "
                  f"Delivery Charge Price: {deliveryChargePrice}, Distance: {distance} km, "
                  f"Eligible Transaction Volume: {eligibleTransactionVolume}, Price Currency: {priceCurrency}")
    else:
        print("No restaurants found open at the specified date and time, within the specified distance and delivery price limit.")

if __name__ == "__main__":
    main()
