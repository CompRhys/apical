from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import random
import re
import pandas as pd
import numpy as np
import os
import pickle
import csv
import sys


def main():

    # Launch Browser
    user = sys.argv[1]
    passwd = sys.argv[2]
    login_details = {"username": user, "password": passwd}
    login_url = "https://login-matnavi.nims.go.jp/sso/UI/Login?goto=http%3A%2F%2Fsupercon.nims.go.jp%3A80%2Fsupercon%2Fmaterial_menu"
    # create a new Firefox session
    driver = webdriver.Firefox()
    login(login_url, login_details, driver)

    # Select from Structure Menu
    # driver.find_element_by_xpath("/html/body/form/table/tbody/tr[5]/td[2]/select").click()
    # driver.find_element_by_xpath("/html/body/form/table/tbody/tr[5]/td[2]/select/option[29]").click()

    # Select from Property Menu
    # driver.find_element_by_xpath("/html/body/form/table/tbody/tr[9]/td[2]/select").click()
    # driver.find_element_by_xpath("/html/body/form/table/tbody/tr[9]/td[2]/select/option[16]").click()

    # Submit the form and wait for human input
    driver.find_element_by_xpath("/html/body/form/table/tbody/tr[15]/td/input[1]").click()
    input("Press Enter to continue...")

    path = os.getcwd()

    if os.path.exists(path + '/restart_url.txt'):
        with open(path + '/restart_url.txt', 'rb') as filehandle:
            # read the data as binary data stream
            restart = pickle.load(filehandle)
        count = int(restart[0])
        restart_url = restart[1]
        driver.get(restart_url)

        input("Press Enter to continue...")

    else:
        count = 1

    datalist = []  # empty list
    complete = False
    while (not complete):
        sleep(0.5)
        # Selenium hands of the source of the specific job page to Beautiful
        # Soup
        loaded = False
        while (not loaded):
            soup_html = BeautifulSoup(driver.page_source, "html5lib")
            try:
                title = soup_html.find_all('title')[0]
                loaded = True
            except IndexError:
                driver.get(driver.current_url)
                sleep(2)

        if str(title) == "<title>OXIDE &amp; METALLIC Search Result</title>":
            try:
                table = soup_html.find_all('table')[3]
            except:
                print("opps something broke")
                break
        else:
            print("opps something broke")
            with open(str(path) + "/restart_count.txt", 'wb') as filehandle:
                # store the data as binary data stream
                pickle.dump([count], filehandle)
            save_data(datalist)
            break

        df = pd.read_html(str(table), header=0)
        # Store the dataframe in a list
        if not df[0].empty:
            datalist.append(df[0])
        print(df[0])

        count += 1

        complete = change_page(driver, count)

    # end the Selenium browser session
    driver.quit()
    save_data(datalist)


def login(url, details, browser):
    browser.implicitly_wait(30)
    browser.get(url)
    browser.find_element_by_id("IDToken1").send_keys(details["username"])
    browser.find_element_by_id("IDToken2").send_keys(details["password"])
    browser.find_element_by_name("IDButton").click()

def find_page(browser, target):
    cuurent = 1
    while current < target:
        current += 1
        change_page(browser, current)

def change_page(browser, count):
    finished = False
    if count > 11:
        if (count % 10) == 0:
            try:
                browser.find_element_by_xpath(
                    "/html/body/a[" + str(11) + "]").click()
            except:
                finished = True
        elif (count % 10) == 1:
            try:
                browser.find_element_by_xpath(
                    "/html/body/a[" + str(12) + "]").click()
            except:
                finished = True
        elif (count % 10) == 9:
            try:
                browser.find_element_by_xpath(
                    "/html/body/a[" + str(10) + "]").click()
            except:
                finished = True
        else:
            try:
                browser.find_element_by_xpath(
                    "/html/body/a[" + str((count + 1) % 10) + "]").click()
            except:
                finished = True
    else:
        browser.find_element_by_xpath(
            "/html/body/a[" + str(count) + "]").click()

    return finished


def save_data(data):
    # Get current working directory
    path = os.getcwd()

    result = pd.concat([x for x in data], axis=0, sort=True)

    if os.path.exists(path + '/lattice.csv'):
        running_result = pd.read_csv(path + '/lattice.csv', index_col=0)
        final_result = pd.concat(
            [running_result, result], ignore_index=True, sort=True)
        csv_records = final_result.to_csv()

        # open, write, and close the file
        f = open(str(path) + "/lattice.csv", "w")  # FHSU
        f.write(csv_records)
        f.close()
    else:
        csv_records = result.to_csv()
        # open, write, and close the file
        f = open(str(path) + "/lattice.csv", "w")  # FHSU
        f.write(csv_records)
        f.close()

if __name__ == "__main__":
    main()
