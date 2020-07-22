'''
WakaTime progress visualizer
copy from https://github.com/athul/waka-readme
'''

import re
import os
import sys
import base64
import datetime
import requests
from github import Github, GithubException

START_COMMENT = '<!--START_SECTION:waka-->'
END_COMMENT = '<!--END_SECTION:waka-->'
listReg = f"{START_COMMENT}[\\s\\S]+{END_COMMENT}"

user = os.getenv('INPUT_USERNAME')
waka_key = os.getenv('INPUT_WAKATIME_API_KEY')
ghtoken = os.getenv('INPUT_GH_TOKEN')
show_title = os.getenv("INPUT_SHOW_TITLE")


def this_week() -> str:
    '''Returns a week streak'''
    week_end = datetime.datetime.today() - datetime.timedelta(days=1)
    week_start = week_end - datetime.timedelta(days=7)
    print("Week header created")
    return f"Week: {week_start.strftime('%d %B, %Y')} - {week_end.strftime('%d %B, %Y')}"


def make_graph(percent: float) -> str:
    '''Make progress graph from API graph'''
    done_block = '█'
    empty_block = '░'
    pc_rnd = round(percent)
    return f"{done_block*int(pc_rnd/4)}{empty_block*int(25-int(pc_rnd/4))}"


def get_stats() -> str:
    '''Gets API data and returns markdown progress'''
    data = requests.get(
        f"https://wakatime.com/api/v1/users/current/stats/last_7_days?api_key={waka_key}").json()

    try:
        lang_data = data['data']['languages']
    except KeyError:
        print("Please Add your WakaTime API Key to the Repository Secrets")
        sys.exit(1)

    data_list = []
    pad = len(max([l['name'] for l in lang_data[:5]], key=len))
    for lang in lang_data[:5]:
        lth = len(lang['name'])
        ln_text = len(lang['text'])
        # following line provides a neat finish
        fmt_percent = format(lang['percent'], '0.2f').zfill(5)
        data_list.append(
            f"{lang['name']}{' '*(pad + 3 - lth)}{lang['text']}{' '*(16 - ln_text)}{make_graph(lang['percent'])}   {fmt_percent} %")
    print("Graph Generated")
    data = ' \n'.join(data_list)
    if show_title == 'true':
        print("Stats with Weeks in Title Generated")
        return '```text\n'+this_week()+'\n\n'+data+'\n```'
    else:
        print("Usual Stats Generated")
        return '```text\n'+data+'\n```'


def decode_readme(data: str) -> str:
    '''Decode the contets of old readme'''
    decoded_bytes = base64.b64decode(data)
    return str(decoded_bytes, 'utf-8')


def generate_new_readme(stats: str, readme: str) -> str:
    '''Generate a new Readme.md'''
    stats_in_readme = f"{START_COMMENT}\n{stats}\n{END_COMMENT}"
    return re.sub(listReg, stats_in_readme, readme)


if __name__ == '__main__':
    g = Github(ghtoken)
    try:
        repo = g.get_repo(f"{user}/{user}")
    except GithubException:
        print("Authentication Error. Try saving a GitHub Token in your Repo Secrets or Use the GitHub Actions Token, which is automatically used by the action.")
        sys.exit(1)
    contents = repo.get_readme()
    waka_stats = get_stats()
    rdmd = decode_readme(contents.content)
    new_readme = generate_new_readme(stats=waka_stats, readme=rdmd)
    # if new_readme != rdmd:
    #     repo.update_file(path=contents.path, message='Updated with Dev Metrics',
    #                      content=new_readme, sha=contents.sha, branch='master')
    print(new_readme)