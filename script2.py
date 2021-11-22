#!/usr/bin/python3
import os, subprocess, sys

#USER INPUT 

def personal(taxon, protein_family) :
   import string
   return print("\nYou have provided the following details for your search:\n\tTaxon: ",taxon,"\n\tProtein Family: ",protein_family)

details={}
details["taxon"] = input("What is your taxon of interest\n\t> ")
details["protein_family"]=input("What is the protein family\n\t> ")

personal(*list(details.values()))

if input("Do You Wish To Continue? [y/n]") == "y":
	print("continuing")
else:
	sys.exit(0)

#Couting number of sequences to be potentially downloaded
#by first downloading their accession IDs
subprocess.call("esearch -db protein -query '{0}[organism] AND {1}[Protein name] NOT PARTIAL' | efetch -db protein -format acc > {0}_acc.acc ".format(details["taxon"], details["protein_family"]), shell=True)
def Countsequences(file_name, mode='r+'):
	count=0
	with open(file_name) as f:
		for _ in f:
			count += 1
		print('total number of sequences to be downloaded: ', int(count))
Countsequences('{}_acc.acc'.format(details["taxon"]))
if input("Do You Wish To Continue? [y/n]") == "y":
	print("continuing")
else:
	sys.exit(0)

print("Downloading sequences")
#Esearch using Edirect
esearch_command="esearch -db protein -query '{0}[organism] AND {1}[Protein name] NOT PARTIAL' | efetch -db protein -format fasta > {0}_esearch.fa ".format(details["taxon"], details["protein_family"])
os.system(esearch_command)
subprocess.call(esearch_command, shell=True)
#Clustalo
#subprocess.call("clustalo -i {0}_esearch.fa -o {0}_clustalo.fa -v".format(details["taxon"]), shell=True)

#Alignment of sequences obtained from edirect search
#subprocess.call("aligncopy -sprotein1 -sequences *_esearch.fa -outfile {}_alignment.fa".format(taxon), shell=True)

#Determine and plot level of protein sequence conservation across the species within that taxonomic group
#Allow user to decide whether to save their plot as an output



if input("Do You Wish To Download Your Conservation Plot? [y/n]") == "y":
	subprocess.call("plotcon -sprotein1 -sequences {0}.fa -winsize 10 -graph svg -goutfile {0}_conservation_plot ".format(details["taxon"]), shell=True)
else:
	subprocess.call("plotcon -sprotein1 -sequences {0}.fa -winsize 10 -graph x11 ".format(details["taxon"]), shell=True)


#Scan protein sequences of interest with motifs from PROSITE database
#Download pullseq
os.chdir("./bin/sh")
subprocess.call("git clone https://github.com/bcthomas/pullseq.git # checkout the code using git \
cd pullseq \
./bootstrap \
./configure \
make \
make install ",shell=True)


#subprocess.call("patmatmotifs -sprotein1 -sequence {0}.fa -outfile {0} ".format(details["taxon"]), shell=True)

os.chdir("Assignment2")
subprocess.call("pullseq -i {0}.fa -n {0}_acc.acc *>* output.fasta ".format(details["taxon"]), shell=True)

def Split_fasta(file_name, mode='r+'):
	infile = open({}.fa[1]).format(details["taxon"])
	outfile = []
	for line in infile:
		if line.startswith(">"):
			if (outfile != []): outfile.close()
			genename = line.strip().split('|')[1]
			filename = genename+".fasta"
			outfile = open(filename,'w')
			outfile.write(line)
		else:
			outfile.write(line)
outfile.close()

Countsequences('{}.fa'.format(details["taxon"]))

#make a BLAST database
makeblastdb -in Aves_esearch.fasta -dbtype prot -out Aves
blastx -db Aves -query Aves_esearch.fasta > blastoutput1.out

pullseq

esearch -db protein -query 'Aves'[organism] AND 'Glucose-6-phosphatase'[Protein name] NOT PARTIAL|wc -l
esearch -db protein -query 'Aves'[organism] AND 'Glucose-6-phosphatase'[Protein name]' | esummary