#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Requirements: sh, PrettyTable
# Credits:
# i. Tomnomnom gf tool (https://github.com/tomnomnom/gf)
# ii. Ryan Wendel

import sys
import os
import argparse

try:
    from sh import grep, ErrorReturnCode
except ImportError:
    print("[Error] Please install sh")
    sys.exit(1)

try:
    from prettytable import PrettyTable
except ImportError:
    print("[Error] Please install prettytable")
    sys.exit(1)

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
    if sourceDir:
        filePathArry = getAllFiles(sourceDir)
    else: # filename
        filePathArry.append(filename)

    for file_path in filePathArry:
        for searchType in searchDict.keys():
            searchTypeOutput = searchTypeCommon(searchType, file_path)
            if searchType in resultsDict:
                searchTypeOutput = resultsDict[searchType][0] + "\n" + searchTypeOutput
            if searchTypeOutput:
                resultsDict[searchType] = [searchTypeOutput]

        commentsOutput = searchComments(file_path)
        if "searchComments" in resultsDict:
            commentsOutput = resultsDict["searchComments"][0] + "\n" + commentsOutput
        if commentsOutput:
            resultsDict["searchComments"] = [commentsOutput]

        s3bucketOutput = getS3Buckets(file_path)
        if "S3Buckets" in resultsDict:
            s3bucketOutput = resultsDict["S3Buckets"][0] + "\n" + s3bucketOutput
        if s3bucketOutput:
            resultsDict["S3Buckets"] = [s3bucketOutput]
    printExtractedData(resultsDict)

# Get list of files or dir in a particular dir
def getAllFiles(sourceDir):
    filePathArry = []
    for root, dirs, files in os.walk(sourceDir, topdown=True):
        for name in files:
            filePath = os.path.join(root, name)
            filePathArry.append(filePath)
    return filePathArry

# method to handle common grep commands
def searchTypeCommon(searchType, filename):
    try:
        searchTypeFlag = searchDict[searchType][0]
        searchTyperegex = searchDict[searchType][1]
        output = grep(searchTypeFlag, searchTyperegex, filename)
        output = output.strip()
        return output
    except ErrorReturnCode:
        # print("No match found")
        pass

# Method to run grep command to extract comments
def searchComments(filename):
    try:
        output = grep(grep("-HaniE", "(api|s3|key|secret|pass|aws|azure|github|admin)", filename), "-vi", "copyright")
        output = output.strip()
        return output
    except ErrorReturnCode:
        # print("No match found")
        pass

# Method to run grep command to extract S3buckets
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


def printExtractedData(resultsDict):
    for result in resultsDict:
        printTable([result], resultsDict[result])

# Print Lists as Tabular Data
def printTable(headerArry, rowArry):
    table = PrettyTable(headerArry)
    # align left
    table.align = "l"
    table.add_row(rowArry)
    print(table)
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
