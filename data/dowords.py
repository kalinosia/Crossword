def listToString(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele

        # return string
    return str1

########################################################

f = open("words3.txt", "a")

with open('forwords3.txt',encoding="utf-8") as file:

    #data = file.read()
    for line in file:

        # reading each word
        for word in line.split():
            # displaying the words
            print(word)
            slowo=[]
            for letter in word:
                if letter == '=':
                    f.write(listToString(slowo))
                    f.write("\n")
                    break
                slowo.append(letter)


f.close()