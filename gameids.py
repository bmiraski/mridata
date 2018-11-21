import sys
from selenium import webdriver

browser = webdriver.Chrome()

browser.get('http://www.espn.com/college-football/scoreboard/_/group/80/year/2018/seasontype/2/week/7')

games = browser.find_elements_by_name('&lpos=college-football:scoreboard:boxscore')

gamelist = []

for elem in games:
    x = elem.get_attribute('href')
    x = x[-9:]
    gamelist.append(x)

print(gamelist)



#weekfile = open("C:\\Users\\MILES_DAVIS\\Desktop\\stats\\weekfile.txt", "wb")

#for chunk in res.iter_content(2500):
#        weekfile.write(chunk)
