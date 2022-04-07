#!/bin/env python3
import logging
import re
import requests
import string
import time

from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm

# ---------------------------------
# Configure the parser
# ---------------------------------
# Base URL to scrape
base_url = "https://www.merriam-webster.com/browse/{dictionary}/{letter}/{page}"

# Folder/File to write results to
output_folder_path = Path("dictionary1")
output_file_path = output_folder_path.joinpath("Word_Dictionary.tsv")

# Min. Delay inbetween requests in seconds
min_delay_s = 1

# ---------------------------------
# Get a list of letters to look for
# ---------------------------------
letter_list = [letter for letter in string.ascii_lowercase + "0"]


def fetch_parse_website(dictionary, letter, page=1):
    """
    Fetch the contents of the website given a dictionary, letter and optionally page.
    Parse the website then using BeautifulSoup
    :param dictionary: dictionary to parse (e.g. 'dictionary' or 'medical')
    :param letter: letter to parse (e.g. 'a', 'b')
    :param page: exact page to get, defaults to 1
    :return: str: Website content as string
    """
    page_url = base_url.format(dictionary=dictionary, letter=letter, page=page)
    logging.debug(f"Fetching URL: {page_url}")
    page_request = requests.get(page_url)
    page_request_status_code = page_request.status_code
    logging.debug(f"Response code: {page_request_status_code}")
    if page_request_status_code != 200:
        logging.warning(f"Could not retrieve the url: {page_url}\n Status code: {page_request_status_code}")
        return

    return BeautifulSoup(page_request.content, "html.parser")


def parse_page_numbers(page_content):
    """
    Determine the number of pages per letter to crawl
    :param page_content: Content of the dictionary site (containing "page 1 of 1" text)
    :return: int: Number of pages for this letter
    """
    # Default value, stop after the first page
    last_page_num = 1

    try:
        # Get the page counter element text (style "page 1 of 10")
        page_count_text = page_content.find("span", class_="counters").text
        # Extract the last number
        last_page_num = int(re.search(r'.* of ([1-9]*)', page_count_text).group(1))
    # TypeError: if counter_list is empty | AttributeError: if there was no match or page_content is None
    except TypeError or AttributeError:
        logging.warning(f"Could not determine the maximum number of pages. Will stop after page 1.")

    return last_page_num


def parse_words(page_content):
    """
    Extract the words from a given site
    :param page_content: Content of the dictionary site (containing all the words for this letter and page)
    :return: [str]: List of words
    """
    word_list = []
    entry_list = page_content.find_all("div", class_="entries")
    if not entry_list:
        logging.warning(f"Could not find any entries (words) for this letter on this page")
        return word_list
    # Get all the words from the entries
    for entry in entry_list:
        new_words = [link.text for link in entry.find_all("a")]
        word_list += new_words

    logging.debug(f"Added {len(word_list)} new words")

    return word_list


# ---------------------------------
# Go through a sub sites (one letter) and retrieve the words
# ---------------------------------
def crawl_by_letter(dictionary, letter_tupel, prog_bar=None, min_delay=1):
    word_list = []
    letter, max_page = letter_tupel
    logging.info(f"Fetching dictionary for letter {letter}")
    # -- Iterate through all the pages per letter
    for page_num in range(1, max_page + 1):
        logging.debug(f"Crawling page {page_num}")
        # Increment the progressbar
        if prog_bar:
            prog_bar.update(1)

        # Fetch and parse the website with bs4
        page_soup = fetch_parse_website(dictionary, letter, page_num)
        if not page_soup:
            logging.warning(f"Empty website, cannot parse entries for letter {letter} on page {page_num}")
        # Look for entries (containing a list of words)
        word_list += parse_words(page_soup)

    time.sleep(min_delay)

    return word_list


def crawl_by_dictionary(dictionary, letter_list, output_file_path, min_delay=1):
    """
    Given a dictionary and letter_list, write the list of words to the specified output file
    :param dictionary: dictionary to parse (e.g. 'dictionary' or 'medical')
    :param letter_list: list of letter to parse (e.g. ['a', 'b'])
    :param output_file_path: file to write the word list to
    :return: word list
    """
    # Our result list
    word_list = []

    # Create output folder
    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine the number of pages per letter to scrape
    letter_dict = {}
    for letter in letter_list:
        page_soup = fetch_parse_website(dictionary, letter)
        letter_dict[letter] = parse_page_numbers(page_soup)

    # Set up the tqdm progress bar and open output file
    with tqdm(total=sum(letter_dict.values())) as prog_bar, open(output_file_path, "w") as output_file:
        # Go through all the letters
        for letter_tupel in letter_dict.items():
            # Get word list by letter, append to result list and write to file
            letter_word_list = crawl_by_letter(dictionary, letter_tupel, prog_bar, min_delay=min_delay)
            word_list += letter_word_list
            output_file.writelines("\n".join(letter_word_list))

    return word_list


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result_list = crawl_by_dictionary("medical", letter_list, output_file_path)
    print(result_list)
