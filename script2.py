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

#Esearch using Edirect
esearch_command="esearch -db protein -query '{0}[organism] AND {1}[Protein name] NOT PARTIAL' | efetch -db protein -format fasta > {0}_esearch.fa ".format(details["taxon"], details["protein_family"])
os.system(esearch_command)
subprocess.call(esearch_command, shell=True)

#Clustalo
subprocess.call("clustalo -i {}_esearch.fa -o {}_clustalo.fa -v".format(details["taxon"]), shell=True)

#Alignment of sequences obtained from edirect search
#subprocess.call("aligncopy -sprotein1 -sequences *_esearch.fa -outfile {}_alignment.fa".format(taxon), shell=True)

#Determine and plot level of protein sequence conservation across the species within that taxonomic group
subprocess.call("plotcon -sprotein1 -sequences {}_clustalo.fa -winsize 10  -graph png > {}_plot.png".format(details["taxon"]), shell=True)
