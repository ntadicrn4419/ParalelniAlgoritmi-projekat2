import multiprocessing.pool
from functools import reduce
import wikipedia
wikipedia.set_lang("sr")

specialCharacters = ['=', '-', ',', '!', '?', '.', '$', '(', ')', '[', ']', ';', '{', '}', '@', '#', '%', '^', '&', '*', '_', '+', '-', '/', '\\', '\'', '"', '<', '>', '|']

#'''Dohvata naslove zahtevanog broja stranica koje se pojavaljuju kao
#  rezultati pretrage za zadatu kljucnu rec'''
def get_pages(query, results=50): #staviti posle results = 50
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

def reduce_text(tuple, currentChar):
    array, flag = tuple
    if flag :
        return (array, flag)
    if len(array) >= 10_000 and currentChar == "$":
        flag = True
    return (array + list(currentChar), flag)


def prepare(tuple):
    query, string1 = tuple
    res = map(lower_case, str(string1))
    string2 = reduce(remove_special_chars, list(res), [])
    string3 = reduce(add_terminator, string2, []) #ukoliko imamo u stringu vise povezanih space-eva, stavice za svaki space $, da li je to validno?
    string3.append("$")
    string4, boolean = reduce(reduce_text, string3, ([], False))
    return query, string4

def choose_texts(tuple, currentElement): #uzima po pet tekstova za svaku kljucnu rec
    newArray, text, index, counter = tuple
    key, currentChar = currentElement
    previousKey, value = text[index-1]
    if key != previousKey:
        counter = 0
    if counter < 5:
        return (newArray + list(currentChar), text, index+1, counter+1)
    else:
        return (newArray, text, index+1, counter+1)

def create_tokens(tuple, currentChar):
    array, chosenTexts, index = tuple
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

if __name__ == '__main__':
    keywords = ['Beograd', 'Prvi svetski rat', 'Protein', 'Mikroprocesor', 'Stefan Nemanja', 'Košarka']
    pool = multiprocessing.pool.ThreadPool(multiprocessing.cpu_count())
    titlesMatrix = pool.map(get_pages, keywords) #titlesMatrix = map(get_pages, keywords)-> za 2 sekunde sporije od map-a iz pool-a
    titlesList = reduce(append_list, titlesMatrix, [])
    processedText = pool.map(prepare, titlesList)
    chosenTexts, oldText, endIndex, cnt = reduce(choose_texts, processedText, ([], processedText, 0, 0))#chosenTexts je lista karaktera
    tokens, text, index = reduce(create_tokens, chosenTexts, ([], chosenTexts, 0))

    #Ideja za 3. zad, 3. tacka: izmapirati niz tokena tako da dobijemo niz taplova, gde je prvi clan u taplu token, a drugi broj pojavaljivanja tog tapla(na pocetku za svaki token bice 1)
    #sortirati niz taplova po tokenima tako da taplovi sa istim tokenima budu jedan do drugog u nizu
    #reducovati niz taplova tako da se ne pojavaljuje vise tokena, nego da za svaki token imamo tacan broj pojavljivanja.
    tupleTokens = pool.map(create_token_tuples, tokens)
    sortedTupleTokens = sorted(tupleTokens, key=lambda tup: tup[0])
    reducedTupleTokens, token, index = reduce(reduce_token_tuples, sortedTupleTokens, ([], 0, -1))
    sortedReducedTupleTokens = sorted(reducedTupleTokens, key=lambda tup: tup[1], reverse=True)
    print(sortedReducedTupleTokens)

# stao sam kod zadatka 3, 6. tacka




