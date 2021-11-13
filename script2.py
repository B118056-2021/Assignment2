#!/usr/bin/python3
import os, subprocess

Glucose-6-phosphatase

#USER INPUT 
taxon = input("What is your taxon of interest\n\t> ")
protein_family=input("What is the protein family\n\t> ")

#Esearch using Edirect
esearch_command="esearch -db protein -query '{}[organism] AND {}[Protein name] NOT PARTIAL' | efetch -db protein -format fasta > {}_esearch.fa ".format(taxon, protein_family, taxon)
os.system(esearch_command)
subprocess.call(esearch_command, shell=True)

#Clustalo
subprocess.call("clustalo -i {}_esearch.fa -o {}_clustalo.fa -v".format(taxon), shell=True)

#Alignment of sequences obtained from edirect search
#subprocess.call("aligncopy -sprotein1 -sequences *_esearch.fa -outfile {}_alignment.fa".format(taxon), shell=True)

#Determine and plot level of protein sequence conservation across the species within that taxonomic group
subprocess.call("plotcon -sprotein1 -sequences {}_clustalo.fa -winsize 10  -graph x11".format(taxon), shell=True)
