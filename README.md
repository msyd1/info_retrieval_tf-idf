# Information retrieval project
### Description:
This script:
- goes through the corpus of provided web pages; 
- tokenizes text;
- implements self-made PorterStemmer;
- counts term frequency, document frequency and term frequency–inverse document frequency (tf–idf) that reflect how important a word is for a document in the corpus. 
- creates a SQL database file with a dictionary with unique tokens


<img src="https://github.com/msyd1/info_retrieval_tf-idf/blob/main/img/term_dictionary_table.png" width=40% height=40%>
<img src="https://github.com/msyd1/info_retrieval_tf-idf/blob/main/img/tfidf_table.png" width=40% height=40%>

### Installations
To clone this repository:
```
$ git clone https://github.com/msyd1/info_retrieval_tf-idf.git
```
Or install requred libraries:
- sqlite3

### Structure
```
- data
|- corpus with 570 html data    # data to process
- database.db                   # sql database file
- script.py                     # python script
- README.md
```

### References:
Manning, C.D., Raghaven, P., & Schütze, H. (2009). An Introduction to Information Retrieval (Online ed.). Cambridge, MA: Cambridge University Press. Retrieved from http://nlp.stanford.edu/IR-book/information-retrieval-book.html
