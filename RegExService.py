import re


def getData(fileName):
    f = open(fileName, "r")
    content = f.read()
    # optimalValue = re.search("Optimal value: (\d+)", content, re.MULTILINE)
    # if(optimalValue != None):
    #     optimalValue = optimalValue.group(1)
    # else:
    #     optimalValue = re.search("Best value: (\d+)", content, re.MULTILINE)
    #     if(optimalValue != None):
    #         optimalValue = optimalValue.group(1)
    # TODO coords = re.findall(r"^(\d+) (\-*\d+) (\-*\d+)$", content, re.MULTILINE)
    coords = re.findall(r"(\d+)\t(\d+.*d*)\t(\d+.*d*)",
                        content, re.MULTILINE)
    print(coords)

    # TODO print(coords)
    # TODO coords = {int(a): (int(b), int(c)) for a, b, c in coords}
    coords = {int(a): (float(b), float(c)) for a, b, c in coords}

    print(coords)

    # optimalValue = int(optimalValue)
    return coords
