"""
A script for preprocessing the XML-format Ibsen letters and gathering named entities.
"""
# base tools
import argparse
import os
import glob
from pathlib import Path

# data tools
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

# nlp tools
import dacy
from thefuzz import fuzz
from thefuzz import process


def parse_args():
    '''
    Function that specifies the available arguments.
    '''
    ap = argparse.ArgumentParser()
    
    # command line parameters
    ap.add_argument("-p", "--preprocess", required = False, type = bool, default = 0, help = "Run only the preprocessing? This requires that the dacy CSV has already been created.")
        
    args = vars(ap.parse_args())
    return args


def clean_name(name):
    '''
    Function that returns the filename of a full path string. 
    
    name: string, filepath
    '''
    split_filename = name.split("/")[-1]
    file_only = split_filename.split(".")[0]
    
    return file_only


def parse_xml_files():
    '''
    Function that parses the XML files in the 'xml' folder. The text of the files is written to text files in the 'txt' folder.
    '''
    file_list = glob.glob(os.path.join('data', 'xml', '*.xml'))
    
    # check if txt folder exists, create it if not
    Path("data/txt/").mkdir(parents = True, exist_ok = True)
    outpath = os.path.join('data', 'txt/')
    
    for file in file_list:
        with open(file) as f_input:
            corpus = ''
            soup = BeautifulSoup(f_input, 'xml')
            
            # only keeping the p-tags that are the body of the text and excluding the adress line
            all_p = soup.find_all(["p"])
            for tag in all_p:
                corpus += tag.get_text().strip().replace("\n", "")
                
            file_name = clean_name(file)
            text_file = open(outpath + F"{file_name}.txt", "w")
            text_file.write(corpus)
            text_file.close()
    return 


def gather_text():
    '''
    Function that reads the text in the txt files of the 'txt' folder. The filename and text is returned in a list.
    '''
    file_list = glob.glob(os.path.join('data', 'txt', '*.txt'))
    text = []
    files = []

    for file in file_list:
        with open(file, encoding = 'utf8') as f_input:
            t = f_input.read()
            text.append(t)

            file_name = clean_name(file)
            files.append(file_name)        
    return files, text


def dacy_loc(text):
    '''
    Function that fits the Dacy large model on a list of text documents and finds all named entities that are locations. 
    
    text: a list of texts.
    '''
    nlp = dacy.load("da_dacy_large_trf-0.1.0")
    ents = []
    
    for doc in tqdm(nlp.pipe(text, disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]), total = len(text)):
        in_list = []

        for e in doc.ents:
            if e.label_ == 'LOC':
                in_list.append((e.text))
        ents.append(in_list)
    return ents


def create_dataframe(files, text, ents):
    '''
    Function that creates a 'csv' folder and a dataframe of the files, text and entities found. 
    
    files: a list of filenames
    text: a list of the text found in those filenames
    ents: a list of the entities found in the text
    '''
    # check if csv folder exists, create it if not
    Path("data/csv/").mkdir(parents = True, exist_ok = True)
    
    lists = {'files': files, 'text': text, 'dacy_large': ents}
    df = pd.DataFrame.from_dict(lists, orient = 'index').transpose()
    
    # exploding the elements of the list created by dacy
    df = df[['files', 'dacy_large']].explode('dacy_large')
    df.to_csv(os.path.join('data', 'csv', 'loc_dacy_large_exp.csv'), encoding = 'utf-8', index = False)
    return 


def remove_s_ending(df):
    '''
    Function that removes the -s ending from the locations in the dataframe (e.g., Danmarks : Danmark).
    
    df: a dataframe that has a column named 'dacy_large' with locations.
    '''
    # a list of names that should not have their -s ending removed
    keep = ['Als', 'Hals', 'Heliopolis', 'Helsingfors', 'Hinterhaus', 'Kaukasus', 'Libanius', 'Bruxelles',
              'New-Orleans', 'Paris', 'Refsnæs', 'Tunis', 'Wales', 'Falsens', 'Basileus', 'Gossensass']

    # looping over the dataframe
    for i,r in df.iterrows():
        loc = r['dacy_large']
        loc = str(loc)

        if loc.endswith('s'):
            if loc not in keep:
                new_name = loc[:-1] # removing the last letter
                
                # using the index to replace the values in the dataframe
                df.loc[i, 'dacy_large'] = new_name
    return df


