# Webster Dictionary Crawler
Tool to get a list of all words in the Merriam Webster dictionary or special sub-categories e.g. medical dictionary.

## Installation
> Requirements:
> - Python 3.8 or higher

1. Clone the repository and enter the downloaded directory
```shell
git clone https://github.com/kevihiiin/Webster-Dictionary-Crawler.git && Webster-Dictionary-Crawler
```
2. Install the required python packagse
```shell
pip -r requirements.txt
```

## Usage
By default the script grabs all words starting with [A-Za-z0-9].
It the writes the output dictionary to `dictionary/Word_Dictionary.tsv`.

The dictionary to download as well as the output file and delay in between
HTTPS requrests can be configured in the `main.py` file.

To start the tool run:
```shell
python3 main.py
```

## Notes
If you require definitions, examples, etymologies etc please refer to the official 
Merriam-Webster [API](https://dictionaryapi.com/products/index).

Please check the Merriam-Webster T&C on how the data may be used.