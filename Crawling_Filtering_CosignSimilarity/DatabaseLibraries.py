# Define a function which prints out the output and writes the same thing on the html output file.
def submitAndPrint (statsFile, title, printableString):
    print title + printableString, '\n'
    
    statsContext = "<td>" + printableString + "</td>"
    statsFile.write(statsContext)
