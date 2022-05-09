# iTunes App Store Scraper
This defines a lightweight Python class that can be used to scrape app 
information from the iTunes App Store. It defines a couple of methods that can
be used to get relevant app IDs given a set of parameters, and a couple of 
methods to then scrape data about these app IDs.

Much of this has been adapted from 
[app-store-scraper](https://github.com/facundoolano/app-store-scraper), a 
nodeJS-based scraper that does similar things. But this scraper uses Python.

## Getting started
The following scrapes app details about all apps similar to the first result 
for the 'fortnite' search query:

```
from itunes_app_scraper.scraper import AppStoreScraper

scraper = AppStoreScraper()
results = scraper.get_app_ids_for_query("fortnite")
similar = scraper.get_similar_app_ids_for_app(results[0])

app_details = scraper.get_multiple_app_details(similar)
print(list(app_details))
```

Documentation is not available separately yet, but the code is relatively
simple and you can look in the `scraper.py` file to see what methods are 
available and what their parameters are.

## Sources of Data:
| Query	        | Source                                                                                                                       | 	URL base                                                          |
|---------------|------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| App           | 	[Affiliates API](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html) | https://itunes.apple.com/lookup?                                   |
| Search	       | Old Affiliates?	                                                                                                             | https://search.itunes.apple.com/WebObjects/MZStore.woa/wa/search?  |
| Developer	    | [Affiliates API](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html)  | https://itunes.apple.com/lookup?                                   |
| List	         | [Old Affiliates](https://images.apple.com/itunesaffiliates/guides/AffiliatesSearch_2.7(JSON).pdf)                            | 	http://ax.itunes.apple.com/WebObjects/MZStoreServices.woa/ws/RSS/ |
| Similar       | iTunes store scrape HTML                                                                                                     | 	https://itunes.apple.com/us/app/app/                              |
| Full Details	 | [Affiliates API](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html)  | https://itunes.apple.com/lookup?                                   |
 | Ratings       | iTunes store scrape HTML                                                                                                     | https://itunes.apple.com/lookup?                                   |                                  |


## License
This scraper was developed by the 
[Digital Methods Initiative](https://digitalmethods.net), and is distributed
under the MIT license. See LICENSE for details.
