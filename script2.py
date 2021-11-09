#!/usr/bin/python3
import os, subprocess
taxon = input("What is your taxon of interest\n\t> ")
protein_family=input("What is the protein family\n\t> ")
esearch_command="esearch -db protein -query '{}[organism] AND {}[Protein name] NOT PARTIAL' | efetch -db protein -format fasta > {}_esearch.fa ".format(taxon, protein_family, taxon)
os.system(esearch_command)
subprocess.call(esearch_command, shell=True)

align_command="aligncopy -sprotein1 -sequences *_esearch.fa -outfile {}_alignment.fa".format(taxon)
os.system(align_command)
subprocess.call(align_command, shell=True)