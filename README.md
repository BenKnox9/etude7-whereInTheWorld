# Etude 7 - Where in the world is CS

## Description

This script performs data cleansing and validation on coordinate inputs and outputs all valid coordinates
in a geojson with POINT(Longitude, Latitude) and its label.

## Program setup
In order to run my programme I installed 3 libraries, geopandas, geojson and matplotlib. Here's how to install each:
```
conda install geopandas
```
```
pip3 install geojson
```
```
pip3 install matplotlib
```

After these three libraries are installed the code should run smoothly.

## Running the Program - Normal usage
To generate the world map with coordinates you can enter this in the terminal:
```
python plotMap.py
```
This will generate a map based off of the coordinates in the text file countries.txt. To run the script with another text file as input, change 
line 5 in plotMap.py and enter a file of your choice:
```
geoJsonConvert.createFile("countries.txt")
```

To run the script with stdin as the input, line 5 will have to have "stdin" as the parameter:
```
geoJsonConvert.createFile("stdin")
```
Once stdin has finished inputing lines, to end the stdin on mac press control + D, on windows press control + z and then enter.
The map will then be shown.

## Testing Method: 
To test the program I used two input files, countries.txt and testCases.txt. countries.txt was used for verification of the location points on the map. testCases.txt was used for verification of my data validation methods. both txt files were created manually by entering all variations of coordinates that I could think of.

## Approach
I went with putting data validation in one file geoJsonConvert.py, while all of the plotting takes place in plotMap.py. Initially I tried to do all of the validation manually with loops, counts, and bools. Soon after I realized that this would be involve far more work than need be. I then started reading up on regular expressions and how to implement them. Although this took some time to wrap my head around, it proved to be the right choice. It took my geojson file from 500 lines without comments down to a little over 200. I didn't use regex's everywhere that I could have, mainly because I had spent so much time on the regex's already implemented and I was happy with the manual approach I took in some methods. The biggest problems I found with the manual approach were both the hasLabel method and the addComma method. It proved quite hard to distinguish a label from a string which can also contain letters, whitespace and commas. for the addComma method I initially decided I would count spaces and then add a comma in the centre space, of course this doesent work on a string like "45 N 89w" where the comma would be put before the N. I decided to use a regex here to add a space before and after any of NESW and then strip whitespace after the validation. This is shown in the below code snippet:
```
if not len(coordsString.split(" ")) == 2:
        pattern = r'(?<=[^\s])([NESWnesw])'
        coordsString = re.sub(pattern, r' \1', coordsString)
        pattern = r"([NEWSnews])(?!\s)"
        coordsString = re.sub(pattern, r"\1 ", coordsString)
        coordsString = coordsString.rstrip()

```
An example of where I added regex's but kept most of the manual code is in my methods to convert DDM and DMS in to standard form.
e.g.
```
try:
        s1 = inputArr[0]
        s1 = re.sub(r'[^0-9.-]', ' ', s1)
        s1 = s1.strip()
        s1Arr = s1.split(" ", 1)

        s2 = inputArr[1]
        s2 = re.sub(r'[^0-9.-]', ' ', s2)
        s2 = s2.strip()
        s2Arr = s2.split(" ", 1)

        if len(s1Arr) == 2 and len(s2Arr) == 2:
            s1dd = float(s1Arr[0]) + (float(s1Arr[1])/60)
            s2dd = float(s2Arr[0]) + (float(s2Arr[1])/60)

            result = [str(s1dd), str(s2dd)]
            return result
    except ValueError:
        return isDMS(inputArr)
```

 Overall I am quite happy with the way I reached the final result as shown below with input file countries.txt

![countriesScreenshot]https://altitude.otago.ac.nz/knobe957/etude7-whereiscs/-/blob/main/countriesScreenshot.png

### geoJsonConvert.py
This file has a method splitInput which calls a string of methods each doing their own part in the data validation. All of the validation happens per line, once a line is validated the coodinate and label are appended to an array called finalArr. Then every finalArr (which is a single coordinate + label) is appended to an array called finalResult. FinalResult is the array containing all coordinates for every line in the file. finalResult is then turned into a dataframe from the createFile method. After this the dfToGeojson method is called with the dataframe created previously as its input parameter. This dfToGeojson method will turn the values into a geojson file called jsonValues.geojson. All separate methods in geoJsonConvert are also explained in the comments above each method in geoJsonConvert.py.


### plotMap.py
This file will call the geoJsonConvert file hence can be used to run the whole program. It will then open the geojson file created by geoJsonConvert.py and take all of the points from the file. Then in line 13 the base map will be plotted, this is just a map provided with geopandas. After this all points will iterated through and will be plotted along with labels. 


## Author
Ben Knox