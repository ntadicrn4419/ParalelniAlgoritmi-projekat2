import multiprocessing.pool
from functools import reduce
import wikipedia
wikipedia.set_lang("sr")

specialCharacters = ['=', '-', ',', '!', '?', '.', '$', '(', ')', '[', ']', ';', '{', '}', '@', '#', '%', '^', '&', '*', '_', '+', '-', '/', '\\', '\'', '"', '<', '>', '|']

#'''Dohvata naslove zahtevanog broja stranica koje se pojavaljuju kao
#  rezultati pretrage za zadatu kljucnu rec'''
def get_pages(query, results=10): #staviti posle results = 50
  titles = wikipedia.search(query, results=results)
  pages = list()
  for title in titles:
      try:
          page = wikipedia.page(title) # ovo su samo naslovi stranica, ako zelimo tekst sa stranice: text = page.content
          data = (query, page)
          pages.append(data)
      except:
          continue
  return pages

def append_list(array, currentElement):
    return array + currentElement

def lower_case(character):
    return str.lower(character)

def remove_special_chars(array, currentChar):
    if currentChar not in specialCharacters:
        return array + list(currentChar)
    else:
        return array

def add_terminator(array, currentChar):
        if currentChar == " " or currentChar == "\n" or currentChar == "\t":
            return array + list("$")
        else:
            return array + list(currentChar)

def reduce_text(args, currentChar):
    array, flag = args
    if flag :
        return (array, flag)
    if len(array) >= 10_000 and currentChar == "$":
        flag = True
    return (array + list(currentChar), flag)


def prepare(args):
    query, string1 = args
    res = map(lower_case, str(string1))
    string2 = reduce(remove_special_chars, list(res), [])
    string3 = reduce(add_terminator, string2, []) #ukoliko imamo u stringu vise povezanih space-eva, stavice za svaki space $, da li je to validno?
    string3.append("$")
    string4, boolean = reduce(reduce_text, string3, ([], False))
    return query, string4

def choose_texts(args, currentElement): #uzima po pet tekstova za svaku kljucnu rec; za sada ne bira nasumicno, nego za svaku kljucnu rec prvih 5 tekstova!
    newArray, text, index, counter = args
    key, currentChar = currentElement
    previousKey, value = text[index-1]
    if key != previousKey:
        counter = 0
    if counter < 5:
        return (newArray + list(currentChar), text, index+1, counter+1)
    else:
        return (newArray, text, index+1, counter+1)

def create_tokens(args, currentChar):
    array, chosenTexts, index = args
    if index == len(chosenTexts)-1 or currentChar == "$":
        return (array, chosenTexts, index+1)
    token = currentChar + chosenTexts[index+1]
    strings = []
    strings.append(token)
    return (array + strings, chosenTexts, index+1)

def create_token_tuples(currentToken):
    return (currentToken, 1)

def reduce_token_tuples(args, currentTokenTuple):
    token, value = currentTokenTuple
    array, previousToken, index = args
    if token != previousToken:
        newTuple = (token, 1)
        helpArray = []
        helpArray.append(newTuple)
        return (array + helpArray, token, index+1)
    else:
        copiedArray = array
        key, num = copiedArray[index]
        copiedArray[index] = (key, int(num)+1)
        return (copiedArray, token, index)

def insert_token(args, currentString):
    array, tokenTuple, tmp, buffer = args
    token, number = tokenTuple
    flag = False
    if (currentString in token): # a,g,e; currentString = ag
        flag = True
        tmp += currentString
    if flag == False:
        array += buffer
    helpArray = []
    if tmp == token:
        helpArray.append(token)
        return (array + helpArray, tokenTuple, "", [])
    helpArray.append(currentString)
    if (flag):
        buffer += helpArray
        return (array, tokenTuple, tmp, buffer)
    else:
        return (array + helpArray, tokenTuple, "", [])
if __name__ == '__main__':
    keywords = ['Beograd', 'Prvi svetski rat', 'Protein', 'Mikroprocesor', 'Stefan Nemanja', 'Košarka']
    pool = multiprocessing.pool.ThreadPool(multiprocessing.cpu_count())
    titlesMatrix = pool.map(get_pages, keywords) #titlesMatrix = map(get_pages, keywords)-> za 2 sekunde sporije od map-a iz pool-a
    titlesList = reduce(append_list, titlesMatrix, [])
    processedText = pool.map(prepare, titlesList)
    returnTuple = reduce(choose_texts, processedText, ([], processedText, 0, 0))#chosenTexts je lista karaktera
    chosenTexts = returnTuple[0]

    currentListOfTokens = []# cemu bi ovo trebalo da sluzi?
    for i in range(5000):
        if i < 100 or i > 4900:
            print(i, chosenTexts)
        returnTuple = reduce(create_tokens, chosenTexts, ([], chosenTexts, 0))# returnTuple je samo promenljiva u koju pakujem povratnu vrednost reduce-a posto on vraca tuple.
        listOfCandidatesForNextToken = returnTuple[0]                         # Uvek ce se na nultom indeksu nalaziti niz koji mi je dalje potreban; ostali elementi tuple-a su nebitni.
        tupleTokens = pool.map(create_token_tuples, listOfCandidatesForNextToken)
        sortedTupleTokens = sorted(tupleTokens, key=lambda tup: tup[0])
        returnTuple = reduce(reduce_token_tuples, sortedTupleTokens, ([], 0, -1))
        reducedTupleTokens = returnTuple[0]
        sortedReducedTupleTokens = sorted(reducedTupleTokens, key=lambda tup: tup[1], reverse=True)

        mostCommonToken = sortedReducedTupleTokens[0]
        currentListOfTokens.append(mostCommonToken)

        returnTuple = reduce(insert_token, chosenTexts, ([], mostCommonToken, "", []))
        chosenTexts = returnTuple[0]
    print(currentListOfTokens, len(currentListOfTokens))

#zadatak 3, tacka 8



