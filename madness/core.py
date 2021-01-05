from bs4 import BeautifulSoup
import requests
import pandas as pd

from .utils import clean_columns

class Madness:

    @staticmethod
    def schools():
        url = "https://www.sports-reference.com/cbb/schools/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
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
        df["school_id"] = hrefs
        return df

    @staticmethod
    def gamelog(school_id, year):
        url = f"https://www.sports-reference.com/cbb/schools/{school_id}/{str(year)}-gamelogs.html"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        else: 
            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table", attrs={"id" : "sgl-basic"})
            body = table.find("tbody")
            rows = body.find_all("tr")
            output = list()
            for row in rows:
                cells = row.find_all("td")
                if cells:
                    row_dict = {i.get("data-stat"): i.text for i in cells if i.get("data-stat")}
                    for cell in cells:
                        data_stat = cell.get("data-stat")
                        if data_stat == "date_game":
                            link = cell.find("a")
                            if link:
                                row_dict["game_ref"] = link.get("href")
                            else:
                                row_dict["game_ref"] = None

                        if data_stat == "opp_id":
                            row_dict["opp_name"] = row_dict.get("opp_id", None)
                            link = cell.find("a")
                            if link:
                                row_dict["opp_id"] = cell.find("a").get("href").split("/")[-2]
                            else:
                                row_dict["opp_id"] = None
                    output.append(row_dict)

            df = pd.DataFrame(output)
            df["season"] = year
            df["school_id"] = school_id
            return df

    @staticmethod
    def gamelog_all_years(school_id):
        dfs = list()
        for year in range(2011, 2021):
            df = Madness.gamelog(school_id, year)
            if isinstance(df, pd.DataFrame):
                dfs.append(df)
        if dfs:
            return pd.concat(dfs)
        else: 
            return None
            
if __name__=="__main__":
    #print(Madness.schools())
    print(Madness.gamelog_all_years("abilene-christian"))
    
    