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
            if not table:
                return None
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
        for year in range(2021, 2022):
            df = Madness.gamelog(school_id, year)
            if isinstance(df, pd.DataFrame):
                dfs.append(df)
        if dfs:
            return pd.concat(dfs)
        else: 
            return None
    
    @staticmethod
    def tournament(year):
        url = f"https://www.sports-reference.com/cbb/postseason/{str(year)}-ncaa.html"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        else:
            soup = BeautifulSoup(response.text, "lxml")
            brackets = soup.find("div", attrs={"id" : "brackets"})
            regions = brackets.find_all("div", recursive=False)
            results = []
            for region in regions:
                bracket = region.find("div", attrs={"id" : "bracket"})
                rounds = bracket.find_all("div", attrs={"class" : "round"})
                for round_ind, rnd in enumerate(rounds):
                    games = rnd.find_all("div", recursive=False)
                    for game in games:
                        game_dict = dict()
                        teams = game.find_all("div", recursive=False)
                        for team_ind, team in enumerate(teams):
                            if len(team.find_all("a")) == 2:
                                school_link = team.find("a")
                                game_link = school_link.find_next_sibling()
                                game_dict[f"team_{team_ind + 1}_code"] = school_link.get("href").split("/")[-2]
                                game_dict[f"team_{team_ind + 1}_rank"] = team.find("span").text
                                game_dict[f"team_{team_ind + 1}_score"] = game_link.text
                        game_dict["round"] = round_ind + 1
                        game_dict["region"] = region.get("id")
                        results.append(game_dict)
            df = pd.DataFrame(results)
            df["year"] = year
            df = df.drop_duplicates()
            df = df.dropna(subset=["team_1_code"]).reset_index(drop=True)
            return df

if __name__=="__main__":
    #print(Madness.schools())
    print(Madness.tournament(2019))
    
    
