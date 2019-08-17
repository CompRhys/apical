from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import random
import re
import pandas as pd
import numpy as np
import os
import sys


def init():
    # Set PRNG Seed
    random.seed()


def login(url, details):
    # create a new Firefox session
    browser = webdriver.Firefox()
    # browser.manage().deleteAllCookies()
    browser.implicitly_wait(30)
    browser.get(url)

    browser.find_element_by_id("IDToken1").send_keys(details["username"])
    browser.find_element_by_id("IDToken2").send_keys(details["password"])
    browser.find_element_by_name("IDButton").click()

    return browser


def get_data(html_page):
    # Beautiful Soup grabs the HTML table on the page
    try:
        table = html_page.find_all('table')[1]
    except ValueError:
        sleep(0.3)

    # Return HTML table as a pandas dataframe object
    return pd.read_html(str(table), header=0)


def get_target(path):
    df = pd.read_csv(path + '/supercon.csv')
    return np.unique(df['refno :'].values)

def main():
    # Get current working directory
    path = os.getcwd()

    if os.path.exists(path + '/ref_restart.dat'):
        print("loading restart file")
        with open(path + '/ref_restart.dat') as f:
            data_entries  = f.read().splitlines()
        data_entries = np.array(data_entries)
    else:
        data_entries = get_target(path)
        # random.shuffle(data_entries)

    # Launch Browser
    user = sys.argv[1]
    passwd = sys.argv[2]
    login_details = {"username": user, "password": passwd}
    login_url = "https://login-matnavi.nims.go.jp/sso/UI/Login?goto=http%3A%2F%2Fsupercon.nims.go.jp%3A80%2Fsupercon%2Fmaterial%3Fnum%3D1"
    driver = login(login_url, login_details)

    url_stem = "https://supercon.nims.go.jp/supercon/reference?refno="

    datalist = []  # empty list

    count = 0

    for i in data_entries:

        driver.get(url_stem + str(i))
        # sleep(random.random()+0.5)

        # Selenium hands of the source of the specific job page to Beautiful
        # Soup
        soup_html = BeautifulSoup(driver.page_source, "html5lib")
        try:
            title = soup_html.find_all('title')[0]
        except IndexError:
            driver.get(url_stem + str(i))
            sleep(random.random() * 3 + 1)
        finally:
            title = soup_html.find_all('title')[0]

        if str(title) == "<title>Reference</title>":
            count += 1
            try:
                table = soup_html.find_all('table')[1]
            except ValueError:
                driver.get(url_stem + str(i))
                sleep(random.random() * 3 + 0.5)
            finally:
                table = soup_html.find_all('table')[1]

            df = pd.read_html(str(table))

            # Store the dataframe in a list
            if not df[0].empty:
                datalist.append(df[0])
        else:
            print("failed after " + str(count) + " attempts")
            np.savetxt(path + "/ref_restart.dat", data_entries[count:], fmt="%s")
            break

    driver.quit()

    # end the Selenium browser session

    print('Processing results')
    
    result = pd.concat([x.set_index(x.columns[0]).T for x in datalist],
                       axis=0, ignore_index=True, sort=True)

    # Save sampled entries as a csv file
    if os.path.exists(path + '/reference.csv'):
        running_result = pd.read_csv(path + '/reference.csv', index_col=0)
        result = pd.concat(
            [running_result, result], ignore_index=True, sort=True)

    csv_records = result.to_csv(index=True)

    # open, write, and close the file
    f = open(str(path) + "/reference.csv", "w")  # FHSU
    f.write(csv_records)
    f.close()

    if count == len(data_entries):
        os.remove(path + "/ref_restart.dat")


if __name__ == "__main__":
    init()
    main()
