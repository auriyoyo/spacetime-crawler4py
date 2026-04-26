from collections import defaultdict
import json

# word_counts is a dictionary that maps words to their counts.
# Used in scraper to record the number of times each word appears in the pages we crawl.
word_counts = defaultdict(int)

# STOP_WORDS is a set of common English words that will be ignored when counting word frequencies.
STOP_WORDS = {
    "a", "able", "about", "above", "abst", "accordance", "according",
    "accordingly", "across", "act", "actually", "added", "adj", "affected",
    "affecting", "affects", "after", "afterwards", "again", "against", "ah",
    "all", "almost", "alone", "along", "already", "also", "although",
    "always", "am", "among", "amongst", "an", "and", "announce", "another",
    "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway",
    "anyways", "anywhere", "apparently", "approximately", "are", "aren",
    "arent", "arise", "around", "as", "aside", "ask", "asking", "at", "auth",
    "available", "away", "awfully", "b", "back", "be", "became", "because",
    "become", "becomes", "becoming", "been", "before", "beforehand", "begin",
    "beginning", "beginnings", "begins", "behind", "being", "believe",
    "below", "beside", "besides", "between", "beyond", "biol", "both",
    "brief", "briefly", "but", "by", "c", "ca", "came", "can", "cannot",
    "can't", "cause", "causes", "certain", "certainly", "co", "com", "come",
    "comes", "contain", "containing", "contains", "could", "couldnt", "d",
    "date", "did", "didn't", "different", "do", "does", "doesn't", "doing",
    "done", "don't", "down", "downwards", "due", "during", "e", "each", "ed",
    "edu", "effect", "eg", "eight", "eighty", "either", "else", "elsewhere",
    "end", "ending", "enough", "especially", "et", "et-al", "etc", "even",
    "ever", "every", "everybody", "everyone", "everything", "everywhere",
    "ex", "except", "f", "far", "few", "ff", "fifth", "first", "five", "fix",
    "followed", "following", "follows", "for", "former", "formerly", "forth",
    "found", "four", "from", "further", "furthermore", "g", "gave", "get",
    "gets", "getting", "give", "given", "gives", "giving", "go", "goes",
    "gone", "got", "gotten", "h", "had", "happens", "hardly", "has",
    "hasn't", "have", "haven't", "having", "he", "hed", "hence", "her",
    "here", "hereafter", "hereby", "herein", "heres", "hereupon", "hers",
    "herself", "hes", "hi", "hid", "him", "himself", "his", "hither", "home",
    "how", "howbeit", "however", "hundred", "i", "id", "ie", "if", "i'll",
    "im", "immediate", "immediately", "importance", "important", "in", "inc",
    "indeed", "index", "information", "instead", "into", "invention",
    "inward", "is", "isn't", "it", "itd", "it'll", "its", "itself", "i've",
    "j", "just", "k", "keep", "keeps", "kept", "kg", "km", "know", "known",
    "knows", "l", "largely", "last", "lately", "later", "latter", "latterly",
    "least", "less", "lest", "let", "lets", "like", "liked", "likely",
    "line", "little", "ll", "look", "looking", "looks", "ltd", "m", "made",
    "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means",
    "meantime", "meanwhile", "merely", "mg", "might", "million", "miss",
    "ml", "more", "moreover", "most", "mostly", "mr", "mrs", "much", "mug",
    "must", "my", "myself", "n", "na", "name", "namely", "nay", "nd",
    "near", "nearly", "necessarily", "necessary", "need", "needs", "neither",
    "never", "nevertheless", "new", "next", "nine", "ninety", "no", "nobody",
    "non", "none", "nonetheless", "noone", "nor", "normally", "nos", "not",
    "noted", "nothing", "now", "nowhere", "o", "obtain", "obtained",
    "obviously", "of", "off", "often", "oh", "ok", "okay", "old", "omitted",
    "on", "once", "one", "ones", "only", "onto", "or", "ord", "other",
    "others", "otherwise", "ought", "our", "ours", "ourselves", "out",
    "outside", "over", "overall", "owing", "own", "p", "page", "pages",
    "part", "particular", "particularly", "past", "per", "perhaps", "placed",
    "please", "plus", "poorly", "possible", "possibly", "potentially", "pp",
    "predominantly", "present", "previously", "primarily", "probably",
    "promptly", "proud", "provides", "put", "q", "que", "quickly", "quite",
    "qv", "r", "ran", "rather", "rd", "re", "readily", "really", "recent",
    "recently", "ref", "refs", "regarding", "regardless", "regards",
    "related", "relatively", "research", "respectively", "resulted",
    "resulting", "results", "right", "run", "s", "said", "same", "saw",
    "say", "saying", "says", "sec", "section", "see", "seeing", "seem",
    "seemed", "seeming", "seems", "seen", "self", "selves", "sent", "seven",
    "several", "shall", "she", "shed", "she'll", "shes", "should",
    "shouldn't", "show", "showed", "shown", "showns", "shows", "significant",
    "significantly", "similar", "similarly", "since", "six", "slightly", "so",
    "some", "somebody", "somehow", "someone", "somethan", "something",
    "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry",
    "specifically", "specified", "specify", "specifying", "still", "stop",
    "strongly", "sub", "substantially", "successfully", "such", "sufficiently",
    "suggest", "sup", "sure", "t", "take", "taken", "taking", "tell",
    "tends", "th", "than", "thank", "thanks", "thanx", "that", "that'll",
    "thats", "that've", "the", "their", "theirs", "them", "themselves",
    "then", "thence", "there", "thereafter", "thereby", "thered", "therefore",
    "therein", "there'll", "thereof", "therere", "theres", "thereto",
    "thereup", "there've", "these", "they", "theyd", "they'll", "theyre",
    "they've", "think", "this", "those", "thou", "though", "thoughh",
    "thousand", "throug", "through", "throughout", "thru", "thus", "til",
    "tip", "to", "together", "too", "took", "toward", "towards", "tried",
    "tries", "truly", "try", "trying", "ts", "twice", "two", "u", "under",
    "unfortunately", "unless", "unlike", "unlikely", "until", "unto", "up",
    "upon", "ups", "us", "use", "used", "useful", "usefully", "usefulness",
    "uses", "using", "usually", "v", "value", "various", "ve", "very", "via",
    "viz", "vol", "vols", "vs", "w", "want", "wants", "was", "wasnt", "way",
    "we", "wed", "welcome", "we'll", "went", "were", "werent", "we've",
    "what", "whatever", "what'll", "whats", "when", "whence", "whenever",
    "where", "whereafter", "whereas", "whereby", "wherein", "wheres",
    "whereupon", "wherever", "whether", "which", "while", "whim", "whither",
    "who", "whod", "whoever", "whole", "who'll", "whom", "whomever", "whos",
    "whose", "why", "widely", "willing", "wish", "with", "within", "without",
    "wont", "words", "world", "would", "wouldnt", "www", "x", "y", "yes",
    "yet", "you", "youd", "you'll", "your", "youre", "yours", "yourself",
    "yourselves", "you've", "z", "zero"
}


