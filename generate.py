import requests
import yaml
import json
import hashlib
from os import path
from datetime import datetime


LANGUAGE_SPEC = 'https://raw.githubusercontent.com/github/linguist' \
    '/master/lib/linguist/languages.yml'

OUTPUT_DIR = 'data'

CHECKSUM_FILE = f'{OUTPUT_DIR}/checksums.json'


def request_spec() -> str:
    res = requests.get(LANGUAGE_SPEC, data='str')
    res.raise_for_status()
    return res.text


def parse_spec(v: str) -> dict:
    return yaml.load(v, Loader=yaml.Loader)


def get_checksum(v: str) -> str:
    return hashlib.md5(v.encode()).hexdigest()


def compare_checksum(checksum: str) -> bool:
    checksums = {}
    if path.isfile(CHECKSUM_FILE):
        with open(CHECKSUM_FILE, 'r') as f:
            checksums = json.load(f)
    equals = checksums.get('spec') == checksum
    checksums['spec'] = checksum
    with open(CHECKSUM_FILE, 'w') as f:
        json.dump(checksums, f, indent=2)
    return equals


def to_json_file(filename: str, data: any, minified=True):
    with open(filename, 'w') as f:
        json.dump(data, f,
                  indent=None if minified else 2,
                  separators=(',', ':') if minified else None)


def drizzle_spec(spec: dict) -> dict:
    alias_spec = {}
    for k, v in spec.items():
        k = k.lower()
        aliases = v.pop('aliases') if 'aliases' in v else None
        alias_spec[k] = v
        if aliases:
            for a in list(aliases):
                alias_spec[a] = v
    return alias_spec


def to_css_file(filename: str, spec: dict, classname: str, property: str):
    with open(filename, 'w', encoding="utf-8") as f:
        for k, v in spec.items():
            color = v.get("color")
            if not color:
                continue
            f.write(f".{classname}[srclang=\"{k}\"]"
                    f"{{{property}:{color};}}\n")


def generate_static_files(spec: dict, checksum: str):
    languages = '/languages.json'
    languages_minified = '/languages.minified.json'
    languages_bg_css = '/languages.bg.css'
    languages_fg_css = '/languages.fg.css'
    checksums = '/checksums.json'

    to_json_file(f'{OUTPUT_DIR}{languages}', spec, minified=False)
    to_json_file(f'{OUTPUT_DIR}{languages_minified}', spec, minified=True)
    to_css_file(f'{OUTPUT_DIR}{languages_bg_css}',
                spec, 'lang-color-bg', 'background-color')
    to_css_file(f'{OUTPUT_DIR}{languages_fg_css}',
                spec, 'lang-color-fg', 'color')

    content = f"""
    <html>
        <head>
        </head>
        <body>
            <h1>Endpoints</h1>
            <h2>JSON</h2>
            <ul>
                <li>
                    <a href="{languages}">{languages}</a>
                </li>
                <li>
                    <a href="{languages_minified}">{languages_minified}</a>
                </li>
                <li>
                    <a href="{checksums}">{checksums}</a>
                </li>
            </ul>
            <h2>CSS</h2>
            <ul>
                <li>
                    <a href="{languages_bg_css}">{languages_bg_css}</a>
                </li>
                <li>
                    <a href="{languages_fg_css}">{languages_fg_css}</a>
                </li>
            </ul>
            <hr />
            <i>
                Generated on:&nbsp;
                {datetime.now().strftime("%d/%m/%Y %H:%M:%S %Z")}
            </i><br />
            <i>Checksum: {checksum}</i><br />
            <i>Source: <a href="{LANGUAGE_SPEC}">{LANGUAGE_SPEC}</a></i>
        </body>
    </html>
    """.strip().replace('    ', '').replace('\n', '')

    with open(f'{OUTPUT_DIR}/index.html', 'w') as f:
        f.write(content)


def main():
    spec_raw = request_spec()
    checksum = get_checksum(spec_raw)
    if compare_checksum(checksum):
        print('Skip because checksums match')
        return
    spec = drizzle_spec(parse_spec(spec_raw))
    generate_static_files(spec, checksum)
    print('Updated files')


if __name__ == '__main__':
    main()
