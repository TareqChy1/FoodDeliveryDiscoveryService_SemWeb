# completed 3 number points for the projects. 

from SPARQLWrapper import SPARQLWrapper, JSON
import datetime

def query_restaurants(endpoint_url, date, time):
    sparql = SPARQLWrapper(endpoint_url)

    # Combine date and time for the query
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
        return results["results"]["bindings"]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    endpoint_url = "http://localhost:3030/dataset_det/sparql" 

    date = input("Enter the date (YYYY-MM-DD) (Example: 1970-01-01): ")
    time = input("Enter the time (HH:MM) (Example: 11:40): ")

    # Validate date and time format
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        datetime.datetime.strptime(time, '%H:%M')
    except ValueError:
        print("Incorrect date or time format. Please use YYYY-MM-DD for date and HH:MM for time.")
        return

    results = query_restaurants(endpoint_url, date, time)

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
            print(f"Restaurant: {name}, Telephone: {telephone}, Opens at: {opens}, Closes at: {closes}, Address Country: {addressCountry}, Address Locality: {addressLocality}, Latitude: {latitude}, Longitude: {longitude}, Delivery Charge Price: {deliveryChargePrice}, Eligible Transaction Volume: {eligibleTransactionVolume}, Price Currency: {priceCurrency}")
    else:
        print("No restaurants found open at the specified date and time.")

if __name__ == "__main__":
    main()
