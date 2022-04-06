#!/bin/env python3
import logging
import re
import requests
import string
import sys
import time

from bs4 import BeautifulSoup
from pathlib import Path

# ---------------------------------
# Configure the parser
# ---------------------------------
# Base URL to scrape
base_url = "https://www.merriam-webster.com/browse/medical/{letter}/{page}"

# Folder/File to write results to
output_folder_path = Path("dictionary")
output_file_path = output_folder_path.joinpath("Word_Dictionary.tsv")

# Min. Delay inbetween requests in seconds
min_delay_s = 1

# ---------------------------------
# Get a list of letters to look for
# ---------------------------------
sub_site_letters = string.ascii_lowercase + "0"


# ---------------------------------
# Go through a subsites (one letter) and retrieve the words
# ---------------------------------
def crawl_letter(letter, base_url):
    word_list = []
    next_page = 1
    last_page = sys.maxsize
    logging.info(f"Fetching dictionary for letter {letter}")
    # -- Iterate through all the pages per letter
    while next_page <= last_page:
        # - Increment page counter
        current_page = next_page
        next_page += 1

        logging.info(f"Crawling page {current_page}")

        # - Assemble the URL
        letter_url = base_url.format(letter=letter, page=current_page)

        # - Fetch the website
        page_request = requests.get(letter_url)
        page_request_status_code = page_request.status_code
        logging.debug(f"Response code: {page_request_status_code}")
        if page_request_status_code != 200:
            logging.warning(f"Could not retrieve the url: {letter_url}\n Status code: {page_request_status_code}")
            continue

        # - Start parsing
        page_soup = BeautifulSoup(page_request.content, "html.parser")
        # Find the number of pages for this letter, if not already set
        if last_page == sys.maxsize:
            counter_list = page_soup.find_all("span", class_="counters")
            try:
                page_count_text = counter_list[0].text
                last_page = int(re.search(r'.* of ([1-9]*)', page_count_text).group(1))
            # TypeError: if counter_list is empty | AttributeError: if there was no match
            except TypeError or AttributeError:
                logging.warning(f"Could not determine the maximum number of pages. Will stop after page 1.")
                last_page = -1

        # Look for entries (containing a list of words)
        entry_list = page_soup.find_all("div", class_="entries")
        if not entry_list:
            logging.warning(f"Could not find any entries (words) for letter {letter} on page {current_page}")
            continue
        # Get all the words from the entries
        for entry in entry_list:
            new_words = [link.text for link in entry.find_all("a")]
            word_list += new_words
            logging.debug(f"Added {len(new_words)} new words")
    time.sleep(min_delay_s)

    return word_list


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    word_list = []

    # Create output folder
    output_folder_path.mkdir(exist_ok=True)

    # Write the output to file
    with open(output_file_path, "w") as output_file:
        # Go through all the letters
        for letter in sub_site_letters:
            letter_word_list = crawl_letter(letter, base_url)
            word_list += letter_word_list
            output_file.writelines("\n".join(letter_word_list))

    # Print the results
    print(word_list)
