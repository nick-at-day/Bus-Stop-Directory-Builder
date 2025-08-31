import os
from itertools import zip_longest
import lorem
import datetime

paragraphs = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Rutrum tellus pellentesque eu tincidunt tortor aliquam nulla. Massa sed elementum tempus egestas. Aliquet risus feugiat in ante metus. Donec pretium vulputate sapien nec sagitt",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Rutrum tellus pellentesque eu tincidunt tortor aliquam nulla. Massa sed elementum tempus egestas. Aliquet risus feugiat in ante metus. Donec pretium vulputate sapien nec sagitt",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Rutrum tellus pellentesque eu tincidunt tortor aliquam nulla. Massa sed elementum tempus egestas. Aliquet risus feugiat in ante metus. Donec pretium vulputate sapien nec sagitt",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Rutrum tellus pellentesque eu tincidunt tortor aliquam nulla. Massa sed elementum tempus egestas. Aliquet risus feugiat in ante metus. Donec pretium vulputate sapien nec sagitt",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Rutrum tellus pellentesque eu tincidunt tortor aliquam nulla. Massa sed elementum tempus egestas. Aliquet risus feugiat in ante metus. Donec pretium vulputate sapien nec sagitt",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Rutrum tellus pellentesque eu tincidunt tortor aliquam nulla. Massa sed elementum tempus egestas. Aliquet risus feugiat in ante metus. Donec pretium vulputate sapien nec sagitt",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Rutrum tellus pellentesque eu tincidunt tortor aliquam nulla. Massa sed elementum tempus egestas. Aliquet risus feugiat in ante metus. Donec pretium vulputate sapien nec sagitt",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Rutrum tellus pellentesque eu tincidunt tortor aliquam nulla. Massa sed elementum tempus egestas. Aliquet risus feugiat in ante metus. Donec pretium vulputate sapien nec sagitt",
]
stops = [
    "1234",
    "14234",
    "1234534",
    "1234534",
    "1234534",
    "1234534",
    "5234",
]



with open("testOutput.txt", "w") as f:
    f.write(f"This is the output\n\n")
    for a,b in zip_longest(paragraphs, stops, fillvalue=""):
        if a:
            f.write(str(a) + "\n\n")
        if b:
            f.write(str(b) + "\n\n")

now = datetime.datetime.now()  
nowString = f"{now.year}-{now.month}-{now.day} {now.hour}{now.minute}-{now.second}"
print(nowString)