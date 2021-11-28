#!/usr/bin/python3
import os, subprocess, sys, re, glob

###USER INPUT 
print("\nHello, welcome to B118056's Python 3 script\nPlease make sure you are in the directory you wish to output data before starting the analysis")
print("Program will write outputs to a folder called \'Assignment2\' in the current directory.")

#making a folder called Assignnment2 in the current directory
if not os.path.exists("Assignment2"):
   os.mkdir("Assignment2")

#moving that directory
os.chdir("Assignment2")

#create a function that takes as inputs the taxon and protein family the user is interested in
def Personal(taxon, protein_family) :
   import string
   return print("\nYou have provided the following details for your search:\n\tTaxon: ",taxon,"\n\tProtein Family: ",protein_family, "\n")

details={}
details["taxon"] = input("What is your taxon of interest\n\t> ")
details["protein_family"]=input("What is the protein family\n\t> ")

#run function Personal using the inputs given by the user
Personal(*list(details.values()))

#allows user to check what input they have entered and let's them decide whether they want to continue with their search
def User_continue():
   resp = input ("Do you wish to continue?\nContinue [1]\nRedefine Query [2]\nExit [3]\n")
   if resp == "1":
      print("Continuing analysis..\n")
   elif resp == "2":
      details["taxon"] = input("What is your taxon of interest\n\t> ")
      details["protein_family"]=input("What is the protein family\n\t> ")
      Personal(*list(details.values()))
      User_continue()
   elif resp == "3":
      sys.exit()
   else:
      print ("Sorry, that was not an integer. Please try again!")
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
      print("Proceeding to download sequences! \n")
   elif resp == "n":
      sys.exit(0)
   else:
      print ("Sorry, that was an invalid command. Please try again!")
      Countsequences('{}_acc.acc'.format(details["taxon"]))

Countsequences('{}_acc.acc'.format(details["taxon"]))

#Esearch using Edirect
#Not partial used to download only complete sequences
esearch_command="esearch -db protein -query '{0}[organism] AND {1}[Protein name] NOT PARTIAL' | efetch -db protein -format fasta > {0}_esearch.fa ".format(details["taxon"], details["protein_family"])
os.system(esearch_command)
subprocess.call(esearch_command, shell=True)

print("\n\nSequences for {0} proteins in the {1} taxon are now downloaded!".format(details["protein_family"], details["taxon"]))

#Find the number of unique species downloaded
data = open("{}_esearch.fa".format(details["taxon"])).read()
print("\n\nWithin your dataset,")
nspec = set(re.findall('\[(.*?)\]', data))
print("The total number of unique species represented is:", len(nspec), "\n")

##SEQUENCE ALIGNMENT

#creates a database using the user's inputs
subprocess.call('makeblastdb -in {0}_esearch.fa -dbtype prot -out {0}_reference'.format(details["taxon"]), shell=True)
print("\n\nA reference database was successfully created\n\n")

#Clustalo
#used for sequences alignment of the query
subprocess.call('clustalo -i {0}_esearch.fa -o {0}_clustalo.fa --outfmt=fa -v'.format(details["taxon"]), shell=True)
print("\n\nData was successfully aligned \n\n")

#creating a consensus sequence from the multiple alignment
subprocess.call('cons -sequence {0}_clustalo.fa -outseq {0}_alignment.fa'.format(details["taxon"]), shell=True)
#blasting our sequence alignment file against the consensus sequence
subprocess.call('blastp -db {0}_reference -query {0}_alignment.fa -outfmt "6 sseqid sseq" > {0}_blastoutput.out'.format(details["taxon"]), shell=True)

#Converting the blastoutput into a fasta file
subprocess.call("sed 's/^/>/' {0}_blastoutput.out > temp".format(details["taxon"]), shell = True)
seq_blast = open("temp").read()
seq_blast = seq_blast.replace('\t', '\n')
f_blast= open("{0}_aligned.fa".format(details["taxon"]), "w")
f_blast.write(seq_blast)
f_blast.close()

###CONSERVATION ANALYSIS

#Function to determine and plot level of protein sequence conservation across the species within that taxonomic group
#Allows user to decide whether to save their plot as an output
#Allows user to decide the window size they want to use

