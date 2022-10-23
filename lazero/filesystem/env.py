
def getHomeDirectory():
    # https://pythonguides.com/get-current-directory-python/#:~:text=Get%20current%20directory%20Python%201%20To%20get%20the,can%20use%20another%20function%20called%20basename%20from%20os.path.
    return os.path.expanduser("~")  # well we borrow this from web.
