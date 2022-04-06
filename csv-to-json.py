import json

with open("datasets/vigilante-pw.csv", "r") as f:
    json_data = []
    data = f.read().splitlines()
    firstline = True
    for line in data:
        if firstline:
            firstline = False
            continue
        entry = {}
        line = line.split(",")
        entry["record_count"] = line[0]
        entry["dump_name"] = line[1]
        entry["hashing_algorithm"] = line[2]
        entry["category"] = line[3]
        entry["breach_date"] = line[4]
        entry["info"] = line[5]
        entry["source"] = "Vigilante.pw"
        json_data.append(entry)

with open("datasets/vigilante-pw.json","w") as out:
    json.dump(json_data, out)