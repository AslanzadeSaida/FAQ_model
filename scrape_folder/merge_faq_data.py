import pandas as pd

df_01 = pd.read_csv("/home/saida/Desktop/Web_scraping/faq_data_asan_login.csv")
df_02 = pd.read_csv("/home/saida/Desktop/Web_scraping/faq_data_egov.csv")
df_03 = pd.read_csv("/home/saida/Desktop/Web_scraping/faq_data_mygov.csv")


merged_df = pd.concat([df_01, df_02, df_03], ignore_index=True)

merged_df.to_csv("merged_faq_data_file.csv", index=False)

