# Web-scraping
My web scraping codes (personal use)

Related packages: `requests`, `bs4`, `re`, `pandas`, `selenium`

## Amap
### Scrape art school information using Amap API

Using the Amap API key I applied at https://lbs.amap.com/, I scraped the art school information including school name, address, telephone with granularity of administrative district in China. The city code and administrative district code using in Amap can be found in the file `AMap_adcode_citycode_2020_4_10.xlsx`.

### Translate from Chinese to English

Using `googletrans` package, the information of art school was translated to English.


## Artand

Using `selenium` realized the log in and automatic "load more" process to get HTML of the website.

