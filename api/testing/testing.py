import requests

IP = "127.0.0.1"
PORT = "5000"
URL = f"http://{IP}:{PORT}"

from dotenv import load_dotenv
import os

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


if __name__ == "__main__":
    test1()
    # test2()
    # test3()
    # test4()
    # test5()
    # test6()