#!/usr/bin/python3
taxon = input("What is your taxon of interest\n\t> ")
protein_family=input("What is the protein family\n\t> ")
mycommand="esearch -db protein -query '{}[organism] AND {}[Protein name] NOT PARTIAL'  ".format(taxon, protein_family)
os.system(mycommand)
subprocess.call(mycommand, shell=True)
