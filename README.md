# crawling-lookbook.nu

## Introduction
This is a crawling step for a fashion project by using 'Scrapy'. We need to get 500 users' information in lookbook.nu. We are going to save the information we have in two dictionaries.

## Data Format
* ***general_info*** = {'ID': '', 
                        'url': '', 
                        'personal_info': {'Name': '', 'Country': '', 'n_fans': '', 'n_looks': '', 'n_loves': '', 
                                          'n_hypes': '', 'n_follow': ''}, 
                        'fans_list': [], 
                        'follow_list': []}

* ***photo_info*** = {'photo_url': [], 
                      'title': [], 
                      'likes': [], 
                      'date': [], 
                      'hashtag': [], 
                      'colors': [], 
                      'photoitems': []} 

First dictionary stores the general information for one user, her/his user ID, page url, name, country, number of fans, number of photos she/he posted, number of loves she/he got, number of hypes she/he got (the likes of each photo), number of users she/he follows, a list of fans, and a list of users she/he follows.

Second dictionary stores the information of photos she/he posted, the photo urls, the title of each photo, how many likes did she/he got in this photo, the date posted, the hashtag used, the colors in this outfit, and the items in this outfit.

## How to Run
In order to store the data we crawled in *.json* file.
```
scrapy crawl lookbookuser -o items.json
```
