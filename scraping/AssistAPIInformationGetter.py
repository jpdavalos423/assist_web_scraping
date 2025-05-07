import requests
'''
This file contains multiple functions that return information from the assist.org api
For more information on the api, look at the github readme on the repo in the articulation doc
'''

# Dictionary showing which community colleges are known as others
# ex: Compton Community College is known as Compton College
CCsdups = {"Compton College": "Compton Community College", "Santa Ana College": "Rancho Santiago College", "Reedley College":"Kings River College",
           "Berkeley City College":"Vista Community College"}
# gets the API data from the correct url as specified through APIType
def getAPIData(APIType):
    BacicURL = "https://assist.org/api/"
    endpoint = APIType
    data = requests.get(BacicURL + endpoint).json()
    return data

# 
# def GetRepeatCCs():
#     Repeats = []
#     data = getAPIData("institutions")
#     for i in range(len(data)):
#         if len(data[i]["names"]) > 1 and data[i]["names"] not in Repeats:
#             Repeats.append(data[i]["names"])
#     return Repeats
# GetRepeatCCs()

# gets the id for the university or CC given the name from the Assist API. If there is an error in this returns -1
def getSchoolID(schoolName):
    # get the dictionary for the institution data
    data = getAPIData("institutions")
    # find the instituion in the dictionary and get the id
    for i in range(len(data)):
        NamesList = data[i].get("names")
        for names in NamesList:
            if schoolName == names.get('name'):
                return data[i].get('id')
             
    return -1

# get the name of the institution from the id
def getSchoolFromID(id):
    data = getAPIData("institutions")
    # find the id and then get the institution
    for i in range(len(data)):
        if id == data[i].get("id"):
            NamesList = data[i].get("names")
            return NamesList[0].get('name')
             
    return -1

# get a list of all CC ids
def getCCIdList():
    CCids = []
    # get the dictionary for the institution data
    data = getAPIData("institutions")
    # find the instituion in the dictionary and get the id
    for i in range(len(data)):
        if data[i].get("isCommunityCollege"):
            CCids.append(data[i].get("id"))
    return CCids       

# get the names of all the CCs
def getCCNameList():
    CCIds = getCCIdList()
    CCNames = []
    for ccid in CCIds:
        CCNames.append(getSchoolFromID(ccid))
    return CCNames

# For a particular university, get a list of CCs it has 2022 - 2023 agreements with
def getCCListWithAggreements(UniName):
    URL = "https://assist.org/api/institutions/" + str(getSchoolID(UniName)) + "/agreements"
    data = requests.get(URL).json()
    CClst = []
    for cc in data:
        if cc["isCommunityCollege"] and 73 in cc["sendingYearIds"] and cc["institutionName"] not in CClst:
            CClst.append(cc["institutionName"])
    return CClst

# gets the list of unique CCs(if a CC is known as another it will not be added)
def getUniqueCCNamelst():
    cclist = []
    ccidlist = getCCIdList()
    for ccid in ccidlist:
        CCName = getSchoolFromID(ccid)
        if(CCName in CCsdups.values()):
            continue
        else:
            # print(getSchoolFromID(ccid))
            cclist.append(CCName)
    return cclist
