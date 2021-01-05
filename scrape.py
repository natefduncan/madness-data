from madness import Madness
from tqdm import tqdm
import pandas as pd

if __name__=="__main__":
    schools = Madness.schools()
    schools.to_csv("data/schools.csv")
    dfs = list()
    for ind, school in tqdm(schools.iterrows()):
        df = Madness.gamelog_all_years(school["school_id"])
        if isinstance(df, pd.DataFrame):
            dfs.append(df)
    df = pd.concat(dfs).to_csv("data/gamelogs.csv")