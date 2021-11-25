#!/usr/bin/python3
import os, subprocess, sys, re, glob

#USER INPUT 
print("\n Hello, welcome to B118056's Python 3 script\n Please navigate to the directory you wish to output data before starting the analysis")
print("Program will write outputs to the \'Assignment2\' folder in the current directory.")

def Personal(taxon, protein_family) :
   import string
   return print("\nYou have provided the following details for your search:\n\tTaxon: ",taxon,"\n\tProtein Family: ",protein_family, "\n")

details={}
details["taxon"] = input("What is your taxon of interest\n\t> ")
details["protein_family"]=input("What is the protein family\n\t> ")

Personal(*list(details.values()))

def User_continue():
   resp = input ("Do you wish to continue?\nContinue [1]\nRedefine Query [2]\nExit [3]\n")
   if resp == "1":
      print("continuing analysis..\n")
   elif resp == "2":
      details["taxon"] = input("What is your taxon of interest\n\t> ")
      details["protein_family"]=input("What is the protein family\n\t> ")
      Personal(*list(details.values()))
      User_continue()
   elif resp == "3":
      sys.exit()
   else:
      print ("Sorry, that was an invalid command. Please try again!")
      User_continue()

User_continue()

#Couting number of sequences to be potentially downloaded
#by first downloading their accession IDs
subprocess.call("esearch -db protein -query '{0}[organism] AND {1}[Protein name] NOT PARTIAL' | efetch -db protein -format acc > {0}_acc.acc ".format(details["taxon"], details["protein_family"]), shell=True)
def Countsequences(file_name, mode='r+'):
   count=0
   with open(file_name) as f:
      #counting the number of lines in file
      for _ in f:
         count += 1
      print('\n\nTotal number of sequences to be downloaded: ', int(count))
   resp = input("Do You Wish To Continue? [y/n]")
   if resp == "y":
      print("Proceeding to download sequences \n")
   elif resp == "n":
      sys.exit(0)
   else:
      print ("Sorry, that was an invalid command. Please try again!")

Countsequences('{}_acc.acc'.format(details["taxon"]))

#Esearch using Edirect
#Not partial used to download only complete sequences
esearch_command="esearch -db protein -query '{0}[organism] AND {1}[Protein name] NOT PARTIAL' | efetch -db protein -format fasta > {0}_esearch.fa ".format(details["taxon"], details["protein_family"])
os.system(esearch_command)
subprocess.call(esearch_command, shell=True)

print("\n\nSequences for {0} proteins in the {1} taxon are now downloaded!".format(details["protein_family"], details["taxon"]))

data = open("{}_esearch.fa".format(details["taxon"])).read()
print("\n\nWithin your dataset,")
nspec = set(re.findall('\[(.*?)\]', data))
print("The total number of unique species represented is:", len(nspec), "\n")

##SEQUENCE ALIGNMENT

subprocess.call('makeblastdb -in {}_esearch.fa -dbtype prot -out reference'.format(details["taxon"]), shell=True)
print("\n\nA reference database was successfully created\n\n")

#Clustalo
#used for sequence alignment
subprocess.call('clustalo -i {0}_esearch.fa -o {0}_clustalo.fa --outfmt=fa -v'.format(details["taxon"]), shell=True)
print("\n\nData was successfully aligned \n\n")


subprocess.call('cons -sequence {0}_clustalo.fa -outseq {0}_alignment.fa'.format(details["taxon"]), shell=True)
subprocess.call('blastp -db reference -query {0}_alignment.fa -outfmt "6 sseqid sseq" > {0}_blastoutput.out'.format(details["taxon"]), shell=True)

#we format the blast into a "semi-fasta"
subprocess.call("sed 's/^/>/' {0}_blastoutput.out > temp".format(details["taxon"]), shell = True)

#replacing each tab with a newline to get a fasta format
text = open("temp").read()
text = text.replace('\t', '\n')
f = open("{0}_aligned.fa".format(details["taxon"]), "w")
f.write(text)
f.close()
#Determine and plot level of protein sequence conservation across the species within that taxonomic group
#Allow user to decide whether to save their plot as an output  
def Download_plot():

   resp = input("Do You Wish To Download Your Conservation Plot? [y/n]")
   if resp == "y":
      subprocess.call("plotcon -sprotein1 -sequences {0}_aligned.fa -winsize 4 -graph svg -goutfile {0}_conservation_plot.png ".format(details["taxon"]), shell=True)
   elif resp == "n":
      subprocess.call("plotcon -sprotein1 -sequences {0}_aligned.fa -winsize 4 -graph x11 ".format(details["taxon"]), shell=True)
   else:
      print ("Sorry, that was an invalid command. Please try again!")
      Download_plot()

Download_plot()

if not os.path.exists("individual_sequences"):
   os.mkdir("individual_sequences")

fasta_file = open("{0}_esearch.fa".format(details["taxon"]), "r")
content = fasta_file.read()
all_sequences = content.split('>')
fasta_file.close()
for seq in all_sequences[1:]:
   #need to retrieve the accession value to name the new file with the single sequence accordingly
   acc = seq.split()[0]
   #some fasta files contain sequences that start with sp or tr before the accession values
   if acc.startswith('sp') or acc.startswith('tr'):
      acc = acc.split('|')[1]
   new_file = open('individual_sequences/' +acc + '.fa', 'w')
   new_file.write('>' + seq)
   new_file.close()

#PROSITE Analysis
os.listdir(path='.')
def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

filelist = getListOfFiles("individual_sequences/")

if not os.path.exists("PROSITE_analysis"):
   os.mkdir("PROSITE_analysis")

count=0
for file in filelist:
   count +=1 
   subprocess.call("patmatmotifs -sprotein1 -sequence {0} -outfile PROSITE_analysis/{1}.txt -auto Y ".format(file, count), shell=True)

##CREATING SUMMARY FILE
os.chdir("PROSITE_analysis/")
read_files = glob.glob("*.txt")

with open("all_prosite.txt", "wb") as outfile:
    for f in read_files:
        with open(f, "rb") as infile:
            outfile.write(infile.read())

#now lets look for elements in the summary file
all = open("all_prosite.txt").read()

print("In this dataset:")

#sequences with motifs
nmotifs = re.findall(r'Motif = .+', all)
lenmotifs=len(nmotifs)
print("A motif has been identified: ", lenmotifs, "times")

#different motifs by name
dmotifs=set(nmotifs)
print("The different motifs present in the sequences are: ", dmotifs)

#number of sequences for each motif 
for i in dmotifs:
   n=nmotifs.count(i)
   print("There are ", n, "occurences of ", i, "in all sequences")

