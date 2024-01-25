import requests
from ics import Calendar
from Vectors.Hidden import webcal_link
import os

def webcal_to_txt(webcal_link, txt_filename):
    open(txt_filename, 'w').write(str(Calendar(requests.get(webcal_link.replace('webcal://', 'http://')).text)))

def clear_file_if_exists(filename):
    if os.path.exists(filename):
        open(filename, 'w').close()

# Example usage
webcal_to_txt(webcal_link, "Calender.txt")
clear_file_if_exists('Calendar.ics')
clear_file_if_exists('Calendar.txt')
