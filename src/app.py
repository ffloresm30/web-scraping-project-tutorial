import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from io import StringIO

def download_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error: {response.status_code}")

def transform_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    if not tables:
        raise Exception("No se encontraron tablas en el HTML.")
    annual_growth_table = tables[0]
    html_string = str(annual_growth_table)
    df = pd.read_html(StringIO(html_string))[0]
    df['Revenue'] = df['Revenue'].replace({"[$B]": ""}, regex=True).str.strip().astype(float)
    df['Change'] = df['Change'].replace({"%": ""}, regex=True).str.strip().astype(float)
    df.dropna(subset=['Year', 'Revenue', 'Change'], inplace=True)
    return df

def save_to_db(df, db_name='tesla_growth.db'):
    with sqlite3.connect(db_name, timeout=10) as conn:
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS tesla_growth')
        c.execute('''
            CREATE TABLE tesla_growth (
                Year INTEGER,
                Revenue FLOAT,
                Change FLOAT
            )
        ''')
        for index, row in df.iterrows():
            c.execute('''
                INSERT INTO tesla_growth (Year, Revenue, Change) 
                VALUES (?, ?, ?)
            ''', (row['Year'], row['Revenue'], row['Change']))
        conn.commit()

def plot_data(df):
    df.plot(kind='bar', x='Year', y='Change', legend=False)
    plt.title('Crecimiento Anual de Tesla')
    plt.xlabel('Año')
    plt.ylabel('Crecimiento (%)')
    plt.savefig('/workspaces/web-scraping-project-tutorial/src/crecimiento_anual_tesla.png')  # Guardar gráfico en el directorio src
    plt.close()  # Cerrar el gráfico para evitar problemas de memoria

    
if __name__ == "__main__":
    url = 'https://companies-market-cap-copy.vercel.app/index.html'
    html_content = download_html(url)
    df = transform_html(html_content)
    save_to_db(df)
    plot_data(df)
