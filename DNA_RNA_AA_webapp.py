##################
# Modules 
##################

import streamlit as st
import re as re
import pandas as pd


##################
# Page formatting
##################

st.title('DNA/RNA/Protein Converter, Counter, and GC Content Calculator')


##################
# Declarations
##################

class Sequence:
	__name = ''
	__sequence = ''
	__length = 0

	def __init__(self, name: str, sequence: str):
		self.__name = name
		self.__sequence = sequence.upper()
		self.__length = len(sequence)

	def getName(self): return self.__name
	def getSequence(self): return self.__sequence
	def getLength(self): return self.__length

DNA_NT = ['A', 'T', 'G', 'C']
RNA_NT = ['A', 'U', 'G', 'C']
AA_dict = {
	'A': ('GCU', 'GCC', 'GCA', 'GCG'),
	'C': ('UGU', 'UGC'),
	'D': ('GAU', 'GAC'),
	'E': ('GAA', 'GAG'),
	'F': ('UUU', 'UUC'),
	'G': ('GGU', 'GGC', 'GGA', 'GGG'),
	'H': ('CAU', 'CAC'),
	'I': ('AUU', 'AUC', 'AUA'),
	'K': ('AAA', 'AAG'),
	'L': ('CUU', 'CUC', 'CUA', 'CUG', 'UUA', 'UUG'),
	'M': ('AUG'),
	'N': ('AAU', 'AAC'),
	'P': ('CCU', 'CCC', 'CCA', 'CCG'),
	'Q': ('CAA', 'CAG'),
	'R': ('AGA', 'AGG', 'CGU', 'CGC', 'CGA', 'CGG'),
	'S': ('AGU', 'AGC', 'UCU', 'UCC', 'UCA', 'UCG'),
	'T': ('ACU', 'ACC', 'ACA', 'ACG'),
	'V': ('GUU', 'GUC', 'GUA', 'GUG'),
	'W': ('UGG'),
	'Y': ('UAU', 'UAC'),
	'.': ('UAG', 'UAA', 'UGA')
}


## Codon_Table[col][row]
## A pandas dataframe containing the possible amino acids for row = codon[0] and col = codon[1], given a codon string.
Codon_Table = pd.DataFrame(index = sorted(RNA_NT), columns = sorted(RNA_NT))
Codon_Table['A'] = [('N', 'K'), ('H', 'Q'), ('D', 'E'), ('Y', '.')]
Codon_Table['C'] = ['T', 'P', 'A', 'S']
Codon_Table['G'] = [('S', 'R'), 'R', 'G', ('C', 'W', '.')]
Codon_Table['U'] = [('I', 'M'), 'L', 'V', ('F', 'L')]


def isDNA(s):
	if re.match('^[ATCG]+$', s, re.IGNORECASE):
		return True
	else:
		st.write('Invalid DNA input.')
		return False

def isRNA(s):
	if re.match('^[AUCG]+$', s, re.IGNORECASE):
		return True
	else:
		st.write('Invalid RNA input.')
		return False

def isPeptide(s):
	peptides = ''.join(AA)
	if re.match('^[' + peptides + ']+$', s, re.IGNORECASE):
		return True
	else:
		st.write('Invalid peptide input.')
		return False

CHOICES = {
	'DNA': isDNA,
	'RNA': isRNA,
	'Peptide': isPeptide
}


##################
# Input sequence
##################

option = st.sidebar.radio('Select your input sequence type:', list(CHOICES.keys()))

st.header('How to Use:')
st.markdown('1. Select your sequence type from the sidebar.\n2. Enter your sequence below, then click "SUBMIT".')

sequence_input = st.text_area(
	label = '(If more than one header (i.e. ">") is detected, only the first sequence will be processed.)', 
	value = '', 
	height=200
	)


## Cleans sequence input and creates Sequence object
def cleanSequence(s):
	lines = s.splitlines()
	name = ''
	for index, item in enumerate(lines):
		if re.search('[>]+', item):
			name = item
			lines.pop(index)
			break
	s = ''.join(lines)
	seq_obj = Sequence(name, s)
	return seq_obj

## Verifies sequence input
def validSequence(option, seq_object):
	for key in CHOICES:
		if option == key:
			return CHOICES.get(key)(seq_object.getSequence())
	st.write('Key not found.')
	return False


##################
# Conversions
##################

def DNAtoRNA(s):
	return s.replace('T', 'U')

def RNAtoDNA(s):
	return s.replace('U', 'T')

def RNAtoAA(s):
	peptide = ''
	codon = ''
	for character in s:
		codon += character
		if len(codon) == 3:
			cell = Codon_Table[codon[1]][codon[0]]
			if type(cell) == str:
				aa = cell
			else:
				for element in cell:
					if codon.upper() in AA_dict.get(element):
						aa = element
						break			
			peptide += aa
			codon = ''
	return peptide

################## TODO
#def AAtoRNA(s):
# 	possibilities = []
# 	rna = ''
# 	for letter in s:
# 		codons = AA_dict.get(letter)
# 	return possibilities

##################
# Submit Button
##################

submitted = False
if st.button('SUBMIT'):
	## Create Sequence object
	seq_object = cleanSequence(sequence_input)
	if validSequence(option, seq_object):
		if option == 'DNA':
			dna = seq_object.getSequence()
			rna = DNAtoRNA(seq_object.getSequence())
			peptide = RNAtoAA(rna)
			submitted = True
		elif option == 'RNA':
			dna = RNAtoDNA(seq_object.getSequence())
			rna = seq_object.getSequence()
			peptide = RNAtoAA(seq_object.getSequence())
			submitted = True
		# else:
		# 	st.header('RNA:\n')
		# 	rna = AAtoRNA(seq_object.getSequence())
		# 	st.text(rna)
		# 	st.header('DNA:\n')
		# 	dna = RNAtoAA(rna)
		# 	st.text(dna)
		################## TODO

	else:
		st.write('Check that your sequence matches the input type and try again.')

if submitted:
	st.markdown('## DNA: _' + str(len(dna)) + ' bases_')
	st.text_area(label = '', value = dna, height = 140)
	st.markdown('## RNA: _' + str(len(rna)) + ' bases_')
	st.text_area(label = '', value = rna, height = 140)
	st.markdown('## Peptide: _' + str(len(peptide)) + ' amino acids_')
	st.text_area(label = '', value = peptide, height = 140)
	#st.markdown('## GC Content:')
	################## TODO
 