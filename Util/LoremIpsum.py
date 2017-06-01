from random import shuffle

class LoremIpsum(object):
    text = "Lorem ipsum dolor sit amet consectetur adipisici elit sed eiusmod tempor incidunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat quis aute iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint obcaecat cupiditat non proident sunt in culpa qui officia deserunt mollit anim id est laborum"
    words = text.split(" ")
    max_length = len(words)

    @staticmethod
    def word_list(length):
        return LoremIpsum.words[0:length]

    @staticmethod
    def random_word_list(length):
        words = LoremIpsum.words
        shuffle(words)
        return words[0:length]

    @staticmethod
    def random_words(length):
        words = LoremIpsum.random_word_list(length)
        return " ".join(words)