def Download_plot():
   print("\n\nPerforming A Conservation Analysis Of The Aligned Sequences.")
   resp = input("Do You Wish To: \nDownload And Visualise Your Conservation Plot [1] \nOnly Visualise Your Plot [2] \nOnly Download Your Plot [3]\n")
   if resp == "1":
      print("\nPlease enter a size of windows for your plot. Default value is 4!")
      print("Larger windows will result in smoother plots at loss of sensitivity\n")
      subprocess.call("plotcon -sprotein1 -sequences {0}_aligned.fa -graph svg -goutfile {0}_conservation_plot ".format(details["taxon"]), shell=True)
      subprocess.call("plotcon -sprotein1 -sequences {0}_aligned.fa -graph x11 ".format(details["taxon"]), shell=True)
   elif resp == "2":
      print("\nPlease enter a size of windows for your plot. Default value is 4!")
      print("Larger windows will result in smoother plots at loss of sensitivity\n")
      subprocess.call("plotcon -sprotein1 -sequences {0}_aligned.fa -graph x11 ".format(details["taxon"]), shell=True)
   elif resp == "3":
      print("\nPlease enter a size of windows for your plot. Default value is 4!")
      print("Larger windows will result in smoother plots at loss of sensitivity\n")
      subprocess.call("plotcon -sprotein1 -sequences {0}_aligned.fa -graph svg -goutfile {0}_conservation_plot ".format(details["taxon"]), shell=True)
   else:
      print ("Sorry, you did not enter an integer. Please try again!")
      Download_plot()

Download_plot()

###PROSITE

print("\n\nNow let's scan your sequences with motifs from the PROSITE database!")
if not os.path.exists("individual_sequences"):
   os.mkdir("individual_sequences")

#patmatmotifs only works on individual sequences
#need to split query fasta files (containing multiple sequences)
#function used to create a list of individual files for each sequence in the query fasta file
fasta_file = open("{0}_esearch.fa".format(details["taxon"]), "r")
content = fasta_file.read()
#every accession IDs is separated by a > at the start of the line
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

#function to get all the names and location of the files that need to be sent to patmatmotifs
def Getlistoffiles(dirName):
    # create a list of file and sub directories names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + Getlistoffiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

filelist = Getlistoffiles("individual_sequences/")

if not os.path.exists("PROSITE_analysis"):
   os.mkdir("PROSITE_analysis")

#do PROSITE analysis for each individual file/ sequence
count=0
for file in filelist:
   count +=1 
   subprocess.call("patmatmotifs -sprotein1 -sequence {0} -outfile PROSITE_analysis/{1}.txt -auto Y ".format(file, count), shell=True)

#Creating summary file from PROSITE analysis
os.chdir("PROSITE_analysis/")
read_files = glob.glob("*.txt")

with open("all_prosite.txt", "wb") as outfile:
    for f in read_files:
        with open(f, "rb") as infile:
            outfile.write(infile.read())

#now lets look for elements in the summary file
# want to find sequences that have motifs
all = open("all_prosite.txt").read()
print("\n\nIn this dataset:")
nmotifs = re.findall(r'Motif = .+', all)
lenmotifs=len(nmotifs)
print("A motif has been identified: ", lenmotifs, "times")
#list of all different types of motifs found
dmotifs=set(nmotifs)
print("The different motifs present in the sequences are:", dmotifs)
#list of the number of times each motif has been found over all the sequences 
for i in dmotifs:
   n=nmotifs.count(i)
   print("\nThere are", n, "occurences of", i, "in all sequences")

##WILDCARD
os.chdir("..")
print("\n\nThis is the final (and optional) stage of our analysis!")
#allow user to decide whether to carry out this optional analysis - distmat from EMBOSS
def Wild_card():
   resp = input("\nDo You Wish To Calculate The Evolutionary Distance Between Every Pair Of Sequences For Your Dataset?\n [y/n]")
   if resp == "y":
      subprocess.call("distmat -sequence {0}_aligned.fa -protmethod 1 -outfile {0}.distmat".format(details["taxon"]), shell=True)
      print("Distance matrix saved as distmat.")
   elif resp == "n":
      print ("Skipping step...")
   else:
      print ("Sorry, that was an invalid command. Please try again!")
      Wild_card()

Wild_card()

#creating a summary file from the PROSITE analsyis
#code doesn't work if it is put earlier on...
sys.stdout = open("prosite_summary.txt", "w")
print("From the input dataset:")
print("A motif has been identified: ", lenmotifs, "times")
print("The different motifs present in the sequences are:", dmotifs)
print("There are", n, "occurences of", i, "in all sequences")
sys.stdout.close()

print("\nAnalysis terminated. Enjoy your day!\n\n")