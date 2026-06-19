import requests

IP = "127.0.0.1"
PORT = "5000"
URL = f"http://{IP}:{PORT}"

from dotenv import load_dotenv
import os
import json
import math

load_dotenv()
AUTH = "Bearer " + os.getenv("API_MASTER_AUTH")

def test1():
    with open("/home/ssymboint/Desktop/prog/python/projects/apimaybe/testing/media/micheal.png", "rb") as f:
        files = {'image': f}
    
        res = requests.post(
            f"{URL}/api/cotd/upload",
            headers={
                "Authorization": AUTH
            },
            data={"data": '{"title": "bingus2", "description": "bongus"}'},
            files=files
        )

    print(res.status_code)
    print(res.json())

def test2():
    res = requests.post(
        f"{URL}/api/cotd/upload",
        headers={
            "Authorization": "Bearer hellotherethisisatoken"
        },
        json={
            "title": "bingus2",
            "description": "bongus",
            # "date": "2021-11-01"
        }
    )
    print(res.status_code)
    print(res.json())

def test3():
    res = requests.post(
        f"{URL}/api/cotd/edit",
        headers={
            "Authorization": "Bearer hellotherethisisatoken"
        },
        json={
            "title": "what",
            "description": "bongus",
            "entry_no": 444
        }
    )
    print(res.status_code)
    print(res.json())

def test4():
    res = requests.delete(
        f"{URL}/api/cotd/delete",
        headers={
            "Authorization": "Bearer hellotherethisisatoken"
        },
        json={
            "date": "2021-11-01"
        }
    )
    print(res.status_code)
    print(res.json())


def test5():
    res = requests.get(
        f"{URL}/api/cotd/get",
        json={
            "date": "2021-11-01"
        }
    )
    print(res.status_code)
    print(res.json())

def test6():
    res = requests.get(f"{URL}/api/cotd/get_today")
    print(res.status_code)
    print(res.json())


def test7():
    # get page data from page n
    data = [{
        "title": "tit",
        "description": "desc",
        "entry_no": i + 1
    } for i in range(1042)]

    entries_per_page = 10

    page_n = 107

    total_pages = math.ceil(len(data) / entries_per_page)
    page_n = page_n % total_pages
    end = (entries_per_page * page_n) - 1
    start = end - entries_per_page + 1
    page_entries = data[start:(end+1)]

    print(start)
    print(end)
    print(f"page: {page_n}/{total_pages}")
    print(len(page_entries))
    print(json.dumps(page_entries, indent=4))
    
def test8():
    # get last page

    data = [{
        "title": "tit",
        "description": "desc",
        "entry_no": i + 1
    } for i in range(1042)]

    entries_per_page = 10

    total_pages = math.ceil(len(data) / entries_per_page)
    page_n = total_pages
    end = (entries_per_page * page_n)-1
    start = end - entries_per_page+1
    if end > len(data):
        end = len(data)-1
    page_entries = data[start:(end+1)]
    page_entry_count = len(page_entries)

    res = {
        "page_entries": page_entries,
        "page_entries_count": page_entry_count,
        "page_number": page_n,
        "total_pages": total_pages,
        "entries_range": [start+1, end+1]
    }

    print(json.dumps(res, indent=4))

    # print(start)
    # print(end)
    # print(f"page: {page_n}/{total_pages}")
    # print(f"showing entires: {start+1}-{end+1}")
    # print(len(page_entries))
    # print(json.dumps(page_entries, indent=4))

if __name__ == "__main__":
    # test1()
    # test2()
    # test3()
    # test4()
    # test5()
    # test6()
    # test7()
    test8()