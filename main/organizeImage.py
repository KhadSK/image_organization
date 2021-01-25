import json
from pathlib import Path
import os
import time
import subprocess
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import re
import shutil
import skimage
from skimage import data, io
from matplotlib import pyplot


def main():
    listOfValue = []
    try:
        if os.path.getsize(pathDirIn):
            for root, dirs, files in os.walk(pathDirIn):
                for subdir in dirs:
                    pathSubdir = root + '/' + subdir
                    # test if dir contains html page
                    if '/www.fishbase.de/photos' in pathSubdir and os.listdir(pathSubdir):
                        for file in os.listdir(pathSubdir):
                            if file.endswith('.html'):
                                pathWebPage = pathSubdir + '/' + file
                                ##print ('web page existe : ', pathWebPage)
                                
                    # test if dir contains pictures
                    if '/www.fishbase.de/images/species' in pathSubdir and os.listdir(pathSubdir):
                        ##print ('species directory existe ', pathSubdir)
                        # extract family name and create dir with family name
                        familyName = pathSubdir.split('/')[4]
                        pathDirFamilyOut = './src/out/fishbase_organized/' + familyName
                        Path(pathDirFamilyOut).mkdir(parents=True, exist_ok=True)
                        # open / read html page
                        with open (pathWebPage, 'r') as webPage:
                            content = webPage.read()
                            soup = BeautifulSoup(content, 'lxml')
                            # return balise with species name
                            table = soup.find_all('a', href= re.compile(r'https://www\.fishbase\.de/photos/PicturesSummary\.php'))
                        
                        # match pictures name, copy, remane species name
                        for pictureName in os.listdir(pathSubdir):
                            ##print(pictureName)
                            try:  
                                for p in table:
                                    ## type p = <class 'bs4.element.Tag'>
                                    # match pictures name with species tag name in html page
                                    if p.find('i') and pictureName in str(p):
                                        scientificName = p.find('i').text
                                        newPictureName = ('{0}_picture_' + pictureName).format(str.replace(scientificName,  ' ', '_'))
                                        ##print ('new picture name : ' + newPictureName)
                                        
                                        # copy pictures
                                        pathDestinationDir = pathDirFamilyOut
                                        sourceFile = pathSubdir + '/' + pictureName
                                        shutil.copy(sourceFile, pathDestinationDir)
                                        ##print ('destination dir : ' + pathDestinationDir + ' source file : ' + sourceFile)
                                        # rename pictures
                                        destinationFileName = os.path.join(pathDestinationDir, pictureName)
                                        newDestinationFileName = os.path.join(pathDestinationDir, newPictureName)
                                        os.rename(destinationFileName, newDestinationFileName)
                                        ##print ('new file name : ' + newDestinationFileName)
                                        # picture pixel values : prepare to analysis
                                        currentPictureValue = io.imread(newDestinationFileName).shape
                                        newPictureValue = currentPictureValue + (newPictureName, scientificName, familyName)
                                        ##print('picture pixel values : ' + str(newPictureValue))
                                        listOfValue.append(newPictureValue)
    
                            except:
                                # don't find tag
                                continue   
                    else:
                        #print('species directory not existe ', pathSubdir)
                        pass
        else: 
            #print ('file does not existe or is not accessible ', pathDirIn)
            pass
                                
                                    
    except OSError as e:
        print ('Erreur : ', e.errno, ' - ', e.strerror)
        ##continue
        
    print(listOfValue)
    # example : (480, 640, 3, 'Acanthurus_nigricauda_picture_Acnig_us.jpg', 'Acanthurus nigricauda', 'Acanthuridae')
    y_val = [i[0] for i in listOfValue]
    x_val = [i[1] for i in listOfValue]
    pic_name_val = [i[3] for i in listOfValue]
    sci_name_val = [i[4] for i in listOfValue]
    fam_name_val = [i[5] for i in listOfValue]
    
    fig = pyplot.figure()
    ax = fig.add_subplot()    
    
    ax.scatter(x_val, y_val)
    
    #for xy in zip(x_val, y_val):
    #    ax.annotate('(%s, %s)' % xy, xy=xy, textcoords='data')
    
    for i, txt in enumerate(sci_name_val):
        ax.annotate(txt, (x_val[i], y_val[i]))
    
    pyplot.grid()
    pyplot.show()
    

def writeFamilyFailedFile(file, returnCode, fam):
    jdataFailed = json.load(file)
    #add family with error code
    fam['returnCode'] = returnCode
    jdataFailed['family'].append(fam)
    json.dump(jdataFailed, open(pathFailedFamily,'w', encoding='utf-8'))  
    logging.debug('write - modification : '+ str(jdataFailed))

def createInitFamilyFailedFile():
    with open(pathFailedFamily, 'w+', encoding='utf-8') as file: 
        data = {'family':[{'id': None, 'name': None}]}
        json.dump(data, file, ensure_ascii=False)
        logging.debug('create file json family failed : '+ file.name)
        file.close()

def createInitLogger():
    # create log file
    with open(pathLog,'a+') as f:
        f.write('log file : ' + pathFailedFamily + '\n')
        f.close()
    # DEBUG, INFO, WARNING, ERROR
    logging.basicConfig(filename=pathLog, 
                        format='%(asctime)s : %(levelname)s : %(message)s', 
                        datefmt='%Y/%m/%d %H:%M:%S', 
                        encoding='utf-8', 
                        level=logging.DEBUG)
                        

if __name__ == "__main__":
    dateTime = datetime.today().strftime('%Y%m%d %H:%M:%S')
    # ./src/in/test_family.json
    pathDirIn = './src/in'
    pathSubDirFishbase = '/fishbase'
    pathFailedFamily = './log/json/family ' + dateTime + '.json'
    pathLog = './log/' + dateTime + '.log'
    familyName = None
    familyId = None
    urlWebPage = ''
    dirWebOutput = ''    
    main()