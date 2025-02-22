import os
import base64
import emoji
import yaml
import requests


def main():
    docversion = os.environ["INPUT_DOCVERSION"]
    apikey = os.environ["INPUT_APIKEY"]
    category_id = os.environ["INPUT_CATEGORYID"]
    settings_path = os.environ["INPUT_SETTINGSPATH"]
    changed_files = os.environ["INPUT_CHANGEDFILES"]

    apikey_changed = apikey+":"
    b64_apikey = base64.b64encode(
        apikey_changed.encode("utf-8")).decode("utf-8")

    # if settings path option is used

    # getting all the source paths to read markdown
    try:
        with open(settings_path, "r") as file:
            try:
                md = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)
    except Exception as e:
        print(e)
        exit(1)

    # if changed files are provided only upload changed docs and not all.
    if changed_files:
        changed_files_list = changed_files.split(";")

        matched_docs = 0

        for integration, value in md.items():
            if value['source'] in changed_files_list:
                matched_docs += 1
                print(f"Docs for {integration} were changed.")
                path = value['source']
                slug = value['slug']

                try:
                    with open(path, "r") as markdown:
                        integration_doc = markdown.read()
                except Exception as e:
                    print(e)

                url = f"https://dash.readme.com/api/v1/docs/{slug}"

                headers = {
                    "Accept": "application/json",
                    "x-readme-version": docversion,
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {b64_apikey}"
                }

                payload = {
                    "hidden": True,
                    "catgory": category_id,
                    "order": 999,
                    "body": integration_doc

                }

                response = requests.put(url, json=payload, headers=headers)

                if response.status_code != 200:
                    print(response.text)
                    exit(1)
                elif response.status_code == 200:
                    print(emoji.emojize(
                        f"Docs for {integration} were updated successfully! :rocket:"))

        if matched_docs == 0:
            print(
                f"None of the changed files are docs. Please check your settings file: {settings_path}")

    # otherwise update all docs.
    else:
        print(emoji.emojize(f"Found {len(md.keys())} doc files"))

        # updating all docs for named slugs. all assumed to be in same category
        for integration, value in md.items():
            print(integration, ": ",
                  value['source'], "| slug: ", value['slug'])
            path = value['source']
            slug = value['slug']

            try:
                with open(path, "r") as markdown:
                    integration_doc = markdown.read()
            except Exception as e:
                print(e)

            url = f"https://dash.readme.com/api/v1/docs/{slug}"

            headers = {
                "Accept": "application/json",
                "x-readme-version": docversion,
                "Content-Type": "application/json",
                "Authorization": f"Basic {b64_apikey}"
            }

            payload = {
                "hidden": True,
                "catgory": category_id,
                "order": 999,
                "body": integration_doc

            }

            response = requests.put(url, json=payload, headers=headers)

            if response.status_code != 200:
                print(response.text)
                exit(1)
            elif response.status_code == 200:
                print(emoji.emojize(
                    f"Docs for {integration} updated successfully! :rocket:"))


if __name__ == "__main__":
    main()
