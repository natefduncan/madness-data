from bs4 import BeautifulSoup
import requests
import pandas as pd

class Madness:

    @staticmethod
    def schools():
        url = "https://www.sports-reference.com/cbb/schools/"
        dfs = pd.read_html(url)
        df = dfs[0]
        df["Rk"] = pd.to_numeric(df["Rk"], errors="coerce")
        df = df.dropna(subset=["Rk"]).reset_index(drop=True)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace(',', '')
        return df

if __name__=="__main__":
    print(Madness.schools())
    
    