def fuzzy_correction(df):
    '''
    Function that uses Levenshtein Distance to compare strings to correct different and historic spellings. If the match similarity score is above or equal to 80 it is saved for replacement in the dataframe. A list has been predefined to compare the dataframe values to for simplicity. 
    
    df: a dataframe that has a column named 'dacy_large' with locations.
    '''
    # creating the lists that will be compared
    df_names = list(df.dacy_large.unique())
    correct_names = ['Amerika', 'Appenninerne', 'Basileus', 'Bayern', 'Bergens teater', 'Burgtheater', 'Christiania Theater', 'Finland', 'Florenz', 'Frankrig', 'Frederikshavn', 'Grand Hotel Oslo', 'København', 'Königsbrücker-Strasse, No 33.', 'Dresden', 'Petersborg', 'Rom', 'Schellingstrasse 30.', 'Schweiz', 'Sorrento', 'Sverige', 'Østrig']
    replace = []

    # looping through the correct spellings and comparing them to the values from the df
    for loc in correct_names:
        matches = process.extract(loc, df_names) # returns a list of 5 tuples
        for match in matches: # for tuple in list
            
            # if the match is not the same as the input and the score is above 80 save it.
            if match[0] != loc:
                if match[1] >= 80:
                    result = (match[0], loc)
                    replace.append(result)

    replace_dict = dict(replace)

    # Using the dictionary to replace the keys with the values in the 'dacy' column 
    df.dacy_large = df.dacy_large.replace(replace_dict)
    return df


def preprocess_ents():
    '''
    Function that loads the dacy data and preprocesses the output by removing values and correcting spellings. A dataframe that contains the number of occurences of each location is then created and saved.
    '''
    file_path = os.path.join('data', 'csv', 'loc_dacy_large_exp.csv')
    df = pd.read_csv(file_path)
    
    # remove specific results (problematic in later steps)
    remove = ['.', '’', 'St.\xa0', 's', 'Øie', 'Måské', 'Mai', 'Ala', 'August', 'Bergliot', 'Brandes', 'Byen', 'Catilina', 'Gaden', 'Gage', 'Humbug', 'Jorden', 'Jupiter', 'Kasino', 'Kbh.', 'Kolera', 'Kr: teater', 'Mars', 'Marts', 'Myron', 'Posten', 'Maaské', 'Kastanienallee 19/20.']

    df = df[~ df['dacy_large'].isin(remove)]
    df['dacy_large'] = df['dacy_large'].str.replace('å', 'aa')
    
    # apply function removing the s endings (e.g., Danmarks : Danmark)
    df = remove_s_ending(df)
    
    # apply function that fuzzy corrects many names
    df = fuzzy_correction(df)

    # count each occurence and save the file
    occur = df.groupby(['dacy_large']).size()
    
    df_o = pd.DataFrame(data = occur, columns = ['count']).rename_axis("loc").reset_index()
    path = os.path.join('data', 'csv', 'loc_count.csv')
    df_o.to_csv(path, index = False)
    return


def main():
    '''
    The process of the script from the creation of all files or from the preprocessing of the dacy CSV file. 
    '''
    # parse argument
    args = parse_args()
    p_only = args['preprocess']
    
    if p_only == False:
        print('[INFO] Parsing xml files ...')
        parse_xml_files()
        print('[INFO] Gathering text')
        files, text = gather_text()
        print('[INFO] Getting named entities')
        ents = dacy_loc(text)
        create_dataframe(files, text, ents)
        print('[INFO] Preprocessing results')
        preprocess_ents() 
        print('[INFO] Script success')

    if p_only == True:
        print('[INFO] Preprocessing results ONLY')
        preprocess_ents() 
        print('[INFO] Script success')
    
    return


if __name__ == '__main__':
    main()