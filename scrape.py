from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import os
import time

def scrape_team(team, wait):
    """
    scrapes multi-year contract data for respective team from spotrac
    """
    time.sleep(wait)
    driver = webdriver.Chrome()
    driver.get(f'https://www.spotrac.com/nba/{team}/yearly/cap/')
    driver.implicitly_wait(10)
    print("successful entrance")

    def year_breakdown(yr):
        """
        yr a list of 2-3 elements containing a player's salary cap data for that year
        returns: salary in dollar amount, percentage of total cap
        """
        if "UFA" in yr or "RFA" in yr or "Two-Way" in yr:
            return np.nan, np.nan
        if "Ext. Eligible" in yr:
            yr.remove("Ext. Eligible")
        if len(yr) == 3:
            return int(yr[0].replace('$', '').replace(',', '')), float(yr[2].replace('%', ''))
        elif len(yr) == 2:
            return int(yr[0].replace('$', '').replace(',', '')), float(yr[1].replace('%', ''))
        else:
            return np.nan, np.nan

    data = []
    try:
        table = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[3]/div[2]/table[1]/tbody')
        rows = table.find_elements(By.XPATH, '//tr[@role="row"]')  # get all table rows
        flag = 0
        for row in rows:
            if "PLAYERS" in row.text:  # break if trying to access other tables than Active Roster
                if flag == 0:
                    flag = 1
                else:
                    break
            try:  # access player name, contract type in first column cells
                player = row.find_elements(By.CLASS_NAME, 'player')
                name, contract, type = [elem.strip() for elem in player[0].text.split('\n')]
            except Exception as e:
                print("Failed at extracting player name and contract type data")
                print(e)
                continue
            try:
                info = row.find_elements(By.CLASS_NAME, 'center')
                pos, age, yr1, yr2, yr3, yr4, yr5, yr6 = [elem.text.split('\n') for elem in
                                                          info[:8]]  # create individual lists
                pos = str(pos[0])
                age = int(age[0])
                sal1, per1 = year_breakdown(yr1)
                sal2, per2 = year_breakdown(yr2)
                sal3, per3 = year_breakdown(yr3)
                sal4, per4 = year_breakdown(yr4)
                sal5, per5 = year_breakdown(yr5)
                sal6, per6 = year_breakdown(yr6)
            except Exception as e:
                print("Failed at extracting yearly contract data")
                print(e)
                continue
            print(
                f"{name}, {contract}, {type}, {pos}, {age}, {sal1, per1}, {sal2, per2}, {sal3, per3}, {sal4, per4}, {sal5, per5}, {sal6, per6}")
            data.append(
                [name, contract, type, pos, age, sal1, per1, sal2, per2, sal3, per3, sal4, per4, sal5, per5, sal6,
                 per6])
            print("----------------------------------------------------")
        driver.quit()
    except Exception as e:
        driver.quit()
        print("Failed to get webpage")
        print(e)

    df = pd.DataFrame(data, columns=['Name', 'Contract', 'Type', 'Position', 'Age', 'Year 1 Salary', 'Year 1 %Cap',
                                     'Year 2 Salary', 'Year 2 %Cap', 'Year 3 Salary', 'Year 3 %Cap', 'Year 4 Salary',
                                     'Year 4 %Cap', 'Year 5 Salary', 'Year 5 %Cap', 'Year 6 Salary', 'Year 6 %Cap'])
    df['Team'] = team
    d = os.getcwd()
    df.to_csv(os.path.join(d, f'{team}-contracts.csv'), index=False)