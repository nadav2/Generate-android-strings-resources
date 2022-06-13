import os
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
    new_string = string_res

    translate_map = {}
    threads = []

    for line in string_res.split("\n"):
        if 'translatable="false"' in line.replace(" ", ""):
            continue

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


def generate_resurces(string_res: str, langs: list[str]):
    if os.path.exists(string_res):
        with open(string_res, "r") as f:
            string_res = f.read()

    for lang in langs:
        new_string = translate_string(string_res, lang)

        os.mkdir(f"values-{lang}")
        with open(f"values-{lang}/strings.xml", "w") as f:
            f.write(new_string)


if __name__ == '__main__':
    generate_resurces(example, ["iw", "fr"])
