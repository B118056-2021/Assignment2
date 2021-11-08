#!/usr/bin/python3
import os, subprocess
os.system('ls')
taxon = input("What is your taxon of interest\n\t> ")
protein_family=input("What is the protein family\n\t> ")
mycommand="esearch -db protein -query '{}[organism] AND {}[Protein name] NOT PARTIAL' | efetch -db protein -format fasta > {}.fa ".format(taxon, protein_family, taxon)


os.system(mycommand)
subprocess.call(mycommand, shell=True)
