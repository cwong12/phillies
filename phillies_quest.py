#!/usr/bin/python
#written by Christopher Wong
import numpy as np
import urllib
from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt


def scrape():

    #perform scraping
    DATA_URL = "https://questionnaire-148920.appspot.com/swe/data.html"

    req = urllib.request.Request(DATA_URL)
    response = urllib.request.urlopen(req)
    page = response.read()

    parsed = BeautifulSoup(page, 'html.parser')

    #found the data format by inspecting the html in a browser
    table = parsed.find_all('tbody')[0]
    salary_data = table.find_all('td',attrs={'class':'player-salary'})
    salary_list = []
    for entry in salary_data:

        curEntry = entry.text

        #filter out invalid entries
        if (len(curEntry)>0 and curEntry != "no salary data"):
            #string deletion sourced from:
            #https://www.geeksforgeeks.org/python-removing-unwanted-characters-from-string/
            no_dollar_sign = curEntry.replace("$", "")
            no_comma = no_dollar_sign.replace(",", "")
            salary_list.append(no_comma)

    df = pd.DataFrame(salary_list, columns = ['salaries'])

    #convert entries to ints so we can call mean()
    df["salaries"] = pd.to_numeric(df["salaries"])
    avg = float(df.nlargest(125, "salaries").mean())
    print("The qualifying offer value is: $" + str(avg))
    return df, avg


def visualize(df, avg):

    #split up the data to be graphed separately
    dataLarge = np.array(df.nlargest(125, "salaries"))
    dataSmall = np.array(df.nsmallest(df.shape[0] -125, "salaries"))

    #create two subplots so we can produce a break in the y-axis to account
    #for outliers i.e. the 700+ players on league minimum contracts
    f, (top, bottom) = plt.subplots(2, 1, sharex=True)


    colors = ["blue", "orange"]
    labels = ["Other Contracts", "Top 125 Contracts"]
    top.hist(dataSmall, 10,rwidth = 0.5, color = "blue")
    bottom.hist([dataSmall,dataLarge], 33, color=colors, label=labels)

    #add line depicting qualifying offer value
    top.axvline(x=avg, linestyle='--', color='red')

    roundAvg = round(avg/1000000, 2)
    bottom.axvline(x=avg, linestyle='--', color='red', label='Qual. Offer Value ($' + str(roundAvg) + "M)")

    # Graph break sourced from:
    # https://matplotlib.org/2.0.2/examples/pylab_examples/broken_axis.html
    top.set_ylim(600, 750)  # outliers only
    bottom.set_ylim(0, 60)  # most of the data
    top.grid(axis='y', alpha=0.3)
    bottom.grid(axis='y', alpha=0.3)

    top.spines['bottom'].set_visible(False)
    bottom.spines['top'].set_visible(False)
    top.xaxis.tick_top()
    top.tick_params(labeltop='off')  # don't put tick labels at the top
    bottom.xaxis.tick_bottom()
    plt.xticks([], np.arange(0, 35, step=5))


    d = .015

    kwargs = dict(transform=top.transAxes, color='k', clip_on=False)
    top.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
    top.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs.update(transform=bottom.transAxes)  # switch to the bottom axes
    bottom.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    bottom.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

    plt.xticks(range(1, 34000000,5000000))

    f.suptitle("Distribution of Major League Contracts (2016)")

    bottom.set_xlabel("Salary in millions ($)")
    top.set_ylabel("# of Contracts")
    bottom.set_ylabel("# of Contracts")
    bottom.legend()


    plt.show()

def main():
    df, avg = scrape()
    visualize(df, avg)
if __name__ == '__main__':
    main()
