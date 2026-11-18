import json
import os
import re
import urllib.parse
import urllib.request
from xml.sax.saxutils import escape

SERVER = os.environ["TA_SERVER"]
TOKEN = os.environ["TA_TOKEN"]
MEDIA_FOLDER = os.environ["TA_MEDIA_FOLDER"]
TARGET_FOLDER = os.environ["TARGET_FOLDER"]


def get(path, **params):
    url = f"{SERVER}/api/{path}/?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"Authorization": f"Token {TOKEN}"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def get_all(path, **params):
    items, page = [], 1
    while True:
        response = get(path, page=page, **params)
        items += response["data"]
        last_page = response["paginate"]["last_page"]
        if not last_page or page >= last_page:
            return items
        page += 1


def urlify(text):
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s]", "", text))


def media_path(media_url):
    return f"{MEDIA_FOLDER}/{media_url.split('/', 3)[3]}"


def link(target, path):
    if not os.path.lexists(path):
        os.symlink(target, path)
        print(f"Linked {path}")


def write_nfo(path, root, fields):
    if os.path.exists(path):
        return
    body = "".join(f"\t<{key}>{escape(value)}</{key}>\n" for key, value in fields.items())
    header = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{header}\n<{root}>\n{body}</{root}>\n")
    print(f"Wrote {path}")


def existing_folders():
    folders = {}
    for entry in os.scandir(TARGET_FOLDER):
        nfo = os.path.join(entry.path, "tvshow.nfo")
        if entry.is_dir() and os.path.exists(nfo):
            with open(nfo, encoding="utf-8") as f:
                match = re.search(r"<uniqueid>(.*?)</uniqueid>", f.read())
            if match:
                folders.setdefault(match[1], []).append(entry.path)
    return folders


def move_folder(source, destination):
    for name in os.listdir(source):
        if name.endswith(".nfo"):
            os.remove(os.path.join(source, name))
    if not os.path.exists(destination) or os.path.samefile(source, destination):
        os.rename(source, destination)
    else:
        for name in os.listdir(source):
            path = os.path.join(source, name)
            if os.path.lexists(os.path.join(destination, name)):
                os.remove(path)
            else:
                os.rename(path, os.path.join(destination, name))
        os.rmdir(source)
    print(f"Moved {source} to {destination}")


def sync():
    folders = existing_folders()
    for channel in get_all("channel"):
        name = urlify(channel["channel_name"]) or channel["channel_id"]
        folder = os.path.join(TARGET_FOLDER, name)
        for old_folder in folders.get(channel["channel_id"], []):
            if os.path.basename(old_folder) != name:
                move_folder(old_folder, folder)
        os.makedirs(folder, exist_ok=True)
        write_nfo(os.path.join(folder, "tvshow.nfo"), "tvshow", {
            "title": channel["channel_name"],
            "showtitle": channel["channel_name"],
            "uniqueid": channel["channel_id"],
            "plot": channel["channel_description"] or "",
            "premiered": channel["channel_last_refresh"][:10],
        })

        for video in get_all("video", channel=channel["channel_id"]):
            stem = os.path.join(
                folder, f"{video['published'][:10]}_{video['youtube_id']}_{urlify(video['title'])}"
            )
            link(media_path(video["media_url"]), f"{stem}.mp4")
            for subtitle in video["subtitles"] or []:
                link(media_path(subtitle["media_url"]), f"{stem}.{subtitle['lang']}.vtt")
            write_nfo(f"{stem}.nfo", "episodedetails", {
                "title": video["title"],
                "showtitle": channel["channel_name"],
                "uniqueid": video["youtube_id"],
                "plot": video["description"] or "",
                "premiered": video["published"][:10],
            })


def cleanup():
    for root, _, files in os.walk(TARGET_FOLDER):
        for name in files:
            path = os.path.join(root, name)
            if name.endswith(".nfo") and name != "tvshow.nfo":
                stale = not os.path.exists(f"{path[:-4]}.mp4")
            else:
                stale = os.path.islink(path) and not os.path.exists(path)
            if stale:
                os.remove(path)
                print(f"Removed {path}")


sync()
cleanup()
