import json

def create_json():
    json_str = {}

    file1 = open('D:/Dracula/Dracula2/info/location_names_eng.txt', 'r')
    Lines = file1.readlines()

    count = 0
    for line in Lines:
        number = line.split()[0]
        name = line.replace(number + "\t", "").replace("\n", "")
        json_str[str(count)] = {"name": name}
        count += 1

    file2 = open('D:/Dracula/Dracula2/info/location_points.txt', 'r')
    Lines = file2.readlines()
    count = 0
    for line in Lines:
        x, y = line.split(" ")[:-1]
        json_str[str(count)]["coor"] = [float(x), float(y)]
        count += 1

    file3 = open('D:/Dracula/Dracula2/info/land_param.txt', 'r')
    Lines = file3.readlines()
    count = 0
    for line in Lines:
        num, isWest, isCity, isPort = line.split(" ")
        isPort = isPort.replace("/n", "")
        json_str[num]["isCity"] = True if isCity == "1" else False
        json_str[num]["isPort"] = True if isPort == "1" else False
        json_str[num]["isWest"] = True if isWest == "1" else False
        json_str[num]["isSea"] = False if int(num) <= 60 else True
        count += 1

    for i in range(61, 71):
        json_str[str(i)]["isCity"] = False
        json_str[str(i)]["isPort"] = False
        json_str[str(i)]["isSea"] = True
    print(json_str)

    file_roads_seas = open('D:/Dracula/Dracula Game/obj_coor/roads_seas.txt', 'r')
    lines = file_roads_seas.readlines()
    for line in lines:
        locations = line.split(" ")
        locations[-1] = locations[-1].replace("\n", "")
        print("file_roads_seas:", locations)
        num = str(locations[0])
        if int(num) > 60:
            json_str[num]["seas"] = locations[1:]
            json_str[num]["roads"] = []
            json_str[num]["railways"] = []
        else:
            print("locations = ", locations)
            roads = [loc for loc in locations[1:] if int(loc) <= 60 ]
            seas = [loc for loc in locations[1:] if int(loc) > 60 ]
            json_str[num]["roads"] = roads
            json_str[num]["seas"] = seas

    file_railways = open('D:/Dracula/Dracula Game/obj_coor/railway.txt', 'r')
    lines = file_railways.readlines()
    for line in lines:
        locations = line.split(" ")
        locations[-1] = locations[-1].replace("\n", "")
        print("file_railways:", locations)
        num = str(locations[0])
        json_str[num]["railways"] = locations[1:]

    json.dump(json_str, open("./game/info/locations.json", 'w'), indent=4)
