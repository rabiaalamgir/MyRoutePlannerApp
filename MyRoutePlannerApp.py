from geopy.geocoders import Nominatim
from itertools import permutations
from uber_rides.client import UberRidesClient
from uber_rides.session import Session


def calculate_estimates(start, end):
    if (start, end) in saved_estimates.keys():
        return saved_estimates[(start, end)]
    else:
        response = client.get_price_estimates(
            start_latitude=latitudes[start],
            start_longitude=longitudes[start],
            end_latitude=latitudes[end],
            end_longitude=longitudes[end],
            seat_count=1
        )
        return response.json.get('prices')

latitudes, locations, longitudes, new_locations = [], [], [], []
saved_estimates = {}
print("Enter the names for the set of locations you wish to visit, "
      "with the start location first in order and the final destination at "
      "the end.\nPlease press Enter after entering each location and 'q' "
      "after entering the last location.\n")
loc = str(input())
while not loc == 'q':
    locations.append(loc)
    loc = str(input())

print("Please wait while your locations get geocoded...\n")

for location in locations:
    try:
        latitudes.append(Nominatim().geocode(location).latitude)
        longitudes.append(Nominatim().geocode(location).longitude)
    except:
        locations.remove(location)
        print("\033[31mUnable to geocode "+location+"! Please press 1 to enter"
              " another location or press 2 to proceed with "
              +str(len(locations))+" locations. Press Enter after entering "
                                   "your option\033[0m\n")
        num = input()
        if int(num) == 1:
            print("Please enter the desired location and press Enter after.")
            new_location = str(input())
            new_locations.append(new_location)
            latitudes.append(Nominatim().geocode(new_location).latitude)
            longitudes.append(Nominatim().geocode(new_location).longitude)

locations += new_locations
print("Please wait while the optimal route gets calculated...\n")
session = Session(server_token='5Jx_gcRNq7Bp-Z-ZyPQkm0Gh_SDtXD0SWNRGwna7')
client = UberRidesClient(session)
first = True
if len(locations)>3:
    for permutation in list(permutations(range(1,len(locations)-1))):
        order = ((0,)+permutation)+(len(locations)-1,)
        price = 0
        for i in range(len(order)-1):
            estimates = calculate_estimates(order[i], order[i+1])
            saved_estimates[(order[i], order[i+1])] = estimates
            high_estimates = list(map(lambda x: x['high_estimate'], estimates))
            price += min(high_estimates)
            if i == 0:
                car = list(filter(lambda x:x['high_estimate']==min(
                    high_estimates), estimates))[0]['display_name']

        if first:
            min_price = price
            best_car = car
            best_permutation = order
            first = False
        elif price < min_price:
            min_price = price
            best_car = car
            best_permutation = order

elif len(locations)<2:
    print("Locations could not be geocoded.")

else:
    estimates = calculate_estimates(0,1)
    high_estimates = list(map(lambda x: x['high_estimate'], estimates))
    car = list(filter(lambda x: x['high_estimate'] == min(
        high_esustimates), estimates))[0]['display_name']
    best_permutation = range(len(locations))

route = ""
for i in best_permutation:
    if i < len(best_permutation)-1:
        route += locations[i]+" -> "
    else:
        route += locations[i]

print("You should use the car "+car+" and the route "+route+".")
