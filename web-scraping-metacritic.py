import requests
import mysql.connector
import re
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# Need a header, so that the Website didn't think, we are a bot
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

# Establish connection to the database
conn = mysql.connector.connect(user='root', password='root', host='127.0.0.1', database='metacritic')
cursor = conn.cursor()

game_id = 1

try:
    # Delete Table 'games', if this Table already exists
    cursor.execute("DROP TABLE IF EXISTS games")
    # Create new table with all the necessary columns
    cursor.execute("CREATE TABLE games (id int, ranking varchar(255), title varchar(255), metascore varchar(255), userscore varchar(255), platform varchar(255))")
    # Commit the db transaction
    conn.commit()
    # Print 'SUCCESS', if the transactions are commited successfully
    print("SUCCESS")
except Exception as e:
    conn.rollback()
    print(e)
    
#todo: Find out last page -> For test purposes we use 2
for i in range(0, 2):
    url = "https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?page=" + str(i)

    page = requests.get(url, headers = headers)
    soup = BeautifulSoup(page.content, "html.parser")
    container = soup.find_all("td", class_="clamp-summary-wrap")

    for container_element in container:
        
        # get specific data from current website
        rank_element = container_element.find("span", class_="title numbered")
        title_element = container_element.find("a", class_="title") 
        metascore_element = container_element.find("div", class_="clamp-score-wrap")
        userscore_element = container_element.find("div", class_="clamp-userscore") 
        platform_element = container_element.find("span", class_="data")
        
        # remove all unnecessary html tags with .text and all unnecessary spaces with .strip()
        rank = rank_element.text.strip()
        title = title_element.text.strip()
        metascore = metascore_element.text.strip()
        userscore = userscore_element.text.strip()
        platform = platform_element.text.strip()
        
        # remove all unnecessary characters
        rank_cleared = rank.replace(".", "")
        title_cleared = title.replace("'", "")
        userscore_cleared = re.sub("[^0.0-9.9]+", "", userscore)
        
        print(userscore)
        
        try:
            cursor.execute("INSERT INTO games (id, ranking, title, metascore, userscore, platform) VALUES ('%d', '%s', '%s', '%s', '%s', '%s')" 
                           % (game_id, rank_cleared, title_cleared, metascore, userscore_cleared, platform))
            conn.commit()
            print("SUCCESSFULLY INSERT INTO DB: Game ID: %d, Rank: %s, Title: %s, Metascore: %s, Userscore %s, Platform: %s" 
                  % (game_id, rank_cleared, title_cleared, metascore, userscore_cleared, platform))
        except Exception as e:
            conn.rollback()
            print(e)
            
        game_id = game_id + 1
            
conn.close()

# Visualizing data using Matplotlib
plt.bar(rank, title)
plt.ylim(0, 5)
plt.xlabel("Name of Students")
plt.ylabel("Marks of Students")
plt.title("Student's Information")
plt.show()
