from bs4 import BeautifulSoup
import requests
import pandas as pd

from utils import clean_columns

class Madness:

    @staticmethod
    def schools():
        url = "https://www.sports-reference.com/cbb/schools/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text)
        table = soup.find("table", attrs={"id" : "schools"})
        headers = table.find("thead")
        columns = clean_columns([i.text for i in headers.find_all("th")])
        body = table.find("tbody")
        rows = body.find_all("tr")
        hrefs = list()
        values = list()
        for row in rows:
            cells = row.find_all("td")
            if cells:
                link = cells[0].find("a")
                if link:
                    hrefs.append(link.get("href").split("/")[-2])
                    values.append([i.text for i in cells])
        df = pd.DataFrame(values, columns=columns[1:])
        df["href"] = hrefs
        return df

if __name__=="__main__":
    print(Madness.schools())
    
    