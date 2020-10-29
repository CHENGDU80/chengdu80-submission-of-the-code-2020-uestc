import os

newsdir = r'C:\Users\Administrator\Desktop\filtered_news'

for root, dirs, files in os.walk(newsdir):
    for file in files:
        new_name = file[11:]
        try:
            os.rename(os.path.join(root, file), os.path.join(root, new_name))
        except:
            os.remove(os.path.join(root, file))