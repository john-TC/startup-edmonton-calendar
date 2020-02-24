import caldav
import vobject
import bs4 as bs
from datetime import datetime
from caldav.elements import dav
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

siteUrl = "https://www.startupedmonton.com/events-overview"
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.get(siteUrl)
soup = bs.BeautifulSoup(driver.page_source, "html.parser")
month = soup.find("div", {"class", "yui3-u yui3-calendar-header-label"})
nextMonthButton = driver.find_element_by_xpath("//a[@class='yui3-u yui3-calendarnav-nextmonth']")
prevMonthButton = driver.find_element_by_xpath("//a[@class='yui3-u yui3-calendarnav-prevmonth']")

calUrl = "https://username:password@calendarhost.com"
client = caldav.DAVClient(calUrl)
principal = client.principal()
calendars = principal.calendars()

try:
    element_present = EC.presence_of_element_located((By.TAG_NAME, "body"))
    WebDriverWait(driver, 15).until(element_present)

    for cal in calendars:
        if cal.get_properties([dav.DisplayName()]) == {'{DAV:}displayname': 'Startup Edmonton'}:
            print("Found calendar")
            cal.delete()
            print("Deleted calendar")
    principal.make_calendar("Startup Edmonton")
    print("Created calendar")
    calendars = principal.calendars()
    for cal in calendars:
        if cal.get_properties([dav.DisplayName()]) == {'{DAV:}displayname': 'Startup Edmonton'}:
            calendar = cal
            print("Using calendar:", cal)

    while month.text != "January 2020":
        prevMonthButton.click()
        soup = bs.BeautifulSoup(driver.page_source, "html.parser")
        month = soup.find("div", {"class", "yui3-u yui3-calendar-header-label"})

    while month.text != "January 2021":
        tableData = soup.find_all("td", {"class": "has-event"})
        for data in tableData:
            eventData = data.find_all("li", {"class": "flyoutitem"})
            for event in eventData:
                name = event.find("a", {"class": "flyoutitem-link"}).text
                time = event.find("div", {"class", "flyoutitem-datetime--24hr"}).text.strip().split(" – ")
                date = data.find("div", {"class", "marker-daynum"}).text

                startDateString = month.text + " " + date + " " + time[0]
                startDateObject = datetime.strptime(startDateString, "%B %Y %d %H:%M")
                endDateString = month.text + " " + date + " " + time[1]
                endDateObject = datetime.strptime(endDateString, "%B %Y %d %H:%M")

                vcal = vobject.iCalendar()
                vcal.behavior
                vcal.add("vevent")

                utc = vobject.icalendar.utc
                startDate = vcal.vevent.add("dtstart")
                startDate.value = startDateObject
                endDate = vcal.vevent.add("dtend")
                endDate.value = endDateObject

                vcal.vevent.add("summary").value = name
                icalstream = vcal.serialize()
                calendar.add_event(icalstream)
                print("Synced", month.text , name)

        nextMonthButton.click()
        soup = bs.BeautifulSoup(driver.page_source, "html.parser")
        month = soup.find("div", {"class", "yui3-u yui3-calendar-header-label"})

except TimeoutException:
    exit("Error: Timed out")
finally:
    driver.quit()
