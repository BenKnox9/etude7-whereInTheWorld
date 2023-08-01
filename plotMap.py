import matplotlib.pyplot as plt
import geopandas as gpd
import geoJsonConvert
# installed matplotlib and geopandas

# use "stdin" as parameter for user input or "testcases.txt" for example for a test file
geoJsonConvert.createFile("countries.txt")


with open("jsonValues.geojson") as json_file:
    points = gpd.read_file('jsonValues.geojson')
    # used for debugging
    # print(points)

worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

fig, ax = plt.subplots(figsize=(12, 6))

worldmap.plot(color="lightgrey", ax=ax, legend=True)
points.plot(marker="^", ax=ax)

for idx, row in points.iterrows():
    coordinates = row['geometry'].coords.xy
    x, y = coordinates[0][0], coordinates[1][0]
    ax.annotate(row['label'], xy=(x, y), xytext=(x, y))

plt.show(block=True)