# update_word_counts takes a list of words and updates the global word_counts dictionary with the counts of each word.
def update_word_counts(words):
    for word in words:
        word_counts[word] += 1


# tokenize takes a string of text and returns a list of words.
def tokenize(text):
    results_list = []
    buffer = ""
    for character in text:
        try:
            if character.isascii() and character.isalnum():
                buffer += character.lower()
            else:
                if buffer != "":
                    results_list.append(buffer)
                    buffer = ""
        except UnicodeDecodeError:
            continue
    if buffer != "":
        results_list.append(buffer)
        buffer = ""
    return results_list


# load_word_counts loads the word counts from a JSON file into the global word_counts dictionary.
def load_word_counts(filepath="word_counts.json"):
    global word_counts
    try:
        with open(filepath, "r") as f:
            word_counts = defaultdict(int, json.load(f))
    except FileNotFoundError:
        pass


# save_word_counts saves the current word counts to a JSON file.
def save_word_counts(filepath="word_counts.json"):
    with open(filepath, "w") as f:
        json.dump(dict(word_counts), f)


# get_top_50 returns a list of the top 50 most common words and their counts, sorted by count in descending order.
def get_top_50():
    return sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:50]


# save_top_50 saves the top 50 most common words and their counts to a text file.
def save_top_50(filepath="top_50.txt"):
    top_50 = get_top_50()
    with open(filepath, "w") as f:
        for word, count in top_50:
            f.write(f"{word}: {count}\n")


# longest_page is a dictionary that keeps track of the url that contains the most words and the word count of that page. 
longest_page = {"url": "", "count": 0}


# update_longest_page takes a url and a word count and updates longest_page
def update_longest_page(url, word_count):
    if word_count > longest_page["count"]:
        longest_page["url"] = url
        longest_page["count"] = word_count


# save_longest_page saves the longest page information to a text file
def save_longest_page(filepath="longest_page.txt"):
    with open(filepath, "w") as f:
        f.write(f"URL: {longest_page['url']}\n")
        f.write(f"Word Count: {longest_page['count']}\n")


# save_all saves both the word counts and the top 50 words to their respective files.
def save_all(filepath_counts="word_counts.json", filepath_top50="top_50.txt"):
    save_word_counts(filepath_counts)
    save_top_50(filepath_top50)
    save_longest_page()