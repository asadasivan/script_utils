#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

# A class containing methods to create HTML table or JSON report from python dict


class CustomReport:
    def __init__(self, findingsDict, headerArry):
        self.findingsDict = findingsDict
        self.headerArry = headerArry

    '''
    ########################## HTML Report #################################################################################
    '''
    # Create HTML table
    def createHTMLReport(self, reportFile, reportTitle):
        print("[Info] Creating HTML report...")
        with open(reportFile, 'w') as fileHandle:
            fileHandle.write("<!doctype html>" + "\n")
            fileHandle.write("<html lang='en-US'>" + "\n")
            fileHandle.write("<head>" + "\n")
            fileHandle.write("<!-- The line below is to make sure it uses the right encoding format  -->" + "\n")
            fileHandle.write("<meta name=viewport content='width=device-width, initial-scale=1'>")
            fileHandle.write("<meta http-equiv='Content-Type' content='application/xhtml+xml; charset=UTF-8' />" + "\n")
            fileHandle.write("<link rel='stylesheet' href='https://cdn.datatables.net/1.10.19/css/dataTables.bootstrap4.min.css' integrity='sha384-EkHEUZ6lErauT712zSr0DZ2uuCmi3DoQj6ecNdHQXpMpFNGAQ48WjfXCE5n20W+R' crossorigin='anonymous'>" + "\n")
            fileHandle.write("<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.css' integrity='sha384-2QMA5oZ3MEXJddkHyZE/e/C1bd30ZUPdzqHrsaHMP3aGDbPA9yh77XDHXC9Imxw+' crossorigin='anonymous'>" + "\n")
            fileHandle.write("<script src='https://code.jquery.com/jquery-3.3.1.js' integrity='sha384-fJU6sGmyn07b+uD1nMk7/iSb4yvaowcueiQhfVgQuD98rfva8mcr1eSvjchfpMrH' crossorigin='anonymous'></script>" + "\n")
            fileHandle.write("<script src='https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js' integrity='sha384-rgWRqC0OFPisxlUvl332tiM/qmaNxnlY46eksSZD84t+s2vZlqGeHrncwIRX7CGp' crossorigin='anonymous'></script>" + "\n")
            fileHandle.write("<script src='https://cdn.datatables.net/1.10.19/js/dataTables.bootstrap4.min.js' integrity='sha384-uiSTMvD1kcI19sAHJDVf68medP9HA2E2PzGis9Efmfsdb8p9+mvbQNgFhzii1MEX' crossorigin='anonymous'></script>" + "\n")
            fileHandle.write("<!-- This is required for collapse -->" + "\n")
            fileHandle.write("<script src='https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js' integrity='sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM' crossorigin='anonymous'></script>" + "\n")
            fileHandle.write("<!-- All custom event handling, css is mentioned below -->" + "\n")
            fileHandle.write("<script type='text/javascript' src='assets/js/custom_report.js'></script>" + "\n")
            fileHandle.write("<link rel='stylesheet' href='assets/css/custom_report.css'>" + "\n")
            fileHandle.write("</head>" + "\n")
            fileHandle.write("<body>")
            fileHandle.write("&nbsp;")
            fileHandle.write("&nbsp;")
            fileHandle.write("<h4 align='center'> <font color='blue'> " + reportTitle + " </font> </h4>" + "\n" + "\n")
            fileHandle.write("<table id='example' class='table table-striped table-bordered'>")

            # Create column header
            fileHandle.write("\n\t" + "<thead>" + "\n" + "\t\t" + "<tr>" + "\n")
            for header in self.headerArry:
                fileHandle.write("\t\t\t" + "<th>" + header + "</th>" + "\n")
            fileHandle.write("\t\t" + "</tr>" + "\n\t" + "</thead>" + "\n")
            fileHandle.write("\t" + "<tbody>" + "\n")

            # create rows
            fileHandle.write("\t\t" + "<tr>" + "\n")
            rowNumber = 0

            for row in self.findingsDict:
                rows = self.findingsDict[row]
                for col in rows:
                    colStr = None
                    lines = None
                    # check if col is array and convert it to string
                    if isinstance(col, list):
                        lines = len(col)  # no. of lines
                        # To handle Array with one value
                        if lines == 1:
                            colStr = col[0]
                            # To handle string operations when value is None
                            if colStr is None:
                                colStr = "Null"
                        else:
                            colStr = "\n".join(col)
                            colStr = colStr.replace("\n", "<br />")
                    else:
                        lines = 1
                        colStr = col
                        # To handle string operations when value is None
                        if colStr is None:
                            colStr = "Null"
                        colStr = colStr.replace("\n", "<br />")
                    
                    # perform collapsible if more lines are in the cell
                    if lines > 3:
                        rowNumber = rowNumber + 1  # required to create unique div id
                        fileHandle.write("\t\t\t" + "<td>" + "\n")
                        fileHandle.write("\t\t\t\t" + "<div class='container'>" + "\n")
                        fileHandle.write("\t\t\t\t\t\t" + "<a href='#demo" + str(rowNumber) + "' data-toggle='collapse'> Show/Hide details </a>" + "\n")
                        fileHandle.write("\t\t\t\t\t\t" + "<div id='demo" + str(rowNumber) + "' class='collapse'>" + "\n")
                        fileHandle.write("\t\t\t\t\t\t\t" + colStr + "\n")
                        fileHandle.write("\t\t\t\t\t\t" + "</div>" + "\n")
                        fileHandle.write("\t\t\t\t" + "</div>" + "\n")
                        fileHandle.write("\t\t\t" + "</td>" + "\n")
                    else:
                        fileHandle.write("\t\t\t" + "<td>" + colStr + "</td>" + "\n")
                fileHandle.write("\t\t" + "</tr>" + "\n")

            fileHandle.write("\t" + "</tbody>" + "\n")
            fileHandle.write("\t" + "</table>" + "\n")
            fileHandle.write("</body>" + "\n")
            fileHandle.write("</html>" + "\n")
       
        print("[Done] Custom HTML report successfully created: " + reportFile)

    '''
    ########################## JSON Report #################################################################################
    '''
    # Convert a Dict to JSON. keyArry is same as table header.
    def createJSONReport(self, reportFile, keyArry=None):
        print("[Info] Creating JSON report...")
        keyArry = self.headerArry
        jsonArry = []
        violationsDict = {}
        keylength = len(keyArry)
        for row in self.findingsDict:
            findings = self.findingsDict[row]
            rowDict = {}
            for i in range(keylength):
                rowDict[keyArry[i]] = findings[i]
            jsonArry.append(rowDict)
        violationsDict["findings"] = jsonArry

        with open(reportFile, 'w', encoding="utf-8") as fileHandle:  # enter the output filename
            # json.dump(violationsDict, fileHandle, indent = 4, , sort_keys=True)
            json.dump(violationsDict, fileHandle, indent=4)

        print("[Done] Custom JSON report successfully created: " + reportFile)
