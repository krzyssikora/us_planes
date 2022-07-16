from googlesearch import search
from bs4 import BeautifulSoup
import requests
import re
import csv


def generate_results(url, pattern='passenger'):
    thepage = requests.get(url, headers={'User-agent': 'your bot 0.1'})
    if thepage.status_code == 429:
        print(thepage.headers)
        quit()
    # thepage = requests.get(url)
    # thepage = urllib.urlopen(url)
    soup = BeautifulSoup(thepage.content, "html.parser")
    page_content = str(soup.contents).replace('\n', '')
    matches = re.finditer(pattern, page_content)
    total_length = len(page_content)
    for m in matches:
        start = max(0, m.start() - 80)
        end = min(m.end() + 70, total_length)
        yield page_content[start: end]


def get_models(file='planes_models.txt'):
    with open(file) as f:
        lines = f.readlines()
    return [line.strip('\n') for line in lines]


def run_query(plane_model='737-236'):
    query = '{} plane passenger capacity'.format(plane_model)
    for url in search(query, stop=1):
        infos = generate_results(url)
        idx = 0
        which = None
        infos_list = list()
        while True:
            info = next(infos, None)
            if info is None:
                if idx == 0:
                    return None
                while True:
                    choice = input('Make your choice from 0 to {}'.format(idx - 1))
                    if choice.isdigit():
                        choice = int(choice)
                        if 0 <= choice < idx:
                            which = choice
                            break
                break
            infos_list.append(info)
            print(str(idx).rjust(3) + ': ...' + info + '...', end='')
            ch = input()
            if ch == 'q' or ch == 'Q':
                break
            elif ch.isdigit():
                which = int(ch)
                if which <= idx:
                    break
            idx += 1
        if which is not None:
            chosen_info = infos_list[which]
            digits = re.findall(r'(\d+)', chosen_info)
            values = [int(value) for value in digits]
            if len(values) == 1:
                return values[0]
            else:
                max_len = max(len(str(x)) for x in values)
                while True:
                    print(chosen_info)
                    print('|'.join(str(value).rjust(max_len) for value in range(len(values))))
                    print('|'.join(str(value).rjust(max_len) for value in values))
                    choice = input('which one?')
                    if choice.isdigit():
                        choice = int(choice)
                        if 0 <= choice < len(values):
                            break
                return values[choice]
    return None


def find_models_capacity():
    models = get_models()
    for model in models:
        print('>>>>> model: {}'.format(model))
        capacity = run_query(model)
        with open('models_capacities.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([model, capacity])


def main():
   find_models_capacity()




if __name__ == '__main__':
    main()

# for url in search(query, stop=1):
#     thepage = requests.get(url)
#     text = thepage.text
