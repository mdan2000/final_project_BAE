import streamlit as st
with st.echo(code_location='below'):
    import pandas as pd
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
    import altair as alt
    import requests
    import sqlite3
    from sklearn import tree
    import networkx as nx
    import re

    ### Below you can see the code of the data ccollection:

    # from selenium import webdriver
    # from selenium.webdriver.chrome.service import Service
    # from webdriver_manager.chrome import ChromeDriverManager
    # from selenium.webdriver.common.by import By
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # driver.get("https://www.farfetch.com/am/shopping/women/dresses-1/items.aspx")
    # products = driver.find_elements(By.TAG_NAME, 'a')
    # collections = []
    # brands = []
    # items = []
    # prices_without_discount = []
    # discounts = []
    # prices = []
    # available_sizes = []
    # for i in range(1, 40):
    #     page = str(i + 1)
    #     site = 'https://www.farfetch.com/am/shopping/women/dresses-1/items.aspx?page=' + page + '&view=90&sort=3'
    #     driver.get(site)
    #     products = driver.find_elements(By.TAG_NAME, 'a')
    #     for product in products:
    #         collection_and_brand_and_item = product.find_elements(By.TAG_NAME, 'p')
    #         if len(collection_and_brand_and_item) > 7:
    #             collections.append(collection_and_brand_and_item[0].text)
    #             brands.append(collection_and_brand_and_item[1].text)
    #             items.append(collection_and_brand_and_item[2].text)
    #             prices_without_discount.append(collection_and_brand_and_item[3].text)
    #             discounts.append(collection_and_brand_and_item[4].text)
    #             prices.append(collection_and_brand_and_item[5].text)
    #         elif len(collection_and_brand_and_item) > 5:
    #             collections.append(collection_and_brand_and_item[0].text)
    #             brands.append(collection_and_brand_and_item[1].text)
    #             items.append(collection_and_brand_and_item[2].text)
    #             prices_without_discount.append(collection_and_brand_and_item[3].text)
    #             discounts.append('')
    #             prices.append('')
    # df = pd.DataFrame({'collection': collections, 'brand': brands, 'item': items,
    #                    'price_without_discount': prices_without_discount,
    #                    'discount': discounts, 'clean_price': prices})
    # df['clean_price'][df['clean_price'] == ""] = df['price_without_discount']
    # df = df.assign(price_without_discount= lambda x: x['price_without_discount']
    #     .str[1:].str.replace(',', '').astype(float))
    # df = df.assign(clean_price= lambda x: x['clean_price'].str[1:].str.replace(',', '').astype(float))
    # df['discount'][df['discount']=='']= '-0%'
    # df = df.assign(discount= lambda x: x['discount'].str[1:].str[:-1].astype(float))
    # df['maltiply'] = 1 - df['discount']/100
    # df.to_csv('dresses.csv')

    @st.cache
    def get_data():
        data_url = ('dresses.csv')
        return (pd.read_csv(data_url))
    df = get_data()
    st.write("here you can see the whole collected data")
    st.write(df)

    st.text("Here are all our brands: ")
    st.write(df['brand'].unique())


    conn = sqlite3.connect("database.sqlite")
    c = conn.cursor()
    #df.to_sql("dres2", conn) #we used this once, so the table already exist
    st.write(pd.read_sql(""" SELECT count(*), avg(clean_price), avg(price_without_discount) FROM dres2 """, conn))
    df_avg_price_without_discount = pd.read_sql("""SELECT brand, avg(price_without_discount) as 
    avg_price_without_discount FROM dres2 GROUP BY brand ORDER BY avg_price_without_discount DESC """, conn)
    st.write(df_avg_price_without_discount)



    st.write("Here we can see only the brands with more then 40 items from our data:")
    df_more_than_40 = pd.read_sql("""SELECT brand, count(*) as count FROM dres2 GROUP BY brand
    ORDER BY count DESC LIMIT 14 """, conn)
    st.write(df_more_than_40)

    df_new_season = df[df['collection'] == "New Season"]['brand'].value_counts().reset_index()\
        .rename(columns = {'index': 'brand', 'brand': 'count'})
    st.write(df_new_season)
    st.text("And we will take only those that have more than 10 such items.")
    df_new_season_7 = df_new_season[0:6]

    df_conscious = df[df['collection'] == "Conscious"]['brand'].value_counts().reset_index()\
        .rename(columns = {'index': 'brand', 'brand': 'count'})
    st.write(df_conscious)
    st.text("And we will take only those that have more than 10 such items.")
    df_conscious_7 = df_conscious[0:6]

    fig, ax = plt.subplots(1, 2)
    sns.violinplot(x='count', y='brand', data=df_new_season_7,
                   palette=['#BB0B4F', '#0C35AF'],
                   ax=ax[0])
    sns.violinplot(x='count', y='brand', data=df_conscious_7,
                   palette=['#BB0B4F', '#0C35AF'],
                   ax=ax[1])
    fig.set_tight_layout(True)
    st.pyplot(fig)

    chart = alt.Chart(df_more_than_40, title=f"Number of items dresses") \
        .mark_bar().encode(x='brand', y='count')
    st.write(chart)

    st.text("Now you can choose the brand and the collection and receive the predicted price")
    brand = st.selectbox("brand", df["brand"].value_counts().index)
    df_selection = df[lambda x: x["brand"] == brand]
    collection = st.selectbox("collection", df["collection"].value_counts().index)
    df_selection2 = df[lambda x: x["collection"] == collection]

    X = df[['collection', 'brand']]
    X['collection'] = X['collection'].apply(hash)
    X['brand'] = X['brand'].apply(hash)
    Y = df['clean_price']
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X, Y)
    a = clf.predict([[hash(collection), hash(brand)]])
    st.write("predicted price is ", a[0])

    df['item'].findall('print*dress', flags=re.IGNORECASE)


    g = df[['collection', 'brand']]

    brands_for_graph = ['Self-Portrait', 'SANDRO', 'Reformation', 'Dolce & Gabbana', 'ZIMMERMANN', 'PINKO',
                        'Tadashi Shoji', 'GANNI', 'Maje', 'TWINSET', 'Elisabetta Franchi']
    for brand in brands_for_graph:
        season_of_brand = list(pd.unique(g[g['brand'] == brand]['collection']))
        for i in range(len(season_of_brand)):
            if pd.isna(season_of_brand[i]):
                season_of_brand[i] = 'Without collection'
        G = nx.Graph()
        for season in season_of_brand:
            G.add_edge(brand, season)
        st.write(nx.draw(G, width=0.03))
        #plt.savefig(f'{brand}.pdf')
        #plt.cla()

    np_prices = np.array([df_avg_price_without_discount])
    df_disc = df['discount'][df['discount'] > 0]
    np_discount = np.array([df_disc['discount']])
    mean_discount = [np.mean(np_discount)]
    new_prices = np_discount * np_prices
    st.write('There you can see prices with average discounts', new_prices)

    st.write('The first commented text is my collection of data')








