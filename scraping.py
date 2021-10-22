#!/usr/bin/env python
# coding: utf-8

# Import Splinter and BeautifulSoup
from splinter import Browser, browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():

    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_scrape(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

### News Title and Paragraph

# add an argument to the function, using the browser variable we defined outside the function
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #set up the HTML parser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:

        slide_elem = news_soup.select_one('div.list_text')

        # assign the title and summary text to variables
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        ## Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# ## JPL Space Images Featured Image

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    #indexing chained at the end,we want our browser to click the second button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# ## Mars Facts

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    df.columns=['description', 'Mars', 'Earth']
    #inplace=True means that the updated index will remain in place, 
    #without having to reassign the DataFrame to a new variable
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

# Hemisphere Data

def hemisphere_scrape(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    #browser.is_element_present_by_css('div.wrapper', wait_time=1)
    html = browser.html
    Mars_soup = soup(html, 'html.parser')

    hemisphere_image_urls = []
    #results = Mars_soup.find_all('div',class_='item')
    n = 0
    for n in range(4):
        hemispheres = {}

        #Parse from base browser
        html = browser.html
        Mars_soup = soup(html, 'html.parser')

        #Click into new browser and parse again
        browser.find_by_tag('h3')[n].click()

        html = browser.html
        Mars_soup = soup(html, 'html.parser')

        #title
        title = Mars_soup.find('h2', class_='title').text

        #image url
        img = Mars_soup.find('div', class_='downloads')
        img = img.a['href']
        img_url = f'https://marshemispheres.com/{img}'

        # add to dictionary
        hemispheres = {
                    "img_url": img_url,
                    "title": title}

        #Append list of urls with new dictionary information
        hemisphere_image_urls.append(hemispheres)
    
        browser.back()

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())



