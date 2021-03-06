#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse

try:
    from sh import grep, ErrorReturnCode
except ImportError:
    print("[Error] Please install sh")
    sys.exit(1)

try:
    from termcolor import colored
except ImportError:
    print("[Error] Please install termcolor")
    sys.exit(1)

try:
    from beautifultable import BeautifulTable
except ImportError:
    print("[Error] Please install BeautifulTable")
    sys.exit(1)

secretsFileList = 'config/secretFiles.txt'

# Regex patters to search for interesting things in the file
searchDict = {
    "URL": ["-oriahE", "https?://[^\"\\'> ]+"],
    "Upload Fields": ["-HnriE", "\u003cinput[^\u003e]+type=[\"']?file[\"']?"],
    "Tokens": ["-HriE", "(token|xsrf|csrf)"],
    "Server": ["-hri", "server: "],
    "Secrets": ["-HanriE", "(aws_access|aws_secret|api[_-]?key|ListBucketResult|S3_ACCESS_KEY|Authorization:|RSA PRIVATE|Index of|aws_|secret|ssh-rsa AA)"],
    "IP": ["-HnroE", "(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])[file:///\\.)%7b3%7d([0-9]|[1-9][0-9]|1[0-9]%7b2%7d|2[0-4][0-9]|25[0-5])]\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"],
    "Hex": ["-HnroE", "([^A-Fa-f0-9+/]|^)(7[bB]22|613[aA]|4[fF]3[aA]|733[aA]|3[cC]3[fF]78|68747470733[aA]|687474703[aA])[A-Fa-f0-9]+={0,2}"],
    "Debug Pages": ["-HnraiE", '(Application-Trace|Routing Error|DEBUG"? ?[=:] ?True|Caused by:|stack trace:|Microsoft .NET Framework|Traceback|[0-9]:in `|#!/us|WebApplicationException|java\\.lang\\.|phpinfo|swaggerUi|on line [0-9]|SQLSTATE)'],
    "Base64": ["-HnroE", "([^A-Za-z0-9+/]|^)(eyJ|YTo|Tzo|czo|PD[89]|aHR0cHM6L|aHR0cDo|rO0|/wE|%2[fF]wE|AAEAAD)[%a-zA-Z0-9+/]+={0,2}"],
    "AWS Key": ["-HanrE", "([^A-Z0-9]|^)(AKIA|A3T|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{12,}"]
}

def parseExtractedData(sourceDir, filename):
    resultsDict = {}
    filePathArry = []
    print("[Info] Analyzing files. Please wait...")
    if sourceDir:
        filePathArry = getAllFiles(sourceDir)
    else: # filename
        filePathArry.append(filename)

    for filePath in filePathArry:
        for searchType in searchDict.keys():
            searchTypeOutput = searchTypeCommon(searchType, filePath)
            if searchTypeOutput is None: # No Match, skip iteration
                continue

            if searchType in resultsDict: # handle multiple match
                searchTypeOutput = resultsDict[searchType][0] + "\n" + searchTypeOutput

            if searchTypeOutput: # handle single match
                resultsDict[searchType] = [searchTypeOutput]

        commentsOutput = searchComments(filePath)

        if commentsOutput is not None:
            if "searchComments" in resultsDict:  # handle multiple match
                commentsOutput = resultsDict["searchComments"][0] + "\n" + commentsOutput

            if commentsOutput:  # handle single match
                resultsDict["searchComments"] = [commentsOutput]

        s3bucketOutput = getS3Buckets(filePath)
        if s3bucketOutput is not None:
            if "S3Buckets" in resultsDict:  # handle multiple match
                s3bucketOutput = resultsDict["S3Buckets"][0] + "\n" + s3bucketOutput

            if s3bucketOutput:  # handle single match
                resultsDict["S3Bucket"] = [s3bucketOutput]

        # check files that contains secrets
        secretFilesArry = getListFilesSecrets()
        if (checkSecretFileExists(filePath, secretFilesArry)):
            if "secretFiles" in resultsDict:
                resultsDict["secretFiles"] = [resultsDict["secretFiles"][0] + "\n" + filePath]
            else:
                resultsDict["secretFiles"] = [filePath]
    printTable(resultsDict)

