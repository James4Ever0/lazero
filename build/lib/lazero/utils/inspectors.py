def inspectObject(obj):
    keys = dir(obj)
    if "__dict__" in keys:
        import pprint
        pprint.pprint(vars(obj))
    else:
        for key in keys:
            code = "obj.{}".format(key)
            try:
                subObj = eval(code)
                print(code, subObj)
            except:
                import traceback
                traceback.print_exc()
                print("ERROR WHEN PRINTING {}".format(code))
            print("_"*30)
