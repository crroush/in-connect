# in-connect
LinkedIn provides a lot of really good information about how you are connected.  They do not provide all the ways a normal user might want to look at their contacts.  I was interested to see what people I had in my network that worked either at the same company, or held similar job titles.  This project is designed to give a way to group our contacts by company or position.

I initially started with this [article](https://towardsdatascience.com/linkedin-network-visualisation-using-plotly-9e1962247859) in ordrer to create a tree map of my data.  Which was super easy to do, but the draw backs quickly limited my view into the data.

* People do not always input the company name in the same format, for instance: ABC Corp, ABC Corporation, ABC Corp.
* There are various punctuations / capitalizations of names. 
* Job positions are also the same way, you have Sr. Systems Engineer, Senior Systems Engineer, Sr. Sys Engineer.  Which are all the same title, yet not the same text.  

This task requires we cluster the different companies / titles with some kind of similarity test, and then use a clustering algorithm (dbscan or similar) to cluster the results using the distance metric.  
# Approach
The goal here was not to find the best algorithm for determining similarity, but try to get something that would work reasonably well, with some potential for contamination.  
* First filter each company to remove punctuation, special symbols and to lowercase each word (token).  
* Using dbscan with the [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) metric cluster the companies.
* Group and plot the results

During the trade offs, I did try using [bigrams](https://en.wikipedia.org/wiki/Bigram) and [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance).  I read up on a few others, but ultimately settled on this approach due to the simplistic nature of it and it working for my use case.  

# Requirements:
* ``` pip install plotly ```
* ``` pip install Faker ```
* ``` pip install pandas ```
* ``` pip install numpy ```
* ``` pip install sklearn ```

# Usage
``` 
python python/cluster_companies.py Connections.csv
```

Generate Fake Connections
```
python python/generate_data.py mycontact.csv --num_contacts=1000 --num_companies=25
```
The result from running cluster_companies.py provides a bubble chart that gives you all of your contacts within a company when you mouse over each bubble.  **Note the bigger bubbles I am seeing an issue with wrapping the hover text that I need to sort out**

![image](https://user-images.githubusercontent.com/9982203/119418163-9b441e80-bcb4-11eb-9432-a8e63e7b6a3f.png)

You can see a "live" version of the plot [here](https://crroush.github.io/in-connect/bubble_chart.html)

Generate a Tree Map
```
python python/gen_treemap.py mycontact.csv --network_name="Fake Network"
```
You can view my ["fake network"](https://crroush.github.io/in-connect/fake_network.html) I generated to get an idea of how you might drill down into your data.