# Get list of all files or sub dir inside a particular dir
def getAllFiles(sourceDir):
    filePathArry = []
    for root, dirs, files in os.walk(sourceDir, topdown=True):
        for name in files:
            filePath = os.path.join(root, name)
            filePathArry.append(filePath)
    return filePathArry

# method to grep common regex patters
def searchTypeCommon(searchType, filename):
    try:
        searchTypeFlag = searchDict[searchType][0]
        searchTyperegex = searchDict[searchType][1]
        output = grep(searchTypeFlag, searchTyperegex, filename)
        if output:
            output = output.strip()
            return output
        return None
    except ErrorReturnCode:
        # print("No match found")
        pass

# method to extract comments
def searchComments(filename):
    try:
        output = grep(grep("-HaniE", "(api|s3|key|secret|pass|aws|azure|github|admin)", filename), "-vi", "copyright")
        output = output.strip()
        return output
    except ErrorReturnCode:
        # print("No match found")
        pass

# Method to extract S3buckets
def getS3Buckets(filename):
    try:
        output = grep("-hrioaE", "-e", "[a-z0-9.-]+\\.s3\\.amazonaws\\.com",
                      "-e", "[a-z0-9.-]+\\.s3-[a-z0-9-][file:///\\.amazonaws\.com]\\.amazonaws\\.com",
                      "-e", "[a-z0-9.-]+\\.s3-website[.-](eu|ap|us|ca|sa|cn)",
                      "-e", "//s3\\.amazonaws\\.com/[a-z0-9._-]+",
                      "-e", "//s3-[a-z0-9-]+\\.amazonaws\\.com/[a-z0-9._-]+", filename)
        output = output.strip()
        return output
    except ErrorReturnCode:
        # print("No match found")
        pass

# get list of files containing secrets
def getListFilesSecrets():
    if os.path.exists(secretsFileList):
        with open(secretsFileList, 'r') as file:
            # readlines methods adds a new line character. Hence using read and splitting it
            return file.read().splitlines()
    elif IOError:
        print ("[Error] Error occured while trying to read file: " + secretsFileList)

# check if file containing secret exists
def checkSecretFileExists(filePath, secretFilesArry):
    for fileName in secretFilesArry:
        if fileName in filePath:
            return True
    return False


# ToDo
# Search for file names that usually contains secrets.
# See list in https://github.com/Plazmaz/leaky-repo
# Handle zip files
# perform string on the executables to extract important stuff

# Create table
def printTable(resultsDict):
    for result in resultsDict:
        parenttable = BeautifulTable(max_width=100, default_alignment=BeautifulTable.ALIGN_LEFT)
        parenttable.set_style(BeautifulTable.STYLE_GRID)
        subtable = BeautifulTable(default_alignment=BeautifulTable.ALIGN_LEFT)
        #table.column_headers = [colored(result, attrs=['bold', 'blink'], on_color='on_red')]
        #table.column_headers = [colored(result, 'cyan', attrs=['bold'])]
        matchedValueArry = resultsDict[result][0].split("\n")
        for matchedValue in matchedValueArry:
            subtable.append_row([matchedValue])
        parenttable.append_row([colored(result, 'cyan', attrs=['bold']), subtable])
        print(parenttable)
        print("")

###############################################################################
# Main
###############################################################################

def main():
    parser = argparse.ArgumentParser(description='Uninteresting')
    parser.add_argument("-d", "--dir", default=None,
                        required=False,
                        help="Directory to Analyze")
    parser.add_argument("-f", "--file", default=None,
                        required=False,
                        help="File to Analyze")
    return parser.parse_args()


if __name__ == '__main__':
    args = main()
    if args.dir is None and args.file is None:
        print("[Error] Please pass the directory name or file name to continue")
        sys.exit(1)
    parseExtractedData(args.dir, args.file)
