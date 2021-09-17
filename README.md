# IRE Mini Project - Search Engine for Wikipedia

### Code division:
1) dataHolder.py: Contains code for processing the raw text, splitting/merging inverted index and saving stats.
2) saxXMLParser.py: Contains code for parsing the XML dump. Extracts text and passes it to the functions in dataHolder.py for further processing.
3) index.sh: Running this will produce the inverted index.
4) query.py: Contains code for finding the top 10 documents given a query.
5) search.sh: Running this will display the titles of top 10 documents for each query given in a text file.

Steps to run:
1) First create inverted index using the following command:
```bat
> bash index.sh path_to_xml_dump directory_to_save_inverted_index path_to_save_stats
```
2) Save the queries in a file, with each query on a seperate line. Then run the following command:
```bat
> bash search.sh path_where_inverted_index_is_saved path_to_queries_file
```

Happy Searching! :blush:
