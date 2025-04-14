## HTML CLONE Identification 

The following solution sholud detect if some sites are a html clone of other sites, from 
the perspective of a person who enters them.
The data for which this solution was made can be found 
https://drive.google.com/file/d/1qONXCVqqEGRHZLQdTkN5hyweBOwIQl_T/view
it is a engineering challenge that can be found on the next page:
https://veridion.com/engineering-challenges/


### How to define if something is a "clone" of another site

These clones can be classified from the code in:

1. direct clones (text, html, css, javascript match almost or even completley) - can be identified easly based on text and code

2. slightly changed clones (small change in text, css or javascript) - can be identified easly with the same method as 1

3. hidden clones (the javascript , html and css differ, but the image looks alike from the point view of a human; the functionality is basically the same; the text may not be the same) 

### How to check if something is a "clone" or not

A way to find out which sites are clones or not is to use different metrics (eventually orthogonal) to find out if something is a clone or not:

1. how similar the information is ( text matching)

2. how similar the page layout is (must work on both statically and dynamically generated pages)

3. how similar the color scheme and text layout is

4. how similar the functionality is (both html buttons and javascript ones).

A pair of clones don't need to have high scores in every metric to be considered clones. So the code may be updated varying on the definition of what a clone is or it is not, finetuning the coeficients.
In real life examples, we could talk about sites like altex.ro and mediagalaxy.ro that can be considerd or not a clone.


#### Implementation

For each tier we make a vector of groups. Everytime we get through a site we assign it to one of the groups based on the 
metrics we defined. for simplicity we'll only check with the first of each group for similarity.
In theory, the relation of similarity is transitive (if a ~ b and b ~ c then a ~ c) even more so if the implementation is as robust at it should be.

The condition on the metric was choosen based on pure intition and documentation.
- page layout must be big usually ( we consider the tags tree in html)
- text matching >= 60 means it is similar text ((https://docs.python.org/3/library/difflib.html#sequencematcher-objects))
- functionality is calculated from every action tag and script and is calculated by comparing the freuqencies of the buttons or actions I considered
- css - I've only checked the inline CSS and the style marked by \<style\>

Notes: For text matching because of ['coade.icu.html', 'imzcr.me.html'] in tier3 that should be with ['susuetawalinkuid.site.html', 'tulangsendietawalin.site.html', 'etawalinherbalmilk.site.html'] I tried adding a translation for every pair where the translation is too small.




### Ideas that may or may not improve the accuracy
- the conditions for the metrics have been chosen by intuition after looking through the tiers by hand.
For a better accuracy, we can make a data set checked partialy by hand and make a matrix for: which files
are similar with which one. After that we compute a matrix of similarity between all files. and by cross-refferencing
we train a model for the condition on the metrics.

- for each of the groups we make, we choose a representative which is the page most similar with the all of them by average, not the first by default
( increases the complexity and would need optimizations like: reducing the number of function calls for pages that are 100 similar or close to, it may be similar with the matrix variation)



### known problems
- tier 3: ['coade.icu.html', 'imzcr.me.html'] does not match with ['susuetawalinkuid.site.html', 'tulangsendietawalin.site.html', 'etawalinherbalmilk.site.html']

- tier 2: for some reason healthfly.in.html always matches with tiptopteak.com.html

### Techonologies I choose not to use and other decisions

- I tried to look for the fastest complexity I could do. So I tried to do this in 
O(n * g) where n is the number of entries in the data set and g is the number of groups. Another solution that could be more accurate but would take much longer would be to compute all 
similarities between any 2 sites and store them in a matrix, and after that
for each line/column we could figure out how to group them. The complexity would have been O(n^2) and I haven't thought enough to find an algorithm good enough to reslove the known problems. (anyway the rang of the matrix would be the number of groups and the proportional lines/columns will be items that are in the same group)

- For the page layout and color scheme, using Playwright to build the image of the web page and then compare 2 sites would have been more easier and accurate, but the cost would have been too big for any data set bigger than 1000.

- I tryed to look into the css stylesheets but a lot of them would not load and there would be errors + the time waiting from the requests from the everysite. I tried even to cache them, but it would be too slow if the application would scale bigger, so I choose to ignore them.

### After thought
Now I think the solution with a matrix where every .html is compared with the other is better, because in my solution we will anyway reach that point in the worst case scenario. So I will try to implement that too