#!/usr/bin/python

'''
InstaFetch v1.0

Creator : Sanjevi Rau
Website : http://www.sanjevirau.com

==============================
InstaFetch is a Python script that uses Webstagram to automatically download all the photo and video
posts from Instagram Public accounts.

Requirements:
- python > 3.0
- requests library
- beautifulsoup4 library

Take Note:
- make sure you have the correct version of Python installed
- make sure you have the pycurl and beautifulsoup4 library installed
- make sure the Instagram User Profile is in "Public"

Usage:
instafetch.py [username]

==============================
Warning:
Before you use InstaFetch, make sure you obtain permission from the Instagram user to download their posts.
I do not approve of any usage of this script without the original user's consent.
'''

import requests
import urllib.request
import os
import platform
import subprocess
import sys
import time
from bs4 import BeautifulSoup

global count
count = 0


def close():
    sys.exit()


def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


# Function to get Full Instagram Name
def real_name():
    url = "http://websta.me/n/" + str(username)
    source = requests.get(url)
    plain_text = source.text
    bs4 = BeautifulSoup(plain_text)
    source_name = bs4.find('h2', {"class": "fullname-headline"})
    global name
    while True:
        try:
            name = source_name.string
            break
        except AttributeError:
            name = "Not Stated"
            break


# Function to get No of Posts and check if account in "Public" or "Private"
def no_posts():
    url = "http://websta.me/n/" + str(username)
    source = requests.get(url)
    plain_text = source.text
    bs4 = BeautifulSoup(plain_text)
    source_name = bs4.find('span', {"class": "counts_media"})
    global prof_type
    global posts
    while True:
        try:
            posts = source_name.string
            prof_type = "Public"
            break
        except AttributeError:
            prof_type = "Private"
            break


# Function to download posts
def fetcher_photo(url):

    global count
    count += 1

    source = requests.get(url)
    plain_text = source.text
    bs4 = BeautifulSoup(plain_text)
    global dl_path
    dl_path = "InstaFetch/" + username
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
    for photo in bs4.findAll('a', {"class": "cb_ajax"}):
        det = photo.get('href')
        fullname = username + "_" + str(count) + ".jpg"
        urllib.request.urlretrieve(det, dl_path + "/" + fullname)
    for video in bs4.findAll('div', {"class": "jp-jplayer"}):
        det = video.get('data-m4v')
        fullname = username + "_" + str(count) + ".mp4"
        urllib.request.urlretrieve(det, dl_path + "/" + fullname)

    percentage = int((int(count) / int(posts)) * 100)
    print("Fetching Instagram Posts : " + str(percentage) + "% (" + str(count) + " posts downloaded)", end="\r")


# Main Function
def fetcher(user):
    print("")
    print("==================================")
    print("InstaFetch v1.0")
    print("==================================")
    print("")
    global username
    # If no arguments entered, ask for username
    if user == "NONE":
        username = input("Type in the Instagram Public Account's username : ")
    else:
        username = str(user)
    # Display username
    print("Username To Fetch : " + str(username))
    # Display Full Instagram Name
    real_name()
    print("Full Instagram Name : " + str(name))
    # Calculate No of Post
    no_posts()
    # Check if username is in Public or Private
    if prof_type == "Public":
        print("Profile Type : Public")
    elif prof_type == "Private":
        print("Profile Type : Private")
        print("")
        print("InstaFetch can only fetch posts from Public Instagram profiles.")
        print("")
        input("Press Enter to exit InstaFetch.")
        close()
    # Display No Of Posts
    print("Estimated Posts Available : " + str(posts))
    # If zero posts, then exit program
    if str(posts) == "0":
        print("")
        print("There are no posts to fetch.")
        print("")
        input("Press Enter to exit InstaFetch")
        close()

    global paginated
    paginated = int(posts) // 20
    start = time.time()
    # If posts more than 20, then use paginated crawl
    if paginated == 0:
        url = "http://websta.me/n/" + str(username)
        source = requests.get(url)
        plain_text = source.text
        bs4 = BeautifulSoup(plain_text)
        for link in bs4.findAll('a', {"class": "mainimg"}):
            det = link.get('href')
            det_full = "http://websta.me" + det
            fetcher_photo(det_full)
    else:
        url_list = ["http://websta.me/n/" + str(username)]
        url = "http://websta.me/n/" + str(username)
        count = 0
        while True:
            source = requests.get(url)
            plain_text = source.text
            bs4 = BeautifulSoup(plain_text)
            link = bs4.find('a', {"rel": "next"})
            det = link.get('href')
            det_full = "http://websta.me" + det
            url_list.extend([det_full])
            url = det_full
            count += 1
            if count == paginated:
                break
        for single_url in url_list:
            source = requests.get(single_url)
            plain_text = source.text
            bs4 = BeautifulSoup(plain_text)
            for link in bs4.findAll('a', {"class": "mainimg"}):
                det = link.get('href')
                det_full = "http://websta.me" + det
                fetcher_photo(det_full)
    end = time.time()
    # Calculate total time
    elapsed = end - start
    print("\n")
    # Display success message
    print("Succesfully fetched " + str(len([check for check in os.listdir(dl_path) if os.path.isfile(os.path.join(dl_path, check))])) + " posts (took " + str("%.2f" % elapsed) + " seconds)")
    print("Opening downloaded directory...")

    # Open the downloaded posts
    try:
        root = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        root = os.path.dirname(os.path.abspath(sys.argv[0]))

    open_file(root + "/" + dl_path)
    print("")
    input("Press Enter to exit InstaFetch")
    close()


try:
    # If Help argument tried, display help.
    if str(sys.argv[1]) == "-h" or str(sys.argv[1]) == "--help":
        print("")
        print("==============================================================================")
        print("InstaFetch v1.0")
        print("Creator : Sanjevi Rau")
        print("")
        print("InstaFetch is a Python script that uses Webstagram to automatically download")
        print("all the photo and video posts from Instagram Public accounts.")
        print("")
        print("Usage:")
        print("instafetch.py/instafetch.exe [username]")
        print("")
        print("Warning:")
        print("Before you use InstaFetch, make sure you obtain permission from the Instagram")
        print("user to download their posts.I do not approve of any usage of this script ")
        print("without the original user's consent.")
        print("==============================================================================")
    else:
        fetcher(str(sys.argv[1]))
except IndexError:
    fetcher("NONE")