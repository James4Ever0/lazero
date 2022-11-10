from reloading import reloading
import json


@reloading
def jsonWalk(jsonObj, location=[]):
    # this is not tuple. better convert it first?
    # mlocation = copy.deepcopy(location)
    if type(jsonObj) == dict:
        for key in jsonObj:
            content = jsonObj[key]
            if type(content) not in [dict, list, tuple]:
                yield location + [key], content
            else:
                # you really ok with this?
                for mkey, mcontent in jsonWalk(content, location + [key]):
                    yield mkey, mcontent
    elif type(jsonObj) in [
        list,
        tuple,
    ]:  # this is not pure JSON. we only have list and dicts.
        for key, content in enumerate(jsonObj):
            # content = jsonObj[key]
            if type(content) not in [dict, list, tuple]:
                yield location + [key], content
            else:
                for mkey, mcontent in jsonWalk(content, location + [key]):
                    yield mkey, mcontent
    else:
        raise Exception("Not a JSON compatible object: {}".format(type(jsonObj)))


@reloading
def jsonWalk2(jsonObj):
    jsonObj = jsonify(jsonObj)
    return jsonWalk(jsonObj)


@reloading
def jsonLocate(jsonObj, location=[]):
    # print("object:",jsonObj)
    # print("location:",location)
    if location != []:
        # try:
        return jsonLocate(jsonObj[location[0]], location[1:])
        # except:
        #     breakpoint()
    return jsonObj


@reloading
def jsonUpdate(jsonObj, location=[], update_content=None):
    if location != []:
        if type(jsonObj) == dict:
            target = {
                location[0]: jsonUpdate(
                    jsonObj[location[0]],
                    location=location[1:],
                    update_content=update_content,
                )
            }
            # print("keys:", location)
            # print("JSONOBJ:", jsonObj)
            # print("update target:", target)
            jsonObj.update(target)
            return jsonObj
        elif type(jsonObj) == list:
            target = jsonUpdate(
                jsonObj[location[0]],
                location=location[1:],
                update_content=update_content,
            )
            # print("keys:", location)
            # print("JSONOBJ:", jsonObj)
            # print("override target:", target)
            jsonObj[location[0]] = target
            return jsonObj
        else:
            raise Exception("Unsupported JSON update target type:", type(jsonObj))
    return update_content


@reloading
def jsonDeleteObject(jsonObj, location: list):
    assert len(location) > 0
    obj = jsonObj
    # print(location, obj)
    for key in location[:-1]:
        obj = obj[key]
    del obj[location[-1]]
    return jsonObj


# how to reload module directly, so we can include this function as well?
import typing


@reloading
def jsonDeleteAllInstances(jsonObj, isInstance: typing.Callable[[typing.Any], bool]):
    jsonObj2 = jsonObj.copy()
    candidates = []
    for key, value in jsonWalk(jsonObj2):
        if isInstance(value):
            # delete that thing! but how to delete these things once for all?
            candidates.append(key)
    candidates.sort(key=lambda x: -x[-1] if type(x[-1]) == int else 1)
    for candidate in candidates:
        jsonObj2 = jsonDeleteObject(jsonObj, candidate)
    return jsonObj2


@reloading
def jsonify(jsonObj):  # remove ellipsis
    isinstance=lambda
    return json.loads(json.dumps(jsonObj2))
