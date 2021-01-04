def clean_columns(col_list):
    return [i.strip().lower().replace(' ', '_').replace('(', '').replace(')', '').replace(',', '') for i in col_list]