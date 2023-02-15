#!/usr/bin/python3

import subprocess
import sys,os
print(os.getcwd())

assert(len(sys.argv)==2)

texFileDir = "/home/mattkab2/Git/LatexEqSnippingTool/eqs/"
outputDir = "/home/mattkab2/Git/LatexEqSnippingTool/pngs/"
eqDigits = 2
eqDict = {}
eqContexts = ["align","align*","equation","equation*"]
pkgContexts = ("\\usepackage","\\newcommand","\\Declare")
eqCounter = 0

def scanFile(fname,dest,pkgs):
    global eqCounter
    with open(fname,'r') as document:
        for line in document:
            line = line.strip()

            # If line contains \usepackage or \newcommand
            # write to packages.tex file
            if line.startswith(pkgContexts):
                if not ("geometry" in line):
                    pkgs.write(line+'\n')

            if line.startswith("%") and ("TEX" in line) and (("png" in line) or ("PNG" in line)):
                print("EQ DETECTED: ",line)
                # First check for a label argument"
                lineTmp = ''.join(line.split())
                if "label=" in lineTmp:
                    lblStart = lineTmp.find('label=')+6
                    eqDict[eqCounter] = lineTmp[lblStart:]

                # Write \begin to \end to dest file.
                line = next(document)
                assert(line.startswith('\\begin{'))
                envType = line[1+line.find('{'):line.find('}')]
                assert(envType in eqContexts)
                if not envType.endswith("*"):
                    line = line.replace(envType,envType+"*")

                if ("\\label{" in line):
                    lblStart = line.find('\\label{')+1
                    lblStop = line.find('}', lblStart)
                    eqDict[eqCounter] = line[7+line.find('\\label{'):line.find('}',line.find('\\label{'))]
                    line = line[:lblStart]+line[lblStop:]

                dest.write(line)
                eqCounter += 1
                line = next(document)

                while not (envType in line):
                    dest.write(line)
                    line = next(document)
                    if ("\\label{" in line):
                        eqDict[eqCounter] = line[7+line.find('\\label{'):line.find('}',line.find('\\label{'))]

                if not envType.endswith("*"):
                    line = line.replace(envType,envType+"*")
                dest.write(line)

            if line.startswith("\\input") or line.startswith("\\include{"):
                print("CALLING SUBPROCESS FOR: ",line)
                # Recursive call;
                subFname = line[1+line.find('{'):line.find('}')]+".tex"
                scanFile(subFname,dest,pkgs)

dest = open(texFileDir+"eq_extracted.tex",'w+')
pkgs = open(texFileDir+"eqPkg.sty",'w+')
scanFile(sys.argv[1],dest,pkgs)
dest.close()
pkgs.close()

subprocess.call(["latexmk","-xelatex","-f","-silent","equations"],cwd=texFileDir)
subprocess.call(["convert","-density","600",texFileDir+"equations.pdf","-quality","95","-trim","+repage",outputDir+"equation%0"+str(eqDigits)+"d.png"])
for key in eqDict:
    subprocess.call(["mv",outputDir+"equation"+str(key).rjust(eqDigits,'0')+".png",outputDir+eqDict[key].replace(":","_")+".png"])
