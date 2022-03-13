from os import listdir, remove
from os.path import isfile, join
from os import path
from posixpath import basename
from PIL import Image, ExifTags
import os,time
import re
import pandas as pd
from sqlalchemy import false, null
import csv

def remove_duplicates(base_path: str, test: bool = False, files: list = None):
    if test == False:
        print('Wel deleten')

    if files is None:
        print('Reading directory '+base_path)
        files = listdir(base_path)
    else:
        print('Reading provided list')
        print(files)

    print('number of files: '+str(len(files)))

    counter = 1
    table = []
    pattern = '^([^\(\)]+)(\(\d+\))?(\..+)$'
    for i in range(len(files)):
        f = files[i]
        if f == '.DS_Store':
            continue
        file_path = base_path+'/'+f
        basename = re.sub(pattern,r'\1',f)

        try:
            exif_created = get_exif_date_created(file_path)
        except Exception as e:
            print(str(counter)+': [Cannot get exif info] '+file_path)
            continue            

        file_size = os.path.getsize(file_path)        
        line = dict(filename = f,basename = basename,date_created = exif_created,file_size = file_size)
        table.append(line)
        print(str(counter)+': '+file_path)
        counter += 1

    # create Pandas dataframe
    df = pd.DataFrame.from_records(table)

    # select duplicates by basename, date created
    g = df.groupby(['basename','date_created']).agg({'file_size':['min','max','count']}).reset_index()
    g.reset_index()

    duplicates = g[(g[('file_size','count')] > 1)]

    # delete duplicates by keeping the variant with the largest file size
    counter = 1
    for index, row in duplicates.iterrows():
        items = df[(df['basename'] == row['basename'][0]) & (df['date_created'] == row['date_created'][0])].sort_values(by=['file_size'],ascending=False).iloc[1: , :]
        for i,r in items.iterrows():
            file_to_delete = base_path+'/'+r['filename'] 
            if path.exists(file_to_delete):
                if test is False:
                    os.remove(file_to_delete)
                print(str(counter)+' [Delete]: '+file_to_delete)
            else:
                print(str(counter)+': [Already deleted] '+file_to_delete)
            counter += 1

def get_exif_date_created(file_path):
    try:
        img = Image.open(file_path)
    except Exception as e:
        raise Exception(e)

    exif_date_created_key = 306
    exifinfo = img.getexif()
    if exifinfo is None:
        raise Exception("Cannot read exif info")

    if exif_date_created_key not in exifinfo.keys():
        raise Exception("No date created tag")   
    else:
        exif_created = exifinfo[exif_date_created_key]  

    return exif_created

def get_basename(filename):
    pattern = '^([^\(\)]+)(\(\d+\))?(\..+)$'
    basename = re.sub(pattern,r'\1',filename)    
    return basename

def analyse_missing():
    counter = 0
    with open("/Users/nadiastolte/Downloads/File Currently Available-2016.txt", newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        for row in reader:
            full_path = row['Full Path']
            year = full_path.split('/')[4]
            filename = full_path.split('/')[5]
            rootdir = '/Users/nadiastolte/Pictures/'+year
            basename = get_basename(filename)
            regex = re.compile(basename)

            found = False

            for root, dirs, files in os.walk(rootdir):
                for file in files:
                    if regex.match(file):
                        found = True
                        found_name = file
                        break

            if found is False:
                counter += 1
                print(str(counter)+': Cannot find '+full_path+' - '+basename)


remove_duplicates('/Users/nadiastolte/Pictures/2017')
# remove_duplicates('/Users/nadiastolte/Pictures/2017',True,['IMG_7502-438.jpg','IMG_7502.jpg','IMG_7502(1).jpg','IMG_7502(2).jpg'])
# remove_duplicates('/Users/nadiastolte/Pictures/2016',['IMG_5719 (1).JPG','IMG_5719 (3).JPG','IMG_5719.JPG','IMG_5719(99).JPG','IMG_5719 (2).JPG'])

#print(get_exif_date_created('/Users/nadiastolte/Pictures/2016/IMG_7983.JPG'))
#get_exif_date_created('/Users/nadiastolte/Pictures/2016/IMG_0970.JPG')

#analyse_missing()

'''
mypath = BASE_PATH+'/2018'
print(mypath)
files = listdir(mypath)
print(files[504])
'''