import requests
import yaml
import json
from datetime import datetime


LANGUAGE_SPEC = 'https://raw.githubusercontent.com/github/linguist' \
    '/master/lib/linguist/languages.yml'

OUTPUT_DIR = 'data'


def request_and_parse_spec() -> dict:
    res = requests.get(LANGUAGE_SPEC, data='str')
    res.raise_for_status()
    return yaml.load(res.text, Loader=yaml.Loader)


def to_json_file(filename: str, data: any, minified=True):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=None if minified else 2)


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


def generate_static_files(spec: dict):
    languages = '/languages.json'
    languages_minified = '/languages.minified.json'

    to_json_file(f'{OUTPUT_DIR}{languages}', spec, minified=False)
    to_json_file(f'{OUTPUT_DIR}{languages_minified}', spec, minified=True)

    content = f"""
    <html>
        <head>
        </head>
        <body>
            <h1>Endpoints</h1>
            <ul>
                <li>
                    <a href="{languages}">{languages}</a>
                </li>
                <li>
                    <a href="{languages_minified}">{languages_minified}</a>
                </li>
            </ul>
            <hr />
            <i>
                Generated on:&nbsp;
                {datetime.now().strftime("%d/%m/%Y %H:%M:%S %Z")}
            </i><br />
            <i>Source: <a href="{LANGUAGE_SPEC}">{LANGUAGE_SPEC}</a></i>
        </body>
    </html>
    """.strip().replace('    ', '').replace('\n', '')

    with open(f'{OUTPUT_DIR}/index.html', 'w') as f:
        f.write(content)


def main():
    spec = request_and_parse_spec()
    spec = drizzle_spec(spec)
    generate_static_files(spec)


if __name__ == '__main__':
    main()
