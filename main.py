import os
import shutil
import threading

import deep_translator

example = """
<resources>
    <string name="app_name" translatable="false">Python controller</string>
    <string name="app_name1">Python controller</string>
    <string name="connected">Connected</string>
    <string name="disconnected">Disconnected</string>
    <string name="send_command">Send Command</string>
    <string name="output">The output will be displayed here</string>
    <string name="documentation">Documentation</string>
    <string name="doc_title">Documentation</string>
    <string name="home">Home</string>
    <string name="pc_version">PC Version</string>
    <string name="to_send_command_to_your_computer_first_scan_the_qr_code_that_appears_in_the_computer_s_app">To Send command to your computer first scan the QR code that appears in the computer\'s app.</string>
    <string name="connect_code">Connect Code</string>
    <string name="or_enter_the_code_manually_below">Or enter the code manually below:</string>
    <string name="connect">Connect</string>
    <string name="connect_to_your_device">Connect to your device</string>
</resources>
"""



def google_translate(text, from_lang, to_lang, mp):
    new_lang = deep_translator.GoogleTranslator(source=from_lang, target=to_lang).translate(text)
    if to_lang == "iw" or to_lang == "hebrew":
        new_lang = remove_nikkud(new_lang)
    mp[text] = new_lang


def translate_string(string_res, lang):

    string_res = "\n".join([line for line in string_res.split("\n") if 'translatable="false"' not in line.replace(" ", "")])

    new_string = string_res

    translate_map = {}
    threads = []

    for line in string_res.split("\n"):

        if len(line) > 0:
            content = line.split("</string>")[0].split(">")[1]
            if content.strip():
                t1 = threading.Thread(target=lambda: google_translate(content, 'auto', lang, translate_map), daemon=True)
                t1.start()
                threads.append(t1)

    for t in threads:
        t.join()

    for key, value in translate_map.items():
        new_string = new_string.replace(f">{key}</string>", f">{value}</string>")

    return new_string


def remove_nikkud(s: str):
    return ''.join(['' if 1456 <= ord(c) <= 1479 else c for c in s])


# string_res can be a string, file path or android studio project
def generate_resurces(string_res: str, langs: list[str]):
    country_to_code = {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy',
                       'azerbaijani': 'az', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bosnian': 'bs',
                       'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny',
                       'chinese (simplified)': 'zh-CN', 'chinese (traditional)': 'zh-TW', 'corsican': 'co',
                       'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dutch': 'nl', 'english': 'en',
                       'esperanto': 'eo', 'estonian': 'et', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr',
                       'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el',
                       'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'iw',
                       'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig',
                       'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw',
                       'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'kinyarwanda': 'rw', 'korean': 'ko',
                       'kurdish': 'ku', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lithuanian': 'lt',
                       'luxembourgish': 'lb', 'macedonian': 'mk', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml',
                       'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'mongolian': 'mn', 'myanmar': 'my',
                       'nepali': 'ne', 'norwegian': 'no', 'odia': 'or', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl',
                       'portuguese': 'pt', 'punjabi': 'pa', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm',
                       'scots gaelic': 'gd', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd',
                       'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es',
                       'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'tatar': 'tt',
                       'telugu': 'te', 'thai': 'th', 'turkish': 'tr', 'turkmen': 'tk', 'ukrainian': 'uk', 'urdu': 'ur',
                       'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi',
                       'yoruba': 'yo', 'zulu': 'zu'}

    for lang in langs:
        if lang not in country_to_code.keys() and lang not in country_to_code.values():
            print(f"{lang} is not a valid language")
            return

    android_studio_path = os.path.expanduser("~/StudioProjects")
    path = f"{android_studio_path}/{string_res}/app/src/main/res"

    is_app = os.path.isfile(f"{path}/values/strings.xml")

    if os.path.isfile(string_res):
        with open(string_res, "r") as f:
            string_res = f.read()
    elif is_app:
        with open(f"{path}/values/strings.xml", "r") as f:
            string_res = f.read()

    for lang in langs:
        lang = country_to_code.get(lang, lang)
        new_string = translate_string(string_res, lang)

        if is_app:

            if os.path.isdir(f"{path}/values-{lang}"):
                res = input(f"Overwrite existing values-{lang}? (y/n) - ")
                if res.lower() == "y" or res.lower() == "yes":
                    shutil.rmtree(f"{path}/values-{lang}")
                else:
                    print("The operation was canceled.")
                    return

            os.mkdir(f"{path}/values-{lang}")
            with open(f"{path}/values-{lang}/strings.xml", "w") as f:
                f.write(new_string)

        else:
            if os.path.isdir(f"values-{lang}"):
                shutil.rmtree(f"values-{lang}")

            os.mkdir(f"values-{lang}")
            with open(f"values-{lang}/strings.xml", "w") as f:
                f.write(new_string)

        print("Done generating resources for " + lang)


if __name__ == '__main__':
    generate_resurces(example, ["german"])
