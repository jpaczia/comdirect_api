This project allows accessing (comdirect) banking information via the [comdirect Rest API](https://www.comdirect.de/cms/kontakt-zugaenge-api.html).
At the moment the functionality is limited to downloading the documents in the postbox.
In my case most documents are related to ETF's and the files are saved based on the WKN of the ETF's to improve the overview.
Files are further classified and sorted by the reason they were generated, e.g. if an ETF was bought, sold or yielded some dividends.
Documents which are not related to ETF's / stocks are saved in the Misc ("Sonstiges") directory.


## Setup
1. Activate the comdirect Rest API as described on official [comdirect website](https://www.comdirect.de/cms/kontakt-zugaenge-api.html)
2. Save your credentials in the ```credentials_template.json```. The ```client_id``` and ```client_secret``` are generated by comdirect and provided after enabling the comdirect Rest API. If you loose them they can be reset via ***Verwaltung*** > ***Entwicklerzugang*** when logged in.
3. Configure the desired output directory, the list of depot positions (i.e. their WKN's) and the path to the credentials file edited from step 2 in ```config.json```. No defaults are provide so no sensitive/confidential files are saved in random directories.
The most common file classes are already included in ```config.json```. The monthly ***Finanzreport*** is the only file class skipped by the program with the given configuration.
4. Install the required python modules via
	```
	pip install -r requirements.txt
	```
5. Run ```main.py``` via
	```
	python -m main
	```
