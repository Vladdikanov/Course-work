import requests
import json
access_token = 'vk1.a.L3DffFxySUmzorLMkHdXO4UkwhAcVtr0pi2pBhXDGG7dFBcM3yXBA1kaoO2qxvNZ-PAV1HuYa-j6ShUwRTQYlgz-y0jRcUM-jn4ebhpEWofu95jMpE1X3SsmQ7AWS4NfFrCQQUcwaExzckh_hZ574hAPUsFM2xmgOkHskzoYU6OKS3vv5wHaddN_nCRTUkxtisuFd0jGjtFIi2fprUqUFg'

class Yandex:
    def __init__(self,ya_token):
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {ya_token}'}
    def create_folder(self,name_folder):
        params = {"path": name_folder}
        res = requests.put('https://cloud-api.yandex.net/v1/disk/resources', headers=self.headers, params=params)

        if res.status_code == 201:
            print(f"Папка создана под именем '{name_folder}'")
        elif res.status_code == 409:
            print(f"Файлы будут помещены в папку '{name_folder}'")
        else:
            print("Не удалось создать папку")
    def upload_files(self, name_file, url):
        params = {"path": name_file, "url": url, "overwrite" : True}
        res = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=self.headers, params=params)
        if res.status_code == 202:
            print("Фото загружено на Диск")
        else:
            print("Не удалось загрузить фото на диск")
        return res
    def get_link_upload(self, disk_path):
        params = {"path": disk_path, "overwrite" : True}
        res = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=self.headers, params=params)
        return res.json()["href"]
    def upload_info_to_disk(self, local_path, ya_path):
        link_for_upload = self.get_link_upload(ya_path)
        res = requests.put(link_for_upload, data=open(local_path, "rb"), headers=self.headers)
        if res.status_code == 201:
            print("Информация о файлах загружена на диск")
        else:
            print("Не удалось загрузить информацию о файлах")


class VK:

    def __init__(self, access_token, version='5.131'):
        self.token = access_token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self, user_id):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': user_id}
        response = requests.get(url, params={**self.params, **params})
        if response.status_code == 200:
            print("Данные пользователя получены")
        else:
            print("Не удалось получить данные пользователя")
        return response.json()

    def get_photos(self,user_id):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': user_id,
                  'album_id': "profile",
                  "photo_sizes": "1",
                  "extended": "1"}
        response = requests.get(url, params={**self.params, **params})
        if response.status_code == 200:
            print(f"Фото получены")
        else:
            print("Не удалось получить фото")
        return response.json()
ya_token = str(input("Введите токен Я.Диска >>"))
id = str(input("Введите User ID(Номер или короткое имя)>>"))
vk = VK(access_token)
ya = Yandex(ya_token)
user_info = vk.users_info(id)
user_id = user_info['response'][0]["id"]
folder = f"{user_info['response'][0]['first_name']} {user_info['response'][0]['last_name']}"
ya.create_folder(folder)
info = {}
info[folder] = {"users_photo" : []}
for i in vk.get_photos(user_id)["response"]["items"]:
    url = i["sizes"][-1]["url"]
    type = i["sizes"][-1]["type"]
    date = i["date"]
    likes = i["likes"]["count"]
    info[folder]["users_photo"].append({
        "file_name": f"{likes}_{date}",
        "size": type
    })
    res = ya.upload_files(f"{folder}/{likes}_{date}", url)

with open("user_info.json", "wt", encoding="utf-8") as file:
    json.dump(info, file, ensure_ascii= False, indent= 2)
ya.upload_info_to_disk("user_info.json", f"{folder}/{folder} info.json")
