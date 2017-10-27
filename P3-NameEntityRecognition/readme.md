# Viterbi and Forward Algorithm

### Python Version used:
************************

* Python 3.6.0


### How to run
#### Using all parameters

This will create files with the extension .ALL
```
python3.6 ner train.txt test.txt locs.txt WORD POSCON POS WORDCON ABBR CAP LOCATION
```
The output files will be stored into the 'OutputFiles' directory

i.e.

OutputFiles/train.txt.readable.ALL

OutputFiles/test.txt.readable.ALL

OutputFiles/train.txt.vector.ALL

OutputFiles/test.txt.vector.ALL


#### Using all one parameter at a time

This willl create files with the extension .WORD and will be the same for all the other
parameters if they are provided individually
```
python3.6 ner train.txt test.txt locs.txt WORD 
```
i.e.

OutputFiles/train.txt.readable.WORD

OutputFiles/test.txt.readable.WORD

OutputFiles/train.txt.vector.WORD

OutputFiles/test.txt.vector.WORD




<b>Note:</b>Tested on lab1-23