import json


def save_json(json_name, json_content, indent_number=1):
    with open(json_name + '.json', 'w', encoding='utf-8') as f:
        json.dump(json_content, f, indent=indent_number)
        f.close()


def read_json(json_name):
    with open(json_name + '.json') as json_data:
        data_dict = json.load(json_data)
        return data_dict


def update_entities_json_file(json_name, key, new_value):
    with open(json_name + ".json", "r+") as jsonFile:
        data = json.load(jsonFile)
        for entity in data["intent"]["entities"]:
            if entity["name"] == key:
                tmp = entity["value"]
                entity["value"] = new_value

        jsonFile.seek(0)  # rewind
        json.dump(data, jsonFile, indent=6)
        jsonFile.truncate()
