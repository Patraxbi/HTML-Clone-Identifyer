## HTML CLONE Identification 

### Abstract
The following solution sholud detect if some sites are a html clone of other sites, from 
the perspective of a person who enters them.
The data for which this solution was made can be found 
https://drive.google.com/file/d/1qONXCVqqEGRHZLQdTkN5hyweBOwIQl_T/view
it is a engineering challenge that can be found on the next page:
https://veridion.com/engineering-challenges/

### Dependinces
from bs4: BeautifulSoup, Tag <br>
from difflib: SequenceMatcher <br>
requests <br>
cssutils <br>
logging <br>

### How to define if something is a "clone" of another site

These clones can be classified from the code in:

1. direct clones (text, html, css, javascript match almost or even completley) - can be identified easly based on text and code

2. slightly changed clones (small change in text, css or javascript) - can be identified easly with the same method as 1

3. hidden clones (the javascript , html and css differ, but the image looks alike from the point view of a human; the functionality is basically the same; the text may not be the same) 

### How to check if something is a "clone" or not

A way to find out which sites are clones or not is to use different metrics (eventually orthogonal) to find out if something is a clone or not:

1. how similar the information is.
implementation: parsing the text and using SequenceMatcher. this information may not be necesarily used in finding clones (In the last solution, I don't even use it anymore) - utils/text.py

2. how similar the page layout is.
implementation: I save the html tags in a tree structure of parent and child. And after that using SequenceMatcher on a string of the tree, we can detect if 2 pages have the same layout or not by how they stand in the hierarchy - utils/layout.py

3. how similar the color scheme and text layout is
implementation: CSS analyzer. the heavylifter and biggest decision maker. I'll detail it more in the next section - utils/style.py

4. how similar the functionality is.
implementation: if in page layout we checked the tags, now we check any type of input tag and some scripts as a whole, it doesn't matter where it is in the page. - utils/functionality.py

A pair of clones don't need to have high scores in every metric to be considered clones. So the code may be updated varying on the definition of what a clone is or it is not, finetuning the coeficients.

In real life examples, we could talk about sites like altex.ro and mediagalaxy.ro that can be considerd or not a clone, or different sites of wikipedia in different languages.


### Implementation

For each tier we make a vector of groups. Everytime we get through a html file we assign it to one of the groups based on the metrics we defined. 
For simplicity we'll only check with the first of each group for similarity.
In theory, the relation of similarity is transitive (if a ~ b and b ~ c then a ~ c) even more so if the implementation is as robust at it should be.

The condition on the metric was choosen based on pure intition and documentation.

- page layout is a bit strict being defined relative to the other terms. So I chose to make a lower coeficient

- text matching >= 60 means it is similar text ((https://docs.python.org/3/library/difflib.html#sequencematcher-objects)). Initially I choose a 10% coefficient for text matching, but because of different languages, I tried to do it without and it works better

Note: For text matching because I tried to see if ['coade.icu.html', 'imzcr.me.html'] in tier3 could be with ['susuetawalinkuid.site.html', ...] I tried adding a translation for every pair where the text matching was too small. In the end I deprecated this and comented it in the code. it may be usefull on a larger scale, but not on this dataset


- functionality is calculated from every action tag and script and is calculated by comparing the freuqencies of the buttons or actions I considered

- css - because css has older and newer standards and can be used inline, with the \<style\> tag or using stylesheets (extern files locally or on the internet), I have developed a lightweight way to do this. 


#### style.py - lightweight HTML Style Analyzer

The file is used for assesying the visual style similarity between two HTML files.
1. It parses the two HTML files using Beautiful Soup

2. Extracts in 3 different arrays:
    - the Inline Styles ( style attribuite in the tags)
    - Embedded styles ( \<style\> tags)
    - External stylesheets ( \<link rel = "stylesheet"\> )

3. I limited the external stylesheets that will be processed to be smaller than 50kB, all the other will be ignored. It would be better to just render the images at that point

4. We compare individualy in the 3 vectors the meaningful visual CSS properties. they are dynamically extracted. <br>
( Initially I went with a static list of the most impactful styles that a read would see: text allignment, shadows, background color, font family, font size, etc. the simplest and easiest to see. But I soon cornered myself because the stylesheets would use new CSS standards) 

5. I computed a similarity score based on these 3 style sources, but if one of them would not be found, its weight is to be distribuited evenly to the others. 

### Ideas that may or may not improve the accuracy
- the conditions for the metrics have been chosen by intuition after looking through the tiers by hand.
For a better accuracy, we can make a data set checked partialy by hand and make a matrix for: which files are similar with which one. After that we compute a matrix of similarity between all files. and by cross-refferencing we train a model for the condition on the metrics.
or the data set can be random and instead of cross-refferencing, we determine which columns of the matrix are almost linear dependent

- for each of the groups we make, we choose a representative which is the page most similar with the all of them by average, not the first by default
( increases the complexity and would need optimizations like: reducing the number of function calls for pages that are 100 similar or close to, it may be similar with the matrix variation)


### Techonologies I choose not to use and other decisions

- I tried to look for the fastest complexity I could do. So I tried to do this in 
O(n * g) where n is the number of entries in the data set and g is the number of groups. 
Another solution that could be more accurate but would take much longer would be to compute all similarities between any 2 sites and store them in a matrix. After that
for each line/column we could figure out how to group them. The complexity would have been O(n^2) and I haven't thought enough to find an algorithm good enough to reslove the known problems. (anyway the rang of the matrix would be the number of groups and the proportional lines/columns will be items that are in the same group)

- For the page layout and color scheme, using Playwright/Selenium to build the image of the web page and then compare 2 sites would have been more easier (to write) and accurate, but the cost would have been too big (I think. There is room for profiling where to use that or not. for exemple they would have been usefull in directory "tier4" but we should have figured out when to use them. probably for the html pages that had stylesheets bigger than M kB because there is a bigger cost for parsing big text files than using Selenium and comparing the visual elements)


### After thought
Now I think the solution with a matrix where every .html is compared with the other may better, anyway is a must for finetuning my coeficients. In my solution we will anyway reach that point of O(n^2) in the worst case scenario, so is not necessarily bad

### Next steps
- to test if parallelizing the code is a good option
    ideas: a thread to preprocess all of the .html to get the text, tags and cache them while a one thread (or 2 threads) analyze all of the similarities.
    it would be a form of producer-consumer classic problem.
- fine tuning the coeficients needed for this
- finding optimizations because it is kinda slow <br>
Output from the /usr/bin/time utilitary:
```
 Command being timed: "python3 main.py"
        User time (seconds): 209.86
        System time (seconds): 0.43
        Percent of CPU this job got: 64%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 5:27.52
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 137316
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 2
        Minor (reclaiming a frame) page faults: 74130
        Voluntary context switches: 1387
        Involuntary context switches: 161
        Swaps: 0
        File system inputs: 23472
        File system outputs: 16
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0 
```