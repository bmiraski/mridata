import sys
from selenium import webdriver

browser = webdriver.Chrome()

browser.get('http://www.espn.com/college-football/scoreboard/_/group/80/year/2017/seasontype/2/week/6')

games = browser.find_elements_by_link_text('Box Score')

weekfile = open("C:\\Users\\MILES_DAVIS\\Desktop\\stats\\weekfile.txt", "w")

for elem in games:
    x = elem.get_attribute('href')
    print(x)
    x = x + '\n'
    weekfile.write(x)




#weekfile = open("C:\\Users\\MILES_DAVIS\\Desktop\\stats\\weekfile.txt", "wb")

#for chunk in res.iter_content(2500):
#        weekfile.write(chunk)

weekfile.close()