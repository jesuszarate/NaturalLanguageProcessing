#Ngrams

###Python Version used:
************************

* Python 3.6.0


### How to run

```
python ngrams.py train.txt -test test.txt
```

```
python ngrams.py train.txt -gen seeds.txt
```

* Running with ```-test``` will print the probabilities of the sentence 
inside of the ```test.txt``` file provided and output a file called
 ```ngrams-test.trace```

* Running with ```-gen``` will print the generated sentences from the 
seed file provided ```seeds.txt``` file provided, and will output a  file 
called ```ngrams-gen.trace```


###Example Output -test output
******************

```
S = Wolf

Unsmoothed Unigrams, logprob(S) = -11.4522
Unsmoothed Bigrams, logprob(S) = -12.4375
Smoothed Bigrams, logprob(S) = -12.826

S = In the jungle

Unsmoothed Unigrams, logprob(S) = -22.0357
Unsmoothed Bigrams, logprob(S) = -15.3101
Smoothed Bigrams, logprob(S) = -18.9389

S = Rustle in the grass .

Unsmoothed Unigrams, logprob(S) = -43.1179
Unsmoothed Bigrams, logprob(S) = undefined
Smoothed Bigrams, logprob(S) = -51.7462

S = What could go wrong ?

Unsmoothed Unigrams, logprob(S) = -48.2676
Unsmoothed Bigrams, logprob(S) = -35.3043
Smoothed Bigrams, logprob(S) = -55.0859

S = I swear I am not making this up .

Unsmoothed Unigrams, logprob(S) = -82.8339
Unsmoothed Bigrams, logprob(S) = undefined
Smoothed Bigrams, logprob(S) = -97.0172

S = But old Mr. Toad will leave one day .

Unsmoothed Unigrams, logprob(S) = -78.5045
Unsmoothed Bigrams, logprob(S) = undefined
Smoothed Bigrams, logprob(S) = -82.1001


```


###Example Output -gen output
******************

```
Seed = She

Sentence 1: She was as if ye know what business a great deal
Sentence 2: She had said , ' said .
Sentence 3: She did venture to him .
Sentence 4: She made of things are you were one day she succeeded
Sentence 5: She carries out the castle , put reeds into such a
Sentence 6: She smiled tenderly and so poor peasant , old mr. toad
Sentence 7: She is no time to work as hateful memories away ?
Sentence 8: She can , and his cap looked round me .
Sentence 9: She called three days on that jolly !
Sentence 10: She is , martin summoned all the jury all her caught

Seed = I

Sentence 1: I do you this man held to see the child .
Sentence 2: I wish to be hanged on the golden hair clustering about
Sentence 3: I never fail !
Sentence 4: I looked at walrus islet , mowgli , ` where are
Sentence 5: I should be treated with rushes and set him than anything
Sentence 6: I 'm not remember ever so he heard news from the
Sentence 7: I suppose .
Sentence 8: I did not forget to see if there was a greenvale
Sentence 9: I do n't .
Sentence 10: I 've had no leader of happiness followed them word to

Seed = Old

Sentence 1: Old mr. toad had already he wore grand and belongings ,
Sentence 2: Old man came leaping along by the barley-corn ; over !
Sentence 3: Old home is the soldier and we make him , twice
Sentence 4: Old woman had his long and courtiers .
Sentence 5: Old conger-eel , and canes together .
Sentence 6: Old dutcher , for i wish i buttoned her dress .
Sentence 7: Old mr. toad needed at the queer tongue in a wake
Sentence 8: Old they gave the time by the same injunctions to the
Sentence 9: Old loves !
Sentence 10: Old dutcher was discouraging but you went back too , hitting

```

    
