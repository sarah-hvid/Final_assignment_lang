# Final assignment (selfassigned) - Ibsen's locations
 
Link to GitHub of this assignment: https://github.com/sarah-hvid/Final_assignment_lang

## Assignment description
The purpose of this assignment is to investigate the locations used by the 18th century writer Henrik Ibsen in his letters. These locations should be gathered from the historic Danish he wrote in. The coordinates of the locations should then be gathered and visualized on a map.

## Contribution
The XML data was gathered from the Ibsen archive [website](https://www.ibsen.uio.no/brevkronologi.xhtml). I've received it from Center for Humanities Computing as it is part of an ongoing project between them and the Ibsen Center. For this reason the data is uploaded in a zip file in this repository.\
\
The code for the parsing of the XML files has previously been created by myself in relation to my bachelor project. The results of that assignment confirmed that using Dacy on historic Danish was possible and that the largest Dacy model performed the best. This experience has been employed in this assignment. The code of the parsing however has been improved based on the knowledge from this course and is therefore not exactly the same (Andersen, 2022).

## Methods
Initially, a script was created for the preprocessing steps: ```preprocess.py```. The XML files were parsed so that only the text of the body of the letters remained. The files were saved as text files. These text files were then used to fit the Dacy large model to gather named entities of the location type. This model was chosen because it returns the best results on the historic Danish text. The output however still required some cleaning. Specific results that were clearly mistakes were removed. The locations were then aligned by removing the _-s_ endings (e.g., Danmark**s** to Danmark). Different spellings were also gathered into one by comparing the strings using Levenshtein Distance. Finally, a dataframe was created showing each unique location and the number of times it occurred. Using the -p flag, the user may specify to only run the preprocessing of the Dacy dataframe. This is available mainly for troubleshooting and ressource saving reasons.\
A script was then created for the geocoding and plotting: ```geocode.py```. The locations were then geocoded, meaning that their coordinates were gathered using ```geopy```. These coordinates were then used to create different visualozations showing the locations that Ibsen mentioned in his letters. Three static and two interactive plots are created and saved in the ```output``` folder. Using the -p flag, the user may specify to only run the plotting of the geocoded dataframe. This is available mainly for troubleshooting and ressource saving reasons. Using the -f flag, the user may also specify a different CSV file containing locations in a column named _loc_ and a corresponding numeric value in a column named _count_.

## Usage
In order to run the scripts, certain modules need to be installed. These can be found in the ```requirements.txt``` file. The folder structure must be the same as in this GitHub repository (ideally, clone the repository).\
The data used in the assignment is __Henrik Ibsen's letters__ (see _Contribution_). The data is available in the ```data.zip``` folder and must be unzipped before running these scripts.
```bash
git clone https://github.com/sarah-hvid/Final_assignment_lang
cd Final_assignment_lang
pip install -r requirements.txt
unzip data.zip
```
The current working directory when running the script must be the one that contains the ```data```, ```output``` and ```src``` folder. It is important that the user runs the ```preprocess.py``` script first.\
\
How to run the scripts from the command line: 

__The XML parsing and preprocessing__\
With default values:
```bash
python src/preprocess.py
```
Specified _ONLY_ preprocessing, meaning the Dacy CSV has already been created:
```bash
python src/preprocess.py -p 1
```
__The geocoding and plotting__\
With default values:
```bash
python src/geocode.py
```
Specified file input and _ONLY_ plotting, meaning the the geocode CSV has already been created:
```bash
python src/geocode.py -p 1 -f data/csv/loc_count.csv
```
Examples of the outputs of the scripts can be found in the ```output``` folder. 

## Results
The results of the scripts are mainly exploratory as no specific hypothesis is being investigated. However, I find the results quite impressive considering the historic text. Even though specific errors of Dacy has been removed, the visualizations show an image that make sense. Ibsen spoke mostly of locations in Europe and specifically in Norway, Sweden, Denmark, Germany and Italy. These countries contain both the most varieties of locations as seen in the ```Folium``` plot and aggregated mentions as seen in the ```GeoPandas``` and ```Plotly``` plots.

**GeoPandas Europe plot**

<img src="/output/geopandas_europe.jpg">

**GeoPandas world plot**

<img src="/output/geopandas_world.jpg">

**Plotly Europe plot**

<img src="/output/plotly_europe.png">

**Plotly world plot**

_download_ html file from the [output folder](https://github.com/sarah-hvid/Final_assignment_lang/blob/main/output/plotly_world.html)

**Folium world plot**

_download_ html file from the [output folder](https://github.com/sarah-hvid/Final_assignment_lang/blob/main/output/folium_plot.html)

 
## References
Andersen, S. H. (2022). "An Evaluation of state-of-the-art NLP Models on Historic text in Danish", from https://github.com/sarah-hvid/Bachelor_ibsen/blob/main/Thesis_Ibsen_04-01-22.pdf & https://github.com/sarah-hvid/Bachelor_ibsen/blob/main/scripts/BeautifulSoup.ipynb

University of Oslo. (2017, December 14). Henrik Ibsens skrifter: Brev. https://www.ibsen.uio.no/brevkronologi.xhtml
