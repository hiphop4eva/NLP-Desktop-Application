import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

stopWords = set(nltk.corpus.stopwords.words("english"))

class nltkProcessor:
    def __init__(self):
        pass

    def processTextInfo(self, text):
        textInfo = {}

        textFilteredMarks = self.filterMarks(text)

        textWordsFilteredMarks = nltk.word_tokenize(textFilteredMarks)
        textWordsFilteredStopWords = []  
        textWordsLemmatized = []
        
        textStopWords = []
        for w in textWordsFilteredMarks:
            if w in stopWords:
                textStopWords.append(w)
            else:
                textWordsFilteredStopWords.append(w)
                textWordsLemmatized.append(nltk.stem.WordNetLemmatizer().lemmatize(w))

        textFinal = textWordsLemmatized

        freqDist = nltk.FreqDist(textWordsFilteredMarks)

        length = len(text.strip(" "))
        wordCount = textWordsFilteredMarks.__len__()
        mostCommonWords = freqDist.most_common(5)
        leastCommonWords = freqDist.most_common()[-5:]

        freqDist = nltk.FreqDist(textStopWords)
        mostCommonStopWords = freqDist.most_common()[5:]

        textInfo["Length"] = length
        textInfo["WordCount"] = wordCount
        textInfo["MostCommonWords"] = mostCommonWords
        textInfo["LeastCommonWords"] = leastCommonWords
        textInfo["MostCommonStopWords"] = mostCommonStopWords
        textInfo["TextFiltered"] = textFinal

        return textInfo
    
    def filterMarks(self, text):
        textFilteredMarks = ""
        spaceMarks = [" ", ".", "/", "(", ")", "[", "]", "{", "}", ",", ";"]
        for c in text:
            if c == "\n":
                textFilteredMarks += "\n"
            elif c in spaceMarks:
                textFilteredMarks += " "
            elif c.isalpha():
                textFilteredMarks += c.lower()
        return textFilteredMarks
    
    def jaccardSimilarity(self, text1, text2):
        textUnion = set(text1 + text2)
        textCommon = [word for word in text1 if word in text2]
        textCommonUnique = set(textCommon)

        jaccardIndex = len(textCommonUnique) / len(textUnion)

        return jaccardIndex
    
    def setFrequency(self, text, freq):
        freq = nltk.FreqDist(text) 

    def customFreqSimilarity(self, text1, text2):
        text1Freq = nltk.FreqDist(text1)
        text2Freq = nltk.FreqDist(text2)

        totalDifference = 0
        totalWordCount = 0
        commonWordCount = 0
        
        for word1 in text1Freq:
            totalWordCount += 1
            freq1 = text1Freq[word1]
            for word2 in text2Freq:
                freq2 = text2Freq[word2]
                if word1 == word2:
                    totalDifference += abs(freq1 - freq2)
                    commonWordCount += 1
                else:
                    totalWordCount += 1

        commonToTotal = commonWordCount / totalWordCount

        difference = 1 / (totalDifference + 1)
        
        value = difference * commonToTotal

        return value
    
    def tfidfSimilarity(self, text1, text2):
        vectorizer = TfidfVectorizer()
        vector1 = vectorizer.fit_transform(text1)
        vector2 = vectorizer.transform(text2)
        
        cosineSimilarity = cosine_similarity(vector1, vector2)

        total = 0
        count = 0
        for i in cosineSimilarity:
            for k in i:
                total += k
                count += 1

        average = total / count

        return average