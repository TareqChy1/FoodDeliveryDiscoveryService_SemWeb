# completed 8 number points for the projects. 

from SPARQLWrapper import SPARQLWrapper, JSON
import datetime
import math
import rdflib
import requests

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

def fetch_user_preferences(rdf_url):
    rdf_data = requests.get(rdf_url).text
    g = rdflib.Graph()
    g.parse(data=rdf_data, format='turtle')

    # Query to extract max price
    max_price_query = """
        PREFIX schema: <http://schema.org/>
        SELECT ?maxPrice
        WHERE {
            ?person schema:seeks ?preference .
            ?preference schema:priceSpecification ?priceSpec .
            ?priceSpec schema:maxPrice ?maxPrice .
        }
    """

    # Query to extract location
    location_query = """
        PREFIX schema: <http://schema.org/>
        SELECT ?latitude ?longitude ?radius
        WHERE {
            ?person schema:seeks ?preference .
            ?preference schema:availableAtOrFrom/schema:geoWithin/schema:geoMidpoint ?geoMidpoint .
            ?geoMidpoint schema:latitude ?latitude ;
                         schema:longitude ?longitude .
            ?preference schema:availableAtOrFrom/schema:geoWithin/schema:geoRadius ?radius .
        }
    """

    # Query to extract preferred time
    time_query = """
        PREFIX schema: <http://schema.org/>
        SELECT ?availabilityStarts
        WHERE {
            ?person schema:seeks ?preference .
            ?preference schema:availabilityStarts ?availabilityStarts .
        }
    """

    max_price = None
    for row in g.query(max_price_query):
        max_price = float(row.maxPrice)
        break

    latitude, longitude, radius = None, None, None
    for row in g.query(location_query):
        latitude = float(row.latitude)
        longitude = float(row.longitude)
        radius = float(row.radius)
        break

    preferred_time = None
    for row in g.query(time_query):
        preferred_time = str(row.availabilityStarts)
        break

    return max_price, latitude, longitude, radius, preferred_time

def query_restaurants(endpoint_url, datetime_input, max_price, max_distance, reference_lat, reference_lon):
    sparql = SPARQLWrapper(endpoint_url)

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
    }}
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        partial_matches = []
        for result in results["results"]["bindings"]:
            lat = float(result["latitude"]["value"])
            lon = float(result["longitude"]["value"])
            distance = haversine(reference_lat, reference_lon, lat, lon)
            eligibleTransactionVolume = float(result["eligibleTransactionVolume"]["value"]) if result["eligibleTransactionVolume"]["value"] else None
            opens = result["opens"]["value"]
            closes = result["closes"]["value"]

            score = 0
            scoreType = ""
            if max_distance is None or distance <= max_distance:
                score += 1
                scoreType += " Below maxDistance"
            if max_price is None or (eligibleTransactionVolume is not None and eligibleTransactionVolume <= max_price):
                score += 1
                scoreType += " Below maxPrice"
            if opens <= datetime_input and closes > datetime_input:
                score += 1
                scoreType += " Match dateTime"

            result["score"] = score
            result["scoreType"] = scoreType
            result["distance"] = distance
            result["eligibleTransactionVolume"] = eligibleTransactionVolume
            partial_matches.append(result)

        partial_matches.sort(key=lambda x: -x["score"])
        return partial_matches
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    
    # Publishing pref-chy.ttl data on a Linked Data Platform:
    # curl -X POST -H "Content-Type: text/turtle" -H "Slug: pref-chy.ttl" --data-binary @C:\Users\nushr\Desktop\Semantic_Web\Project\pref-chy.ttl http://193.49.165.77:3000/semweb/chy-workspace/
    # link: http://193.49.165.77:3000/semweb/chy-workspace/pref-chy.ttl
    

    rdf_url = "http://193.49.165.77:3000/semweb/chy-workspace/pref-chy.ttl"
    max_price, latitude, longitude, radius, preferred_time = fetch_user_preferences(rdf_url)

    if None in [max_price, latitude, longitude, radius, preferred_time]:
        print("Error parsing user preferences.")
        return

    endpoint_url = "http://localhost:3030/dataset_det/sparql"
    datetime_input = f"1970-01-01T{preferred_time}:00"

    results = query_restaurants(endpoint_url, datetime_input, max_price, radius, latitude, longitude)

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
            eligibleTransactionVolume = result.get("eligibleTransactionVolume", "N/A")
            priceCurrency = result.get("priceCurrency", {}).get("value", "N/A")
            score = result.get("score", "N/A")
            scoreType = result.get("scoreType", "N/A")
            
            if score > 1:
                print(f"Restaurant: {name}, Score: {score}, ScoreType: {scoreType}, Telephone: {telephone}, Opens at: {opens}, Closes at: {closes}, "
                      f"Address Country: {addressCountry}, Address Locality: {addressLocality}, "
                      f"Latitude: {latitude}, Longitude: {longitude}, "
                      f"Delivery Charge Price: {deliveryChargePrice}, Distance: {distance} km, "
                      f"Eligible Transaction Volume: {eligibleTransactionVolume}, Price Currency: {priceCurrency}")
    else:
        print("No restaurants found open at the specified date and time, within the specified distance and delivery price limit.")

if __name__ == "__main__":
    main()
