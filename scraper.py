# Medium.com Web Scrapper
# @author: Edward Callihan
# Last Modification: 7/7/2020

# Description:
# This program retrieves the article link, title, word count, clap count and text from articles on
# medium.com. The script operates from the command line with argument options for the url, minimum words,
# minimum claps, number of articles to check, and output file name. The title of the article, the link to
# it, the word count, the clap count and article text are saved for each one that meets the qualifications.
# All articles saved to the file are unique.

import requests
from bs4 import BeautifulSoup
import re
import argparse

# command line options:

parser = argparse.ArgumentParser()
parser.add_argument("-u",
                    "--url",
                    help="This argument allows the user to select their"
                         " article for a starting point from medium.com.",
                    default="https://medium.com/codersclan-blog/foolproof-front-end" 
                            "-guidelines-for-novice-and-pro-developers-1f32f0e5b7c5")
parser.add_argument("-mW",
                    "--minWords",
                    help="This allows the user to select the minimum number of words"
                         " for the articles to be saved.",
                    default="0")
parser.add_argument("-mC",
                    "--minClaps",
                    help="This is the minimum number of claps for an article to be rated "
                         "to save to the file.",
                    default="0")
parser.add_argument("-o",
                    "--outputFile",
                    help="This allows the user to select the output file location.",
                    default="output.txt")
parser.add_argument("-p",
                    "--pageCheck",
                    help="This allows the user to select the number of links to check "
                         "for qualified articles to store in the output file.",
                    default="50")
parser.add_argument("-r",
                    "--readFile",
                    help="This option prints the content of the output file to the "
                         "terminal",
                    action="store_true",
                    default=False)
args = parser.parse_args()
URL = args.url
MIN_WORDS = int(args.minWords)
MIN_CLAPS = int(args.minClaps)
data_file = args.outputFile
MAX_LINKS = int(args.pageCheck)
READ_FILE = args.readFile
# instance variables:
claps_regex = r".*claps$"
link_num = 0
scraped = ["NO TITLE"]
links = []


# function definitions:

# clap_count parses the clap count from an article link.
def clap_count(button_list):
    for button in button_list:
        b_text = button.text.strip()
        if re.match(claps_regex, b_text):
            b_text_list = b_text.split()
            num_claps = b_text_list[0]
            # print("value of num claps: " + num_claps)
            if "M" in num_claps:
                print("contains M")
                num_claps = int(float(num_claps.replace("M", "")) * 1000000)
            elif "K" in num_claps:
                print("contains K")
                num_claps = int(float(num_claps.replace("K", "")) * 1000)
            elif isinstance(num_claps, str):
                print("value is a string")
                num_claps = int(num_claps)
            else:
                print("value should be 0")
                num_claps = 0
            print("num_claps type: " + str(type(num_claps)))
            print("num_claps value: " + str(num_claps))
            return num_claps


# word_count returns the number of words in the article text.
def word_count(tag_list):
    my_list = []
    for tags in tag_list:
        word_list = tags.text.strip().split()
        for word in word_list:
            my_list.append(word)
    return len(my_list)


# article_text returns the article text from the list of tags containing the article text.
def article_text(tagged_text):
    text = [tag.text.strip() for tag in tagged_text]
    return "\n".join(text)


# This clears the file before storing the articles.
file = open(data_file, "w", encoding="utf-8")
file.close()
# MAX_LINKS = Number of links to check
while link_num < MAX_LINKS:
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    # This catches the occasional error from an article not having a title.
    try:
        article_title = soup.title.string
    except TypeError:
        article_title = "NO TITLE"
    # used to track articles being checked
    print(article_title)
    # preventing duplicate articles
    if article_title not in scraped:
        scraped.append(article_title)
        buttons = soup.find_all("button")
        total_claps = clap_count(buttons)
        # preventing error from zero clap articles
        if str(type(total_claps)) == "<class 'NoneType'>":
            total_claps = 0
        print("before checking type is " + str(type(total_claps)))
        # ensuring minimum clap count for articles
        if total_claps >= MIN_CLAPS:
            print("claps are good")
            article = soup.find("article")
            # These are all the tags inside the article section that contain
            # the article text.
            article_text_with_tags = article.find_all(["p", "h1", "h2", "h3", "h4"])
            total_words = word_count(article_text_with_tags)
            # ensuring minimum clap count for articles
            if total_words >= MIN_WORDS:
                print("words are good")
                output = article_title + "\n\n" + URL + "\n\nWord Count: " + str(total_words) \
                    + "\n\nClap Count: " + str(total_claps) + "\n\n" + article_text(
                    article_text_with_tags) + "\n\n\n"
                # appending checked article to the file
                f = open(data_file, "a", encoding="utf-8")
                f.write(output)
                f.close()
        # This is where the the links are scraped from the 'more from medium' section
        page_links = soup.find_all("a", href=True)
        valid_links = [link["href"] for link in page_links if
                       re.match(r"^/.+/.+(-{5,}[0-9]-{5,})$", link["href"])]
        unique_links = [valid_links[i].split("------", 1)[0] for i in range(len(valid_links)) if i % 2 == 0]
        for link in unique_links:
            if link not in links:
                links.append(link)
    # This is where the url is updated for the next iteration.
    URL = "https://medium.com" + links[link_num]
    # This updates the links index for the next iteration.
    link_num += 1
# This displays the content of the output file to the monitor if the readFile
# option is used.
if READ_FILE:
    t = open(data_file, "r", encoding="utf-8")
    print(t.read())
    t.close()
# This displays the links on the final page - used for testing.
# print()
# for link in unique_links:
#     print(link)

