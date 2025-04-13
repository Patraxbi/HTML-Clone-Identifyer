## HTML CLONE Identification 

The following solution can detect if some sites are a html clone of other sites, from 
the perspective of a person who enters them.
The data for which this solution was made can be found 
https://drive.google.com/file/d/1qONXCVqqEGRHZLQdTkN5hyweBOwIQl_T/view
it is a engineering challenge that can be found on the next page:
https://veridion.com/engineering-challenges/


### How to define if something is a "clone" of another site

In the data base we have different type of clones from the perspective of a user:

1.

These clones can be classified from the code in:

1. direct clones (text, html, css, javascript match almost or even completley) - can be identified easly based on text and code

2. slightly changed clones (small change in text, css or javascript) - can be identified easly with the same method as 1

3. hidden clones (the javascript , html and css differ, but the image looks alike from the point view of a human; the functionality is basically the same; the text is not the same) - how to assess - "translation cases" here ??

### How to check if something is a "clone" or not

A way to find out which sites are clones or not is to use different orthogonal metrics to find out if something is a clone or not:

1. how similar the information is

2. how similar the page layout is (must work on both statically and dynamically generated pages)

3. how similar the color scheme is 

4. how similar the functionality is (both html buttons and javascript ones).

A pair of clones don't need to have high scores in every metric to be considered clones. So the code may be updated varying on the definition of what a clone is or it is not.
In real life examples, we could talk about sites like altex.ro and mediagalaxy.ro They should or should not be considered a clone.

#### Implementation

For each tier we make a vector of groups. Everytime we get through a site we assign it to one of the groups based on the 
metrics we defined. for simplicity we'll only check with the first of each group for similarity.
In theory, the relation of similarity is transitive (if a ~ b and b ~ c then a ~ c).

The condition on the metric was choosen based on pure intition and documentation.
- page layout must be big usually
- text matching >= 60 means it is similar text ((https://docs.python.org/3/library/difflib.html#sequencematcher-objects))



### Ideas that may or may not improve the accuracy
- the conditions for the metrics have been chosen by intuition after looking through the tiers by hand.
For a better accuracy, we can make a data set checked partialy by hand and make a matrix for: which files
are similar with which one. After that we compute a matrix of similarity between all files. and by cross-refferencing
we train a model for the condition on the metrics.

- for each of the groups we make, we choose a representative which is the page most similar with the all of them by average 
( increases the complexity and would need optimizations like: reducing the number of function calls for pages that are 100 similar or close to)



### known problems
- translation does texts are not recognized if the text is too different
